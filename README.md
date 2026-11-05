# BizBoost AI

**A free SEO audit for small businesses. Enter a website address and get scores, evidence, and a short list of what to fix first, in plain English.**

Big companies like B&H pay a full-time Senior SEO Specialist to audit their websites. Small businesses can't afford that, so they guess, pay an agency, or do nothing. BizBoost AI gives them the same kind of audit in minutes, with no account, no SEO knowledge, and no paid tools.

---

## Who it's for

- **Small-business owners** (shops, restaurants, local services) who have a website, know little about SEO, and want more customers to find them online.
- **Freelance marketers and web designers** who want a quick, evidence-based audit to share with a client.

## User stories

1. **The new café owner:** As a café owner who just launched a website, I want to enter my URL and see an overall SEO score, so that I know whether people can even find my site on Google.
2. **The busy plumber:** As a plumber with no time to learn SEO, I want to see just the top 3 things to fix first, so that I can spend my one free hour where it matters most.
3. **The skeptical boutique owner:** As a boutique owner who's been burned by agencies, I want to see the evidence behind every finding, like which page has the problem, so that I can trust the results are real and not a sales pitch.
4. **The restaurant owner losing nearby customers:** As a restaurant owner, I want to know whether my address, phone number and hours are easy for Google to find, so that people searching nearby can find me instead of my competitor.
5. **The owner who hands it off:** As a salon owner who pays a web designer, I want a clear report I can download and send to her, so that she knows exactly what to fix without me having to explain SEO.

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

## How the score works

- Every check returns **pass** (1 point), **warn** (half a point), **fail** (0), or **unavailable** (dropped, never counted as 0).
- **Category score (0–100):** weight × points for the measured checks, divided by the total weight of those checks, times 100.
- **Overall score (0–100):** the weighted average of the category scores. A category with no measured checks is left out and the other weights are rescaled to 100.

| Category | Weight |
| --- | --- |
| Technical SEO | 25 |
| Keyword Optimization | 25 |
| Content Quality | 20 |
| Local SEO | 20 |
| Credibility and Backlinks | 10 |

The weights are a first guess, to be tuned after the 10 test sites. Backlinks never fail a site, because the data source is incomplete.

---

## What data is stored

Nothing is stored after the audit. The website address, scanned pages, findings and report exist in memory only while the audit runs and the results are on screen. There are no accounts, no database and no saved reports.

Two outside services receive data to do their job: Google PageSpeed receives the homepage address, and the Claude API receives the findings and scores as text (the evidence, not the raw page HTML).

---

## Assumptions

| Assumption | Basis | Risk | If wrong |
| --- | --- | --- | --- |
| The homepage gets the most traffic and matters most for SEO, so we test it first (crawl order and PageSpeed check). | Common for small-business sites; not verified with real analytics. | Medium: some businesses get most visits on Menu, Shop, or Location pages via Google. | Let users choose which page to check first, or prioritize pages using their analytics data. |
| Impact and Effort ratings (used to pick the top 3 fixes) reflect what helps small-business rankings and what owners can fix themselves. | General SEO best practice; team judgment, not measured. | High: it decides the top 3 fixes, the core of the product. | Test with real owners (did they fix it, did it help?) and adjust the ratings. |

---

## Tech stack

- **Python**
- **Streamlit**: web interface and results dashboard
- **BeautifulSoup**: page parsing for the crawler and analyzers
- **Crawly API** (optional): inbound backlinks, free key with 100 requests a day
- **Google PageSpeed Insights API**: homepage speed and mobile performance
- **Claude API (Anthropic)**: AI explanations and recommendations

---

## Getting started

### Requirements

- Python 3.10+
- A Google PageSpeed Insights API key
- An Anthropic (Claude) API key
- Optional: a Crawly API key for backlinks (without it, backlinks show "Data unavailable")

### Install

```bash
git clone <your-repo-url>
cd bizboost-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

Copy `.env.example` to `.env` in the project root and fill it in. Never commit `.env`.

```
PAGESPEED_API_KEY=your_pagespeed_key
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=claude-sonnet-5-5
BACKLINK_API_KEY=your_crawly_key   # optional
```

### Run

```bash
streamlit run app.py
```

Open the local URL Streamlit prints, enter a website address, and click **Start Audit**.

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
| All categories work | 5 of 5 categories return a score or "Data unavailable" by Nov 11, 2026 |
| Trustworthy AI | 0 AI recommendations that cite something not in the evidence |

---

## Known risks and how we handle them

- **PageSpeed is slow or rate-limited:** we run it on the homepage only, with a 30-second timeout. If it fails, speed shows "Data unavailable" and the rest of the audit still finishes.
- **Sites that block crawling:** we respect the block, stop the scan, and explain in plain language. Pages we can't reach are listed as not scanned, never scored as failures.
- **AI explains something that isn't in the evidence:** the AI only receives the scanner's evidence, is told to explain only what's in it, and every recommendation must name the check it comes from. We review the output on all 10 test sites.
- **Claude API rate limit is unknown:** the key comes from the school and no limit has been shared. The SDK retries rate-limit errors automatically, and if the AI is still unavailable the report falls back to rule-based text.

### If time runs short

**Never cut:** URL validation, the crawler, the Technical, Keyword and Content analyzers, the scoring engine, the report with evidence and a top 3 fixes list, and AI explanations with the rule-based fallback text.

**Ship a simpler version:** Local SEO keeps only the phone number, address and map checks.

**Cut first, in this order:**
1. Inbound backlinks (the checks stay and show "Data unavailable")
2. P2 items: the example report and copy or download of the report
3. PageSpeed results (speed shows "Data unavailable", the rest still works)
4. The extra Local SEO checks

---

## Out of scope for the MVP

- Google Analytics, Search Console, and user accounts
- Crawling more than 10 pages per audit
- Ongoing monitoring, alerts, rank tracking, and automated link building
- Required inbound backlink analysis (optional only: the free Crawly provider has a 100-requests-a-day limit and an incomplete index)

---

## Build plan (Nov 4–12, 2026)

| Dates | Work | Deliverable |
| --- | --- | --- |
| Nov 4–5 | Streamlit interface, URL validation, crawler | Website scanner |
| Nov 6–7 | Five SEO analyzers, PageSpeed, scoring engine | Evidence-based scores |
| Nov 8 | Audit orchestrator: one site runs end to end | URL to scores |
| Nov 9–10 | Claude AI explanations, top 3 fixes, results dashboard | AI-powered audit |
| Nov 11 | Test on 10 sites, fix bugs, feature freeze | Demo-ready build |
| Nov 12 | Demo | Working demo |

Status on Nov 5: the URL validator, crawler and all five analyzers are built and tested. The full day-by-day plan is in `BizBoost AI — Project plan.md`.

---

## Open questions

- Resolved: backlinks stay in as an optional feature and are the first thing cut if time runs short. Provider: the free Crawly API (getcrawly.com), tested on 5 Nov 2026 on veganbodhi.com, which returned 18 referring domains. Limit: 100 requests a day, one call per audit. Crawly uses an open web index that may be incomplete, so no data, a missing key or an error shows “Data unavailable”, never zero and never a failure. Collaborator’s free Backlink Checker (a web form, 5 checks a day, no backlink API found) is only a manual reference.
- Resolved: category weights are Technical 25, Keyword 25, Content 20, Local 20, Credibility and Backlinks 10. A first guess to tune after the 10 test sites (see "How the score works").
- Resolved: the default model is Claude Sonnet 5.5 (`claude-sonnet-5-5`), chosen for cost and speed, set with `ANTHROPIC_MODEL`. Budget: $40 of API credits, roughly 10 cents per audit (estimate). Before the demo, compare it with Claude Opus 5.5 on a few test sites and switch only if Sonnet fails the citation rule.
- How should Local SEO be handled for businesses where local search doesn't matter?

---

## Background

This project started from the **B&H Senior SEO Specialist** job description. That role covers recurring technical and on-page audits, monitoring crawlability, speed, sitemaps, canonical tags, metadata and redirects, keyword research, and data-driven prioritization. BizBoost AI turns those recurring tasks into an automated audit a small business can run on its own.

## Team

- Soma Majumder
- Erick Marcatoma
