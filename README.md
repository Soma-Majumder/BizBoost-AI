# BizBoost AI

**A free SEO audit for small businesses. Enter a website address and get scores, evidence, and a short list of what to fix first, in plain English.**

Big companies like B&H pay a full-time Senior SEO Specialist to audit their websites. Small businesses can't afford that, so they guess, pay an agency, or do nothing. BizBoost AI gives them the same kind of audit in minutes, with no account, no SEO knowledge, and no paid tools.

---

## Who it's for

- **Small-business owners** (shops, restaurants, local services) who have a website, know little about SEO, and want more customers to find them online.
- **Freelance marketers and web designers** who want a quick, evidence-based audit to share with a client.

## What it does

1. **You enter a public website URL.** No sign-up and no private data.
2. **It scans up to 10 pages** of the site.
3. **It checks five SEO categories:**
   - Keyword optimization
   - Content quality
   - Local SEO
   - Technical SEO (plus homepage speed from Google PageSpeed Insights)
   - Credibility and backlinks
4. **It scores the site** with an overall score out of 100 and a score for each category.
5. **It shows the evidence** behind every finding: what was found and on which page.
6. **An AI assistant explains** each issue in plain language and recommends the **top 3 fixes** in priority order.
7. **It's honest about gaps.** Anything it can't check shows **"Data unavailable"** instead of a failing score.

---

## How it works

```
URL entry
  → URL validation and safety check
  → Audit orchestrator
  → Website crawler (up to 10 pages)          PageSpeed Insights (homepage, in parallel)
  → Five SEO analyzers                         Optional backlink data
  → Evidence and scoring engine
  → AI reasoning (explains findings, recommends fixes)
  → Recommendations and report
  → Streamlit results dashboard
```

**One AI agent, five rule-based analyzers.** The analyzers decide whether something exists, for example whether a page has a meta description. The AI only explains those findings and suggests an action. It never decides on its own that a problem exists.

---

## Rules the system follows

| Rule | What it means |
| --- | --- |
| Public data only | No Google Analytics, no Search Console, no user accounts. |
| Crawler safety | Never scans private IP addresses, localhost, or unsafe redirects. |
| Respect site rules | Checks `robots.txt`, uses reasonable crawl limits, and identifies its crawler. |
| Evidence first | Every finding links to a measurable check or a named data source. |
| No invented data | Missing backlink data stays "unavailable", never zero. |
| Honest scoring | Unavailable checks are dropped from the score, and the remaining weights are rescaled to add up to 100. |
| Small crawl | Up to 10 pages per audit. |
| Page selection | Homepage first, then pages in the XML sitemap, then internal links from the homepage, until 10 pages. Duplicates and off-site links are skipped. |
| Speed check scope | PageSpeed Insights runs on the homepage only, alongside the crawl, with a 30-second timeout. |
| JavaScript-heavy sites | The crawler reads the HTML the server sends. If a check can't see content that is built by JavaScript, it shows "Data unavailable", not a failure. |

---

## Tech stack

- **Python**
- **Streamlit**: web interface and results dashboard
- **BeautifulSoup**: page parsing for the crawler and analyzers
- **Google PageSpeed Insights API**: homepage speed and mobile performance
- **OpenRouter**: AI explanations and recommendations

---

## Getting started

### Requirements

- Python 3.10+
- A Google PageSpeed Insights API key
- An OpenRouter API key

### Install

```bash
git clone <your-repo-url>
cd BizBoost-AI
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

Copy `.env.example` to `.env` in the project root and fill it in:

```
PAGESPEED_API_KEY=your_pagespeed_key
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=your_chosen_model
```

### Run

```bash
streamlit run app.py
```

Open the local URL Streamlit prints, enter a website address, and click **Start Audit**.

### Test

```bash
pytest
```

### Project structure

| Path | Purpose |
| --- | --- |
| `app.py` | Streamlit interface and audit orchestrator |
| `crawler/` | Website crawler |
| `analyzers/` | The five SEO analyzers |
| `integrations/` | PageSpeed and optional backlinks |
| `scoring/` | Scoring engine |
| `agent/` | AI reasoning agent |
| `tests/` | Tests |
| `docs/` | PRD and agent architecture |

---

## Success targets (MVP)

| Goal | Target |
| --- | --- |
| Audits complete | At least 9 of 10 valid test sites |
| Fast results | Under 2 minutes from Start Audit to report |
| Evidence-backed findings | 100% of findings show their evidence or source |
| Clear next steps | 100% of reports include at least 3 prioritized fixes |
| Honest scoring | 0 "Data unavailable" items counted as zero |
| Plain language | 4 of 5 test users can name their top fix without help |
| All categories work | 5 of 5 categories return a score or "Data unavailable" by Day 6 |
| Trustworthy AI | 0 AI recommendations that cite something not in the evidence |

---

## Known risks and how we handle them

- **PageSpeed is slow or rate-limited:** we run it on the homepage only, with a 30-second timeout. If it fails, speed shows "Data unavailable" and the rest of the audit still finishes.
- **Sites that block crawling:** we respect the block, stop the scan, and explain in plain language. Pages we can't reach are listed as not scanned, never scored as failures.
- **AI explains something that isn't in the evidence:** the AI only receives the scanner's evidence, is told to explain only what's in it, and every recommendation must name the check it comes from. We review the output on all 10 test sites.

---

## Out of scope for the MVP

- Google Analytics, Search Console, and user accounts
- Crawling more than 10 pages per audit
- Ongoing monitoring, alerts, rank tracking, and automated link building
- Required inbound backlink analysis (optional only, since it needs a paid provider)

---

## Six-day build plan

| Day | Work | Deliverable |
| --- | --- | --- |
| 1 | Streamlit interface, URL validation, crawler | Website scanner |
| 2 | Keyword and content analyzers | First two SEO checks |
| 3 | Local, technical, and credibility analyzers | All five SEO checks |
| 4 | PageSpeed, optional backlinks, scoring | Evidence-based results |
| 5 | OpenRouter AI reasoning, recommendations, dashboard | AI-powered audit |
| 6 | Testing, bug fixes, presentation | Working demo |

---

## Open questions

- Which backlink data provider, if any, can we use without a paid account?
- How should each category be weighted in the overall score?
- Which OpenRouter model gives the best balance of cost, speed, and explanation quality?
- How should Local SEO be handled for businesses where local search doesn't matter?

---

## Background

This project started from the **B&H Senior SEO Specialist** job description. That role covers recurring technical and on-page audits, monitoring crawlability, speed, sitemaps, canonical tags, metadata and redirects, keyword research, and data-driven prioritization. BizBoost AI turns those recurring tasks into an automated audit a small business can run on its own.

## Team

- Soma Majumder
- Erick Marcatoma
