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

> The project structure and file names below are the planned setup. Update them to match the repo as it's built.

### Requirements

- Python 3.10+
- A Google PageSpeed Insights API key
- An Anthropic (Claude) API key

### Install

```bash
git clone <your-repo-url>
cd bizboost-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

Create a `.env` file in the project root:

```
PAGESPEED_API_KEY=your_pagespeed_key
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=claude-sonnet-5-5
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
| 5 | Claude AI reasoning, recommendations, dashboard | AI-powered audit |
| 6 | Testing, bug fixes, presentation | Working demo |

---

## Open questions

- Resolved: backlinks stay in as an optional feature and are the first thing cut if time runs short. Provider: the free Crawly API (getcrawly.com), tested on 5 Nov 2026 on veganbodhi.com, which returned 18 referring domains. Limit: 100 requests a day, one call per audit. Crawly uses an open web index that may be incomplete, so no data, a missing key or an error shows “Data unavailable”, never zero and never a failure. Collaborator’s free Backlink Checker (a web form, 5 checks a day, no backlink API found) is only a manual reference.
- Resolved: category weights are Technical 25, Keyword 25, Content 20, Local 20, Credibility and Backlinks 10. A first guess to tune after the 10 test sites.
- Resolved: the default model is Claude Sonnet 5.5 (`claude-sonnet-5-5`), chosen for cost and speed, set with `ANTHROPIC_MODEL`. Budget: $40 of API credits, roughly 10 cents per audit (estimate). Before the demo, compare it with Claude Opus 5.5 on a few test sites and switch only if Sonnet fails the citation rule.
- How should Local SEO be handled for businesses where local search doesn't matter?

---

## Background

This project started from the **B&H Senior SEO Specialist** job description. That role covers recurring technical and on-page audits, monitoring crawlability, speed, sitemaps, canonical tags, metadata and redirects, keyword research, and data-driven prioritization. BizBoost AI turns those recurring tasks into an automated audit a small business can run on its own.

## Team

- Soma Majumder
- Erick Marcatoma
