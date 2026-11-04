"""The findings data contract shared by analyzers, scoring and the AI agent.

Every analyzer returns a list of ``Finding`` objects. The scoring engine and the AI
only ever see this shape, so neither has to guess.

Statuses:
    pass         the check was measured and is fine
    warn         measured, but only partly fine
    fail         measured and a problem
    unavailable  could not be measured (blocked page, JavaScript content, no API key)

``unavailable`` is never a failure and never zero. Scoring drops it and rescales the
remaining weights.

Example JSON (``Finding.to_dict()``):

    {
      "check_id": "technical.meta_description",
      "category": "technical_seo",
      "page": "https://example.com/",
      "status": "fail",
      "evidence": "Meta description tag is missing",
      "source": "crawler",
      "weight": 3
    }
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class Status(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    UNAVAILABLE = "unavailable"


class Category(str, Enum):
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    CONTENT_QUALITY = "content_quality"
    LOCAL_SEO = "local_seo"
    TECHNICAL_SEO = "technical_seo"
    CREDIBILITY_BACKLINKS = "credibility_backlinks"


class Source(str, Enum):
    CRAWLER = "crawler"
    PAGESPEED = "pagespeed"
    BACKLINK_PROVIDER = "backlink_provider"


MEASURED_STATUSES = (Status.PASS, Status.WARN, Status.FAIL)


class InvalidFindingError(ValueError):
    """A finding does not follow the contract. This is a programming error."""


@dataclass(frozen=True)
class Finding:
    check_id: str  # stable ID such as "technical.meta_description"
    category: Category
    status: Status
    evidence: str  # what was found, in plain words. Never empty.
    source: Source
    weight: int = 1  # how much this check counts in its category, 1 or more
    page: str | None = None  # page URL, or None for a site-wide check

    def __post_init__(self) -> None:
        # Accept plain strings from JSON or analyzers and convert them to enums.
        for name, enum in (("category", Category), ("status", Status), ("source", Source)):
            value = getattr(self, name)
            if not isinstance(value, enum):
                try:
                    object.__setattr__(self, name, enum(value))
                except ValueError:
                    allowed = ", ".join(member.value for member in enum)
                    raise InvalidFindingError(
                        f"{name} must be one of: {allowed} (got {value!r})"
                    ) from None
        if not isinstance(self.check_id, str) or not self.check_id.strip():
            raise InvalidFindingError("check_id is required")
        if not isinstance(self.evidence, str) or not self.evidence.strip():
            raise InvalidFindingError(f"{self.check_id}: evidence is required")
        if isinstance(self.weight, bool) or not isinstance(self.weight, int) or self.weight < 1:
            raise InvalidFindingError(f"{self.check_id}: weight must be a whole number, 1 or more")
        if self.page is not None and not isinstance(self.page, str):
            raise InvalidFindingError(f"{self.check_id}: page must be a URL string or None")

    @property
    def is_measured(self) -> bool:
        """True when the check counts toward scores. ``unavailable`` does not."""
        return self.status in MEASURED_STATUSES

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for name in ("category", "status", "source"):
            data[name] = data[name].value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Finding:
        known = {"check_id", "category", "status", "evidence", "source", "weight", "page"}
        extra = set(data) - known
        if extra:
            raise InvalidFindingError(f"Unknown finding fields: {', '.join(sorted(extra))}")
        try:
            return cls(**data)
        except TypeError as error:
            raise InvalidFindingError(str(error)) from None


def finding(
    check_id: str,
    category: Category | str,
    status: Status | str,
    evidence: str,
    source: Source | str = Source.CRAWLER,
    weight: int = 1,
    page: str | None = None,
) -> Finding:
    """Build a finding. Positional order matches how analyzers usually read."""
    return Finding(
        check_id=check_id,
        category=category,
        status=status,
        evidence=evidence,
        source=source,
        weight=weight,
        page=page,
    )


def unavailable(
    check_id: str,
    category: Category | str,
    reason: str,
    source: Source | str = Source.CRAWLER,
    weight: int = 1,
    page: str | None = None,
) -> Finding:
    """Shortcut for a check that could not be measured. ``reason`` says why."""
    return finding(check_id, category, Status.UNAVAILABLE, reason, source, weight, page)


def findings_to_json_data(findings: list[Finding]) -> list[dict[str, Any]]:
    """The list the AI agent receives."""
    return [item.to_dict() for item in findings]
