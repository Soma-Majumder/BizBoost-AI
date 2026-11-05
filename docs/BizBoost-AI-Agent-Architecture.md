# BizBoost AI: Agent Architecture

One AI agent, supported by five deterministic SEO analyzers. Six-day MVP. Updated to match the PRD dated 11/3/2026.

## Core idea

Code decides what is true about the website, and the AI explains it. The scanner checks whether a meta description exists. The AI never makes that call. It only turns verified findings into plain-language explanations and prioritized recommendations.

## Flow

```
User enters URL (Streamlit)
  -> URL validator (valid, public, not localhost/private IP, safe redirects)
  -> Audit orchestrator (crawl and PageSpeed run in parallel; 2-minute target)
      |- Website crawler (robots.txt check, homepage, then sitemap, then internal
      |     links, max 10 pages, identified user-agent)
      |     -> Extracted page data (server HTML only: titles, headings, meta, links,
      |        text, NAP, social links)
      |           -> 5 deterministic analyzers (keyword, content, local, technical,
      |              credibility)
      |- Google PageSpeed API (homepage only, 30-second timeout; feeds Technical SEO)
      |- Backlink provider (optional; feeds Credibility)
  -> Evidence + scoring engine (unavailable checks dropped, weights rescaled to 100)
  -> AI reasoning agent (Claude API)
  -> Output validator
  -> Report generator
  -> Streamlit results dashboard
```

The diagram is in `bizboost-agent-architecture.png`.

## Components and responsibilities

| Component | Type | Input | Output |
|---|---|---|---|
| URL validator | Deterministic | Raw URL | Normalized URL or a clear error |
| Crawler | Deterministic | Valid URL | Page data for up to 10 pages, or a "site does not allow scanning" status. Pages it could not reach are listed as not scanned |
| 5 analyzers | Deterministic | Page data | A list of findings, each with a check ID, status, evidence and source |
| PageSpeed | External API | Homepage URL | Speed and mobile metrics, or unavailable after a 30-second timeout or rate limit |
| Backlink provider | External API (optional) | URL | Inbound link data, or unavailable |
| Scoring engine | Deterministic | Findings | Category scores and an overall score out of 100; unavailable checks are dropped and the remaining weights rescaled to add up to 100 |
| AI reasoning agent | LLM | Findings and scores as JSON | Explanation, why it matters and recommended action per finding (each naming its check), plus the top 3 priorities |
| Output validator | Deterministic | AI output | Pass or reject |
| Report generator | Deterministic | Everything above | Dashboard view |

## How the crawl works

- **Page selection:** The crawler starts with the homepage, then adds pages listed in the XML sitemap, then internal links found on the homepage, in that order, until it reaches 10 pages. Duplicate and off-site links are skipped.
- **PageSpeed scope:** PageSpeed Insights runs on the homepage only, at the same time as the crawl, so the full audit stays under the 2-minute target.
- **JavaScript-heavy sites:** The crawler reads each page's HTML as the server sends it, and BeautifulSoup cannot see content built by JavaScript. When a check cannot see the content it needs for this reason, it shows "Data unavailable", not a failure.
- **Blocked sites:** If robots.txt or a firewall blocks the crawler, the scan stops and tells the user in plain language that the site does not allow scanning. Pages that could not be reached are listed as not scanned, never scored as failures.

## The data contract

Every analyzer returns findings in the same shape, so the scoring engine and the AI never guess. Status is one of `pass`, `fail`, `warn` or `unavailable`. A missing backlink API key gives `unavailable`, never `0`.

```json
{
  "check_id": "technical.meta_description",
  "category": "technical_seo",
  "page": "https://example.com/",
  "status": "fail",
  "evidence": "Meta description tag is missing",
  "source": "crawler",
  "weight": 3
}
```

## Scoring

Each check returns pass, warn, fail or unavailable, with a weight. Points: pass 1, warn 0.5, fail 0. Unavailable checks are dropped.

- **Category score** = 100 × Σ(weight × points) ÷ Σ(weight), over the measured checks only.
- **Overall score** = weighted average of the category scores. A category with no measured checks is left out and the remaining weights are rescaled to add up to 100.

| Category | Weight |
|---|---|
| Technical SEO | 25 |
| Keyword Optimization | 25 |
| Content Quality | 20 |
| Local SEO | 20 |
| Credibility and Backlinks | 10 |

Every finding counts: a check that runs on each page contributes once per page. The PRD (A10) has a worked example.

## How the AI agent behaves

- **Input:** Only the scanner's evidence (findings JSON), the scores and a short business context (name, apparent business type). It gets no raw HTML to improvise from.
- **Task per finding:** Explain the issue for a non-expert, say why it matters and give one specific action.
- **Task overall:** Pick the top 3 improvements, ranked by weight and failed-check count.
- **Output:** Structured JSON, so the Streamlit report can render it reliably.
- **Single pass for the MVP:** No tool-calling loop. That keeps it easy to build, test and explain at the Pursuit presentation. Letting the agent request extra checks could be a v2 idea.

## Guardrails

1. **Evidence rule:** The AI is told to explain only what is in the evidence, and every recommendation must name the `check_id` it comes from. The output validator rejects anything that does not.
2. **Unavailable rule:** For `unavailable` items, the AI may only say what could not be checked and why. It cannot comment on results or score them.
3. **No invented data:** The prompt forbids new metrics, rankings, traffic numbers or competitor claims. If the output fails validation, retry once, then fall back to rule-based text (for example, "Missing meta description. Add a unique description summarizing your business").
4. **Honest scoring:** An unavailable check is dropped from the score and the remaining checks' weights are rescaled to add up to 100, so the score reflects only what was measured and no one is penalized for data the tool cannot reach.
5. **Crawler safety:** No private IPs, localhost or unsafe redirects. Respect robots.txt, cap the crawl at 10 pages, use reasonable crawl limits and identify our crawler.
6. **Human review:** AI output is reviewed on the 10 test sites, and the success target is 0 unsupported recommendations.
7. **Public data only:** No Google Analytics, Search Console or logins.

## Failure handling

| Situation | Behavior |
|---|---|
| Invalid or unsafe URL | Stop and show a specific message |
| PageSpeed times out (30 seconds) or hits a rate limit | Technical SEO continues with the deterministic checks, the speed items show "Data unavailable" and the rest of the audit finishes |
| Crawler blocked by robots.txt or a firewall | Stop the scan, tell the user the site does not allow scanning and list pages as not scanned |
| Content built by JavaScript | Affected checks show "Data unavailable", not a failure |
| No backlink provider | Backlink items show "Data unavailable", and the audit continues |
| Claude API fails | Show scores and findings with rule-based text, plus a note that AI explanations are unavailable |

## Open questions from the PRD

- Backlinks stay in as an optional feature and are the first thing cut if time is short. Still open: which backlink data provider, if any, can we use without a paid account?
- Resolved: category weights are Technical 25, Keyword 25, Content 20, Local 20, Credibility and Backlinks 10 (see Scoring). They are a first guess to tune after the 10 test sites.
- Resolved: the default model is Claude Sonnet 5.5 (`claude-sonnet-5-5`), chosen for cost and speed, set with `ANTHROPIC_MODEL`. Budget: $40 of API credits, roughly 10 cents per audit (estimate). Before the demo, compare it with Claude Opus 5.5 on a few test sites and switch only if Sonnet fails the citation rule.
- How should Local SEO be handled for businesses where local search is not relevant?

## Mapping to the project structure

`app.py` is the interface and orchestrator. `crawler/website_crawler.py` is the crawler. The `analyzers/` folder holds the five checks (`keyword.py`, `content.py`, `local_seo.py`, `technical.py`, `credibility.py`). `integrations/` holds PageSpeed and backlinks. `scoring/score_engine.py` is scoring and `agent/reasoning.py` is the AI agent. `tests/test_audit.py` covers it, and the URL validator lives in `app.py` or a small utils file.
