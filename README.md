# BizBoost AI

**A free SEO audit for any business. Enter a website address and get scores, evidence, and a short list of what to fix first, in plain English.**

---

## The problem we noticed

A lot of vegan restaurants in New York are not SEO optimized. Their websites are missing the basics Google reads, so when someone nearby searches for a place to eat, the larger NYC community cannot find them. The owners usually don't know, and most can't afford a specialist or an agency to tell them.

## What we decided to do

We wanted to put more eyeballs on these restaurants, so we built **BizBoost AI**: a free audit that checks a website the way an SEO specialist would and explains the results in plain English. It needs no account, no SEO knowledge, and no paid tools.

We started with vegan restaurants. The checks work for any small business with a website, so **the app is now open to ALL businesses**.

We found the problem first, then matched it to a real job: the **B&H Senior SEO Specialist**. That role covers recurring technical and on-page audits, monitoring crawlability, speed, sitemaps, canonical tags, metadata and redirects, keyword research, and data-driven prioritization. Big companies pay a full-time person for this. BizBoost AI turns those recurring tasks into an automated audit a small business can run on its own.

---

## Problems we hit, and what we decided

| Problem | What we decided |
| --- | --- |
| An AI can say things that aren't true. | The rules decide what is wrong, and the AI only explains it. The AI never decides on its own that a problem exists. |
| An AI explanation might mention something the scan never found. | Every AI explanation is checked against the real list of problems. If it fails, Claude gets one more try. |
| The AI service might be down, or the retry might still fail. | The report falls back to ready-made plain-English text and says the text wasn't written by the AI. |
| Some pages are built by JavaScript, so a plain scan can't read them. | Those checks show "Data unavailable" and are left out of the score. They are never counted as a failure. |
| Owners don't understand SEO terms. | Every finding is a problem, why it matters, and one solution, written without jargon. |
| Owners who've been burned by agencies don't trust a score. | Every finding shows its evidence: what was found, and on which page. |
| Speed tests and backlink data can be slow or incomplete. | PageSpeed runs on the homepage only with a 30-second timeout. Backlinks are optional and never fail a site. |
| A deep audit of a whole site would be slow. | We scan up to 10 pages, homepage first. |

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

---

## What it automates

Normally, someone has to click through your website page by page, look for problems, work out what matters, and write it up. BizBoost AI does all of that automatically:

1. **It visits your website.** It reads up to 10 pages the way Google would, and it respects the site's rules about what robots may read.
2. **It checks five areas:**
   - Keywords: do your pages use the words customers actually search for?
   - Content quality: is your writing useful and complete?
   - Local presence: can Google easily find your address, phone number and hours? This matters for "near me" searches.
   - Technical health: are there broken pieces? Is the site fast?
   - Credibility: do other websites link to you and vouch for you?
3. **It gives you scores.** One overall score out of 100 and a score for each area.
4. **It shows proof.** Every problem says what was found and on which page, so it doesn't read like a sales pitch.
5. **It explains the problems in plain English.** An AI assistant turns the technical findings into simple language.
6. **It picks your top 3 fixes,** in priority order, so you know where to spend your first hour.
7. **It says so when it can't check something.** It shows "Data unavailable" instead of guessing or giving a false failing grade.

### How it can help a business

- **Saves money.** An expert-style audit without an agency or a full-time specialist.
- **Saves time.** Results in minutes. A manual audit takes hours.
- **Brings in more customers.** If Google can't read your site well, nearby customers find your competitor instead.
- **Tells you what to do first.** The top 3 list puts the fixes that matter most first.
- **Builds trust.** You can see the evidence behind every finding.
- **Makes handing off easy.** Send the report to your web designer and they'll know exactly what to fix.
- **Helps freelancers.** A quick, evidence-based audit to share with a client.

One limit: it only looks at public information and up to 10 pages. It's a good starting check-up, not a full replacement for a long-term SEO strategy.

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

**One AI agent, five rule-based analyzers.** The analyzers decide whether something exists, for example whether a page has a meta description. The AI only explains those findings and suggests an action.

### How the AI is used

BizBoost AI checks your website with ordinary rules first, like a checklist. The app then sends that list of problems to Claude once. Claude explains each problem and picks your top 3 fixes. This is where the Claude API helps most: it turns technical findings into plain language, so business owners can understand them without knowing any jargon.

**The loop.** It works like a teacher marking homework, with one chance to redo it:

1. Claude writes the explanations.
2. The app checks them against the real list of problems.
3. If they're good, they go in your report.
4. If not, Claude gets one more try.
5. If it still fails, or the AI service is down, ready-made plain-English text is used instead. The report notes that this text wasn't written by the AI.

**Why it matters:** the report only contains real problems, every explanation is written for a business owner, and the app still works if the AI is unavailable.

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

## Did it work? Testing on 10 real sites

We ran the audit on 10 public restaurant websites and reviewed the AI's explanations by hand against the scanner's evidence. The full review is in [`review/ai-review-10-sites.md`](review/ai-review-10-sites.md) (and a PDF).

| Result | Target | What we found |
| --- | --- | --- |
| Audits complete | At least 9 of 10 | 10 of 10 |
| Fast results | Under 2 minutes | Every test run finished under 2 minutes (longest about 70 seconds) |
| Evidence-backed findings | 100% | 100% |
| Trustworthy AI | 0 claims not in the evidence | 0 found in our review |

Overall scores ranged from 69 to 91 (average about 82).

| Site | Score | Site | Score |
| --- | --- | --- | --- |
| Bodhi | 81 | Jajaja | 84 |
| Sen Saigon | 75 | Coletta | 89 |
| Ahimsa | 81 | Natural Blend | 88 |
| Next Level Vegan | 87 | Spicy Moon | 69 |
| Slutty Vegan | 73 | Kailash Parbat | 91 |

Testing also found real bugs, which we fixed: AI wording that went beyond the evidence and a wrong readability result on menu-style pages.

---

## Meet the team

<table>
  <tr>
    <td align="center" width="50%">
      <img src="docs/team/soma.png" alt="Photo of Soma Majumder" width="220"><br>
      <b>Soma Majumder</b><br>
      <a href="https://github.com/Soma-Majumder">GitHub</a> · <a href="https://www.linkedin.com/in/somamajumder/">LinkedIn</a>
    </td>
    <td align="center" width="50%">
      <!-- TODO: add Erick's photo as docs/team/erick.png, then uncomment:
      <img src="docs/team/erick.png" alt="Photo of Erick Marcatoma" width="220"><br> -->
      <b>Erick Marcatoma</b><br>
      <a href="https://github.com/erickmarcatoma">GitHub</a> · <a href="https://www.linkedin.com/in/erick-marcatoma-611326419/">LinkedIn</a>
    </td>
  </tr>
</table>

**What Soma did**
- Wrote the product requirements and the agent architecture.
- Built the website crawler and HTML parser, and the five SEO analyzers (keywords, content, local, technical, credibility).
- Added the Google PageSpeed and Crawly backlink integrations, and the scoring engine.
- Built the Claude AI reasoning agent, then made its output plain-language, with a problem, why it matters, and a solution for each finding.
- Ran and reviewed the 10-site test, fixed the bugs it found, and prepared the demo and presentation.

**What Erick did**
- Wrote the project plan, the assumptions and the early README.
- Built the audit orchestrator that runs a site end to end.
- Built the output validator and the rule-based fallback text.
- Built the report generator and the results dashboard, and the end-to-end audit tests.
- Designed the new front end: the landing page, the progress screen and the report screen.

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
- An Anthropic (Claude) API key. Without one, the app still works and shows standard explanations instead of AI-written ones.
- Recommended: a Google PageSpeed Insights API key. Without one, speed checks show "Data unavailable".
- Optional: a Crawly API key for backlinks (without it, backlinks show "Data unavailable")

### Install

```bash
git clone https://github.com/Soma-Majumder/BizBoost-AI.git
cd BizBoost-AI
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

Open the local URL Streamlit prints (usually http://localhost:8501), enter a website address, and click **Start Audit**.

### Run the tests

```bash
pip install pytest
python -m pytest -q
```

### Troubleshooting

**"AI explanations are unavailable right now."** Check the Streamlit terminal output. If it says the API key was rejected, look for an old `ANTHROPIC_API_KEY` exported in your shell (for example in `~/.zshrc`). A key already set in the environment takes priority over the one in `.env`. Remove or update the old one, open a new terminal, and restart the app.

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

The full day-by-day plan is in `BizBoost AI — Project plan.md`. More detail is in the [PRD](docs/BizBoost-AI-PRD.md) and the [agent architecture](docs/BizBoost-AI-Agent-Architecture.md).

---

## Open questions

- Resolved: backlinks stay in as an optional feature and are the first thing cut if time runs short. Provider: the free Crawly API (getcrawly.com), tested on 5 Nov 2026 on veganbodhi.com, which returned 18 referring domains. Limit: 100 requests a day, one call per audit. Crawly uses an open web index that may be incomplete, so no data, a missing key or an error shows "Data unavailable", never zero and never a failure.
- Resolved: category weights are Technical 25, Keyword 25, Content 20, Local 20, Credibility and Backlinks 10. A first guess to tune after the 10 test sites (see "How the score works").
- Resolved: the default model is Claude Sonnet 5.5 (`claude-sonnet-5-5`), chosen for cost and speed, set with `ANTHROPIC_MODEL`. Before the demo, compare it with Claude Opus 5.5 on a few test sites and switch only if Sonnet fails the citation rule.
- How should Local SEO be handled for businesses where local search doesn't matter?
