**BizBoost AI**

**Product Requirements Document: Net New Build**

**Build name:** BizBoost AI

**Owner:** Soma Majumder and Erick Marcatoma

**Date:** 11/3/2026

**1\. PROBLEM**

Small-business owners experience difficulty finding and fixing the SEO problems on their websites because professional SEO work (technical and on-page audits, keyword research, content refreshes, and ongoing monitoring) takes specialized skills and expensive tools, resulting in websites that are hard to find in search, missed customers, and no clear idea of what to fix first. A company like B\&H hires a full-time Senior SEO Specialist to audit its site, watch for broken pages, missing metadata and slow speeds, and prioritize fixes using data. A small business cannot afford that role, so it guesses, pays for an agency, or does nothing.

**Supporting Context**

* **Scale:** The U.S. Small Business Administration’s Office of Advocacy reports that the number of small businesses in the U.S. exceeds 36 million. Every one of them with a website competes to be found in search.  
* **Pain point from the job description:** B\&H’s Senior SEO Specialist role bundles recurring technical and on-page audits; monitoring of crawlability, site speed, XML sitemaps, canonical tags, metadata and redirects; keyword research; and ranking reports. That is a full-time job of specialized work.  
* **Cost and complexity:** Paid SEO suites are built for marketing professionals, and 2026 reviews cite entry plans starting around \$129 per month (Semrush). Owners who are not SEO experts struggle to turn tool output into action.

**1a. Opportunity**

Enable any small-business owner to get an evidence-based SEO audit in minutes from just a public website URL, with no account, no SEO background and no agency, closing the gap between expensive professional SEO tools and the millions of small businesses that need to be found online.

**Market Opportunity**

* 36+ million U.S. small businesses (SBA Office of Advocacy); entry-level paid SEO suites start around \$129 per month, leaving room for a free, plain-language alternative.  
* Competitive analysis: see Appendix, section A5.

**1b. Users & Needs**

**Primary users:** Small-business owners (for example shops, restaurants and local service providers) who have a public website, know little about SEO, and want more customers to find them online. They care about plain-language answers and clear next steps.

**Secondary users:** Freelance marketers, web designers and marketing coordinators who support small businesses and want a quick, evidence-based audit to share with a client.

**Key User Needs**

* As a small-business owner, I need to get an SEO audit by entering only my website URL because I do not want to create an account or connect private data.  
* As a small-business owner, I need to see my SEO health as simple scores and plain language because I do not know SEO terms.  
* As a small-business owner, I need to see the evidence behind every finding because I need to trust the results are real and not made up.  
* As a small-business owner, I need to know the top things to fix first because I have limited time and budget.  
* As a small-business owner, I need missing information labeled “Data unavailable” instead of counted as a failure because I do not want to be scored unfairly.  
* As a freelance marketer, I need a clear report I can hand to a client because I want to explain what to improve and why.

**2\. PROPOSED SOLUTION**

BizBoost AI is a web app that audits a small business’s website for SEO health and tells the owner what to fix. Users simply enter their public website address, and the system scans up to 10 pages, checks five SEO categories (keywords, content quality, local SEO, technical health, and credibility and backlinks), and calculates scores from measurable evidence. An AI assistant then explains each issue in plain language and recommends prioritized improvements. As a result, owners get the kind of audit a senior SEO specialist would run, in minutes, without SEO expertise or an expensive tool.

**2a. Value Proposition**

Small-business owners who struggle to understand and fix their website’s SEO because it takes specialist skills and costly tools use BizBoost AI, an AI SEO auditing assistant, to scan their public website and get scored, evidence-backed recommendations in minutes. Unlike expensive SEO suites and agencies, it needs no account, no private data and no SEO knowledge, and it clearly marks missing information instead of guessing, helping owners know exactly what to fix first.

**2b. Top 3 MVP Value Props**

**The Vitamin (must-have baseline):** A complete baseline audit of any public small-business website across five SEO categories (keywords, content, local SEO, technical SEO, credibility) with a score for each.

**The Painkiller (solves the core pain):** Turns confusing SEO work into plain-language findings, backed by evidence and a short list of prioritized fixes, with no account, no SEO knowledge and no agency fees.

**The Steroid (the magic moment):** An AI assistant that explains each issue and recommends a specific fix based on evidence from the owner’s own site, and honestly marks “Data unavailable” instead of guessing.

**2c. Goals & Non-Goals**

**Goals**

* Give small-business owners a clear, plain-language picture of their website’s SEO health from just a URL.  
* Make every finding trustworthy by tying it to evidence from the website or an identified data source.  
* Help owners know exactly what to fix first through prioritized recommendations.  
* Keep scoring honest by never penalizing a site for data the tool cannot access.  
* Deliver a working, demo-ready audit across all five categories within the six-day MVP.

**Non-Goals**

* Private data such as Google Analytics or Search Console, and user accounts: the MVP uses public data only so owners never need to connect anything.  
* Crawling more than 10 pages per audit: a small crawl keeps the six-day build safe and fast.  
* Ongoing monitoring, alerts, ranking-position tracking and automated link building: the job description includes these, but they are deferred to a later version.  
* Required inbound backlink analysis: it depends on a paid third-party provider, so it stays optional and shows “Data unavailable” without one.

**2d. Success Metrics**

| Goal | Signal | Metric | Target |
| :---- | :---- | :---- | :---- |
| Clear picture of SEO health | Owners complete an audit from a URL | Audit completion rate on valid public test sites | 90% or more of 10 test sites complete an audit |
| Fast results | Owners get results without waiting long | Time from Start Audit to displayed report | Under 2 minutes for a scan of up to 10 pages |
| Evidence-backed findings | Every finding shows where it came from | Share of findings with evidence or an identified data source | 100% of findings |
| Clear next steps | Report shows what to fix first | Reports with at least 3 prioritized recommendations | 100% of completed reports |
| Honest scoring | Missing data is labeled, not treated as failure | Data unavailable items counted as zero in any score | 0 items |
| Plain-language understanding | Test users can explain what to fix after reading the report | Test users who can name their top fix without help | 4 of 5 test users |
| Demo-ready MVP | All five categories return results | Categories returning a score or Data unavailable label | 5 of 5 by Day 6 |
| Trustworthy AI explanations | AI recommendations only describe what the scanner found | AI recommendations that cite something not in the evidence, reviewed on the 10 test sites | 0 recommendations |

**3\. REQUIREMENTS**

**User Journey 1: Small-business owner running an SEO audit on their website**

**Context:** This is the core journey. We are optimizing for getting from a URL to results in minutes, with no account and no setup.

**Sub-journey: Starting an audit**

* **\[P0\]** User can learn what BizBoost AI does from a landing page before starting.  
* **\[P0\]** User can enter a public business website URL and start an audit without creating an account.  
* **\[P0\]** User can see a clear message if the URL is invalid, unreachable or unsafe to scan, and what to do next.  
* **\[P1\]** User can enter a web address without typing https\://.  
* **\[P2\]** User can see an example report before running their own audit.

**Sub-journey: Scanning the website**

* **\[P0\]** User can see that the audit is in progress.  
* **\[P0\]** User can have up to 10 public pages from their website scanned.  
* **\[P0\]** User can see a clear message if the website does not allow scanning.  
* **\[P1\]** User can see which pages were scanned.

**Sub-journey: Running the five SEO checks**

* **\[P0\]** User can get results for keyword optimization, content quality, local SEO, technical SEO, and credibility and backlinks.  
* **\[P0\]** User can see “Data unavailable” instead of a failing score when information cannot be retrieved.  
* **\[P1\]** User can see mobile performance and speed results.  
* **\[P2\]** User can see inbound backlink information when a data provider is available.

**User Journey 2: Small-business owner understanding and acting on the report**

**Context:** The report is the product. We are optimizing for a non-expert understanding what is wrong, why it matters and what to do first.

**Sub-journey: Reading the results**

* **\[P0\]** User can see an overall SEO health score out of 100 and a score for each of the five categories.  
* **\[P0\]** User can see the evidence behind every finding, including what was found and where.  
* **\[P0\]** User can read every finding in plain language without SEO jargon.  
* **\[P1\]** User can tell which findings were measured and which are unavailable.

**Sub-journey: Deciding what to fix**

* **\[P0\]** User can see the top three recommended improvements in priority order.  
* **\[P0\]** User can see why each issue matters and a specific action to take.  
* **\[P1\]** User can expand findings by category.  
* **\[P1\]** User can run a new audit for another website.  
* **\[P2\]** User can copy or download the report to share with a web developer or colleague.

**4\. APPENDIX**

**A1. How the job description shaped the product**

We started from the B\&H Senior SEO Specialist job description, identified the recurring pain points of doing SEO well, and turned them into what BizBoost AI automates for small businesses.

* Technical and on-page audits; monitoring crawlability, speed, XML sitemaps, canonical tags, metadata and redirects: Technical SEO analyzer plus Google PageSpeed Insights.  
* Keyword research and knowledge of ranking factors: Keyword Optimization analyzer.  
* Requesting new or refreshed content and landing-page changes: Content Quality analyzer.  
* Link building and interlinking: Credibility and Backlinks analyzer (inbound backlinks optional).  
* Prioritizing projects based on data and reporting status: scoring engine, AI recommendations and report dashboard.  
* Local SEO was added because small businesses compete for nearby customers.  
* Deferred from the job description: ongoing alerts, ranking tracking and cross-department coordination.

**A2. Architecture decision**

BizBoost AI is one AI agent supported by five deterministic SEO analyzers, not five independent AI agents. The scanner decides whether something exists (for example, whether a meta description tag is present); the AI only explains the finding and recommends an action. Flow: URL entry, URL validation and safety check, audit orchestrator, website crawler, five analyzers (plus PageSpeed and optional backlink data), evidence and scoring engine, AI reasoning, recommendations and report, Streamlit results dashboard.

**A3. Technology**

Streamlit, Python, BeautifulSoup, Google PageSpeed Insights API and the Claude API (Anthropic).

**A4. System rules**

* **Public data only:** No private Google Analytics or Search Console access.  
* **Crawler safety:** Do not scan private IP addresses, localhost or unsafe redirects.  
* **Respect website access rules:** Check robots.txt, use reasonable crawl limits and identify our crawler.  
* **Evidence first:** Every finding connects to a measurable check or identified source.  
* **No invented data:** Missing backlink information stays unavailable, not zero.  
* **Honest scoring:** Do not penalize businesses for information the tool cannot access. When a check is unavailable, it is dropped from the score and the remaining checks’ weights are rescaled to add up to 100, so the score reflects only what was measured.  
* **Small crawl:** Maximum 10 pages for the initial version.  
* **Page selection:** The crawler starts with the homepage, then adds pages listed in the XML sitemap, then internal links found on the homepage, in that order, until it reaches 10 pages. Duplicate and off-site links are skipped.  
* **PageSpeed scope:** Google PageSpeed Insights runs on the homepage only, at the same time as the crawl, so the full audit stays under the 2-minute target.  
* **JavaScript-heavy sites:** The crawler reads each page’s HTML as the server sends it; BeautifulSoup cannot see content that is built by JavaScript. When a check cannot see the content it needs for this reason, it shows “Data unavailable”, not a failure.

**A5. Competitive context**

Paid SEO suites such as Semrush, Ahrefs and Moz serve marketing professionals and charge monthly fees. Agencies and in-house specialists cost more. BizBoost AI differentiates by being free to start, account-free, plain-language, and evidence-first.

**A6. Six-day implementation plan**

* Day 1: Streamlit interface, URL validation and crawler. Deliverable: website scanner.  
* Day 2: Keyword and content analyzers. Deliverable: first two SEO checks.  
* Day 3: Local, technical and credibility analyzers. Deliverable: all five SEO checks.  
* Day 4: PageSpeed, optional backlink integration and scoring. Deliverable: evidence-based results.  
* Day 5: Claude AI reasoning, recommendations and dashboard. Deliverable: AI-powered audit.  
* Day 6: Testing, bug fixes and presentation. Deliverable: working demo.

**A7. Open questions**

* Resolved: no backlink provider for the MVP. Backlinks stay in as an optional feature and are the first thing cut if time is short, so inbound backlink items show “Data unavailable”. Collaborator’s free Backlink Checker (powered by SE Ranking) is only a manual reference: it is a web form limited to 5 checks a day (20 with an account) and no backlink API was found, so we do not automate it. Version 2 idea: a provider with a real API, such as the SE Ranking API (price and terms not yet checked).  
* Resolved: the initial category weights are Technical SEO 25, Keyword Optimization 25, Content Quality 20, Local SEO 20, and Credibility and Backlinks 10 (see A10). They are a first guess and will be tuned after the 10 test sites.  
* Resolved: the default model is Claude Sonnet 5.5 (`claude-sonnet-5-5`), chosen for cost and speed, set with `ANTHROPIC_MODEL`. Budget: $40 of API credits, roughly 10 cents per audit (estimate). Before the demo, compare it with Claude Opus 5.5 on a few test sites and switch only if Sonnet fails the citation rule.  
* How should Local SEO be handled for businesses where local search is not relevant?

**A8. Risks and how we handle them**

* **PageSpeed is slow or rate-limited:** PageSpeed Insights can take several seconds per page and limits how often it can be called. We run it on the homepage only, at the same time as the crawl, with a 30-second timeout. If it times out or hits a limit, speed results show “Data unavailable” and the rest of the audit still finishes.  
* **Sites that block crawling:** Some sites block our crawler in robots.txt or with a firewall. We respect the block, stop the scan and tell the user in plain language that the site does not allow scanning. Pages we could not reach are listed as not scanned, never scored as failures.  
* **The AI explains something that is not in the evidence:** The AI could describe a problem the scanner never found. The AI only receives the scanner’s evidence, is told to explain only what is in it, and every recommendation must name the check it comes from. We review AI output on the 10 test sites and track it in the success metrics (target: 0 unsupported recommendations).

**A9. Scope tiers and fallback plan**

*Build status on 5 Nov 2026:* the URL validator, crawler and all five analyzers are built and tested. Still to build: PageSpeed, the scoring engine, the audit orchestrator, the AI agent with its output validator, the report dashboard, and the 10-site test run.

If time runs short, we protect the core and cut in this order.

* **Must ship, never cut:** URL validation, the crawler, the Technical, Keyword and Content analyzers, the scoring engine, the report with evidence and a top 3 fixes list, and AI explanations with the rule-based fallback text.  
* **Ship a simpler version:** Local SEO keeps only the phone number, address and map checks.  
* **Cut first, in this order:**  
  1. Inbound backlinks (the optional provider). The checks stay and show “Data unavailable”.  
  2. P2 items: the example report and copy or download of the report.  
  3. PageSpeed results. Speed items show “Data unavailable” and the rest of the audit still works.  
  4. The extra Local SEO checks above.

**A10. How the score is calculated**

Every check returns pass, warn, fail or unavailable. Each check has a weight (for example, a missing title counts 3 and a missing language tag counts 1).

* **Check points:** pass = 1, warn = half a point, fail = 0. A check that is unavailable is dropped, not counted as 0.  
* **Category score (0 to 100):** add up weight × points for the measured checks, divide by the total weight of those checks, and multiply by 100.  
* **Overall score (0 to 100):** the weighted average of the category scores, using the category weights below. A category with no measured checks is left out and the other weights are rescaled to add up to 100.

| Category | Weight |
| :---- | :---- |
| Technical SEO | 25 |
| Keyword Optimization | 25 |
| Content Quality | 20 |
| Local SEO | 20 |
| Credibility and Backlinks | 10 |

**Example:** a category has three checks, each with weight 3. The title passes, the meta description fails and the H1 warns: (3×1 + 3×0 + 3×0.5) ÷ 9 × 100 = 50. Now say the title and meta description both pass and the H1 check is unavailable. The score is (3×1 + 3×1) ÷ 6 × 100 = 100, not the 67 it would be if unavailable counted as a failure.

**Worked example (veganbodhi.com):** the category scores were Technical 100, Keywords 69, Content 70, Local 83 and Credibility 94. Overall = (100×25 + 69×25 + 70×20 + 83×20 + 94×10) ÷ 100, about 82 out of 100.

**A11. Accounts, keys and limits**

| Service | Used for | Status | Cost and limits |
| :---- | :---- | :---- | :---- |
| Claude API (Anthropic), model Claude Sonnet 5.5 | Plain-language explanations and the top 3 fixes | Key in hand, $40 of credits | About $2 per million input tokens and $10 per million output tokens (Anthropic’s published rates, October 2026). Our estimate is roughly 10 cents per audit, so about 400 audits. Rate limit: to confirm in the Anthropic Console. |
| Google PageSpeed Insights API | Homepage speed and mobile results | Key in hand | 25,000 queries per day and 30 per minute, read from the Google Cloud console on 5 Nov 2026 (usage was 0). We run one speed test per audit, so this is far more than we need. |
| Backlink data provider (optional) | Inbound backlinks | None for the MVP | Not needed to ship, shows “Data unavailable”. First thing cut if time is short. Collaborator’s free checker is a manual reference only (5 checks a day, no backlink API found). |

Keys live in a local `.env` file that is never committed to GitHub (the repository ignores it). The model is set with `ANTHROPIC_MODEL`, so we can compare it with Claude Opus 5.5 on the test sites without changing code.

**A12. What data is stored**

Nothing is stored after the audit. The website address, the scanned pages, the findings and the report exist in memory only while the audit runs and the results are on screen. There are no accounts, no database and no saved reports, and the app never touches private data such as Google Analytics.

Two outside services receive data to do their job: Google PageSpeed receives the homepage address, and the Claude API receives the findings and scores as text (the evidence, not the raw page HTML). Each provider handles what it receives under its own terms.

**A13. End-to-end scenario**

*An illustration using the real public site https://www.veganbodhi.com/ as a test case. Numbers come from a run of the analyzers built so far on 5 Nov 2026; speed results are not included yet, so they show “Data unavailable”.*

**The restaurant owner**

1. The owner of a restaurant opens BizBoost AI, types `veganbodhi.com` without `https://`, and clicks Start Audit. No account is needed. The app checks the address and turns it into `https://www.veganbodhi.com/`.  
2. The app scans the 5 pages listed in the site’s sitemap. In our test the scan took under 2 seconds. The full report target is under 2 minutes.  
3. The report shows an overall score of about 82 out of 100 and five category scores. Technical SEO is strong, and Keywords and Content are the lowest.  
4. Every finding shows its evidence. For example: “Meta description tag is missing” on the homepage.  
5. Gaps are labeled honestly. The contact, menu and about pages are built with JavaScript, so their text and heading checks show “Data unavailable” instead of failing. Backlinks and speed also show “Data unavailable”.  
6. The AI picks the top 3 fixes in plain language, each naming the check it came from:  
   * **Add a meta description to the homepage.** It is the short text shown under your link in search results, and yours is missing. Write one or two sentences about what you serve and where you are.  
   * **Add alt text to your photos.** 12 of the 14 homepage images have none. A short description of each dish or room helps search engines and screen readers.  
   * **Add local business markup.** Your page already shows a phone number, an address and a map, but search engines are not told in a form they can read. Adding Restaurant structured data fixes that.  
7. The owner makes the first fix in their website editor and runs a new audit to see the score change.

**The freelancer**

A freelance web designer runs the same audit for a client before a meeting. They read the findings by category, use the evidence to show the client what is wrong, and hand over the top 3 fixes as the to-do list. Copying or downloading the report is a P2 feature; until then they share the on-screen report.
