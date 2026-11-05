"""Report generator: turns the audit and its explanations into one report to display.

``build_report(audit, explanation)`` is deterministic and has no Streamlit code, so the
dashboard in ``app.py`` only decides how things look. ``to_text(report)`` is the plain-text
version people can download and share. Evidence can quote text from the scanned website,
so plain text also means nothing in the file can act as a link or image.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from agent.output_validator import Explanation
from findings import Finding, Status
from orchestrator import AuditResult

DATA_UNAVAILABLE = "Data unavailable"

CATEGORY_LABELS = {
    "technical_seo": "Technical SEO",
    "keyword_optimization": "Keyword Optimization",
    "content_quality": "Content Quality",
    "local_seo": "Local SEO",
    "credibility_backlinks": "Credibility and Backlinks",
}

STATUS_LABELS = {
    Status.FAIL: "Problem",
    Status.WARN: "Needs attention",
    Status.UNAVAILABLE: DATA_UNAVAILABLE,
    Status.PASS: "Passed",
}

# The worst status on any page decides how a check is shown, and problems are listed first.
_STATUS_ORDER = {Status.FAIL: 0, Status.WARN: 1, Status.UNAVAILABLE: 2, Status.PASS: 3}

# Plain names where the last part of the check ID would be jargon.
_CHECK_NAMES = {
    "h1": "Main heading",
    "title_terms_in_content": "Title words used in the page text",
    "image_alt": "Image descriptions",
    "https": "Secure connection (HTTPS)",
    "noindex": "Listed in search results",
    "canonical": "Preferred page address",
    "viewport": "Works on phones",
    "lang": "Page language",
    "sitemap": "XML sitemap",
    "robots_txt": "Robots.txt file",
    "speed_score": "Mobile speed score",
    "lcp": "Main content load time",
    "cls": "Layout stability",
    "tbt": "Page responsiveness",
    "schema_markup": "Business details for search engines",
    "analyzer_error": "These checks",
    "not_applicable": "Local checks",
}


@dataclass(frozen=True)
class ReportCheck:
    check_id: str
    name: str
    status: Status
    evidence: tuple[str, ...]  # what was found and where, one line per page
    explanation: str = ""  # AI text. Rule-based reports show the evidence on its own.
    why_it_matters: str = ""
    action: str = ""

    @property
    def status_label(self) -> str:
        return STATUS_LABELS[self.status]


@dataclass(frozen=True)
class ReportCategory:
    key: str
    label: str
    score: float | None
    checks: tuple[ReportCheck, ...]  # problems first

    @property
    def to_fix(self) -> tuple[ReportCheck, ...]:
        return tuple(c for c in self.checks if c.status in (Status.FAIL, Status.WARN))

    @property
    def unavailable(self) -> tuple[ReportCheck, ...]:
        return tuple(c for c in self.checks if c.status is Status.UNAVAILABLE)

    @property
    def passed(self) -> tuple[ReportCheck, ...]:
        return tuple(c for c in self.checks if c.status is Status.PASS)


@dataclass(frozen=True)
class TopFix:
    check_id: str
    name: str
    title: str
    reason: str
    action: str


@dataclass(frozen=True)
class NotScannedPage:
    url: str
    reason: str


@dataclass(frozen=True)
class Report:
    url: str
    completed: bool
    message: str | None  # why the audit stopped, when it did not complete
    overall: float | None
    categories: tuple[ReportCategory, ...]
    top_fixes: tuple[TopFix, ...]
    pages_scanned: tuple[str, ...]
    pages_not_scanned: tuple[NotScannedPage, ...]
    ai_generated: bool
    note: str | None  # shown when explanations are rule-based
    seconds: float | None = None


def score_text(score: float | None) -> str:
    return DATA_UNAVAILABLE if score is None else f"{round(score)} / 100"


def build_report(
    audit: AuditResult, explanation: Explanation | None = None, seconds: float | None = None
) -> Report:
    """Combine the audit and explanations. ``explanation`` is None when the audit stopped."""
    output = explanation.output if explanation else {}
    ai_generated = bool(explanation and explanation.ai_generated)
    entries = {entry["check_id"]: entry for entry in output.get("findings", [])}

    categories: list[ReportCategory] = []
    if audit.scores:
        for key, category in audit.scores.categories.items():
            in_category = [item for item in audit.findings if item.category == category.category]
            categories.append(
                ReportCategory(
                    key=key,
                    label=CATEGORY_LABELS.get(key, key),
                    score=category.score,
                    checks=_build_checks(in_category, entries, ai_generated),
                )
            )

    return Report(
        url=audit.url,
        completed=audit.completed,
        message=audit.site.message,
        overall=audit.scores.overall if audit.scores else None,
        categories=tuple(categories),
        top_fixes=tuple(_top_fix(item, entries) for item in output.get("top_priorities", [])),
        pages_scanned=audit.site.scanned_urls,
        pages_not_scanned=tuple(NotScannedPage(p.url, p.reason) for p in audit.site.not_scanned),
        ai_generated=ai_generated,
        note=explanation.note if explanation else None,
        seconds=seconds,
    )


def _build_checks(
    findings: list[Finding], entries: dict[str, dict[str, Any]], ai_generated: bool
) -> tuple[ReportCheck, ...]:
    groups: dict[str, list[Finding]] = defaultdict(list)
    for item in findings:
        groups[item.check_id].append(item)

    def rank(group: list[Finding]) -> tuple[int, int]:
        return (min(_STATUS_ORDER[item.status] for item in group), -max(item.weight for item in group))

    checks = []
    for check_id, group in sorted(groups.items(), key=lambda pair: rank(pair[1])):
        entry = entries.get(check_id, {})
        checks.append(
            ReportCheck(
                check_id=check_id,
                name=check_name(check_id),
                status=min((item.status for item in group), key=_STATUS_ORDER.__getitem__),
                evidence=_evidence_lines(group),
                # Rule-based explanations only repeat the evidence, which is always shown.
                explanation=entry.get("explanation", "") if ai_generated else "",
                why_it_matters=entry.get("why_it_matters", ""),
                action=entry.get("action", ""),
            )
        )
    return tuple(checks)


def _evidence_lines(group: list[Finding]) -> tuple[str, ...]:
    lines: list[str] = []
    for item in group:
        needs_page = item.page and item.page not in item.evidence
        line = f"{item.page}: {item.evidence}" if needs_page else item.evidence
        if line not in lines:
            lines.append(line)
    return tuple(lines)


def _top_fix(priority: dict[str, Any], entries: dict[str, dict[str, Any]]) -> TopFix:
    check_id = priority["check_id"]
    return TopFix(
        check_id=check_id,
        name=check_name(check_id),
        title=priority.get("title", ""),
        reason=priority.get("reason", ""),
        action=entries.get(check_id, {}).get("action", ""),
    )


def check_name(check_id: str) -> str:
    """``keyword.meta_description`` becomes ``Meta description``."""
    last_part = check_id.split(".", 1)[-1]
    return _CHECK_NAMES.get(last_part) or last_part.replace("_", " ").capitalize()


def to_text(report: Report) -> str:
    """The whole report as plain text, for downloading and sharing."""
    lines = ["BizBoost AI SEO report", f"Website: {report.url}", ""]
    if not report.completed:
        lines += [report.message or "The audit could not be completed.", ""]
    else:
        lines += [f"Overall score: {score_text(report.overall)}"]
        lines += [f"{c.label}: {score_text(c.score)}" for c in report.categories]
        lines.append("")
        if report.note:
            lines += [report.note, ""]
        lines += _top_fix_lines(report)
        for category in report.categories:
            lines += _category_lines(category)
    lines += _page_lines(report)
    return "\n".join(lines).rstrip() + "\n"


def _top_fix_lines(report: Report) -> list[str]:
    if not report.top_fixes:
        return []
    lines = ["TOP FIXES"]
    for number, fix in enumerate(report.top_fixes, start=1):
        lines.append(f"{number}. {fix.title}")
        lines.append(f"   Why: {fix.reason}")
        if fix.action:
            lines.append(f"   What to do: {fix.action}")
        lines.append(f"   Check: {fix.check_id}")
    lines.append("")
    return lines


def _category_lines(category: ReportCategory) -> list[str]:
    lines = [f"{category.label.upper()}: {score_text(category.score)}"]
    for check in category.checks:
        lines.append(f"[{check.status_label}] {check.name} ({check.check_id})")
        if check.explanation:
            lines.append(f"   What we found: {check.explanation}")
        if check.why_it_matters:
            lines.append(f"   Why it matters: {check.why_it_matters}")
        if check.action:
            lines.append(f"   What to do: {check.action}")
        lines += [f"   Evidence: {line}" for line in check.evidence]
    lines.append("")
    return lines


def _page_lines(report: Report) -> list[str]:
    lines = [f"PAGES SCANNED: {len(report.pages_scanned)}"]
    lines += [f"- {url}" for url in report.pages_scanned]
    if report.pages_not_scanned:
        lines += ["", f"PAGES NOT SCANNED: {len(report.pages_not_scanned)}"]
        lines += [f"- {page.url}: {page.reason}" for page in report.pages_not_scanned]
    return lines
