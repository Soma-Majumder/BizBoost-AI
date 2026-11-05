# BizBoost AI — Project plan

Nov 4, 2026 · @Erick

We present a complete working demo on Nov 12, 2026.

## Timeline

&#91;embedded content: BizBoost AI plan · Nov 4–12, demo on Nov 12\]

The engine must run end to end by Sun Nov 8 so AI and dashboard work can start on Nov 9; Nov 11 is for testing only.

## Who owns what

Erick owns the audit engine; Soma owns the user-facing side and the design story. Swap anything that fits your strengths better.

| Area | Erick | Soma |
| --- | --- | --- |
| Scanning | Repo, URL validation and safety check, crawler, page selection, robots.txt | Pick and document the 10 test sites |
| SEO checks | Keyword, content and technical analyzers, scoring engine | Local SEO and credibility analyzers, PageSpeed integration |
| AI | OpenRouter prompts, top 3 fixes, evidence citation rule | Review AI output for plain language |
| Interface | Wire the engine into Streamlit | Landing page, progress screen, results dashboard, error messages |
| Design | Architecture diagram | Wireframes, user flow diagram |
| Presenting | Live demo driver | Slides and narration |
| Testing | Speed and accuracy on 10 test sites | 5-user plain-language test |

## Day-by-day tasks

Build runs Nov 4–8 and Nov 10–11. Feature freeze is Nov 11 at 6 pm; after that, only bug fixes.

### Wed Nov 4 — Kickoff

- [ ] Both: agree on the owner split and the 10 test sites
- [x] Erick: create the repo, Streamlit skeleton, `.env` for API keys
- [x] Erick: URL validation and safety check (no private IPs, localhost, unsafe redirects)
- [ ] Soma: get the PageSpeed Insights and OpenRouter API keys and test one call each
- [ ] Soma: sketch wireframes for the landing page and the results report

### Thu Nov 5 — Crawler and design

- [x] Erick: crawler with page selection (homepage, sitemap, homepage links, up to 10) and robots.txt check
- [ ] Erick: clear messages for blocked or unreachable sites
- [ ] Soma: final wireframes, user flow and architecture diagrams
- [ ] Soma: start the demo slides

### Fri Nov 6 — First analyzers

- [x] Erick: keyword and content analyzers, each finding with its evidence and page
- [x] Soma: local SEO and credibility analyzers
- [ ] Soma: PageSpeed on the homepage, in parallel with the crawl, 30-second timeout

### Sat Nov 7 — Scoring

- [x] Erick: technical analyzer
- [ ] Erick: scoring engine, with unavailable checks dropped and weights rescaled to 100
- [ ] Soma: draft the demo slides

### Sun Nov 8 — End-to-end run

- [ ] Both: one site runs end to end from URL to scores (no AI yet)
- [ ] Both: review the run together and list what broke

### Mon Nov 9 — AI and report start

- [ ] Erick: start OpenRouter integration
- [ ] Soma: start the results dashboard layout
- [ ] Both: fix the bugs found in the Nov 8 run

### Tue Nov 10 — AI and report

- [ ] Erick: AI explanations and top 3 fixes, each naming the check it comes from
- [ ] Soma: results dashboard with overall and category scores, evidence, and Data unavailable labels
- [ ] Soma: progress screen and list of scanned pages

### Wed Nov 11 — Test and freeze

- [ ] Erick: run all 10 test sites and record completion and time to report
- [ ] Erick: review AI output for anything not in the evidence (target 0)
- [ ] Soma: plain-language test with 5 people (target 4 of 5 name their top fix)
- [ ] Both: fix bugs, then feature freeze at 6 pm
- [ ] Both: write the demo script and record a backup video

### Thu Nov 12 — Demo day

- [ ] Both: rehearse the demo twice in the morning
- [ ] Both: check API keys, internet and the backup video before presenting
- [ ] Both: present the complete demo

## Nov 12: complete demo

**Demo script (about 5 minutes)**

1. Soma: the problem and the user, in one slide (30 seconds)
2. Erick: enter a real small-business URL on the landing page and start the audit
3. Erick: show the progress screen and the list of scanned pages
4. Soma: walk through the overall score, the five category scores and one finding's evidence
5. Soma: point to a Data unavailable label and explain why it isn't a zero
6. Erick: show the top 3 fixes and how each names the check it comes from
7. Both: show the results on the 10 test sites against the success metrics

**Readiness checklist**

- [ ] At least 9 of 10 test sites complete an audit
- [ ] Every audit finishes in under 2 minutes
- [ ] 100% of findings show their evidence
- [ ] Every report has at least 3 prioritized fixes
- [ ] 0 Data unavailable items counted as zero
- [ ] 0 AI recommendations citing something not in the evidence
- [ ] 4 of 5 test users can name their top fix
- [ ] Demo site chosen and tested that morning
- [ ] Backup video recorded and ready to play

## Risks and buffer

| Risk | Fallback |
| --- | --- |
| Crawler or analyzers run late | Nov 8 end-to-end run is the checkpoint; if it slips, cut P1 and P2 items first (example report, expand-by-category, download) |
| PageSpeed slow or rate-limited during the demo | 30-second timeout shows Data unavailable; the rest of the audit still finishes |
| Live site blocks the crawler on demo day | Test the demo site that morning and keep a second site ready |
| AI writes something not in the evidence | Tighten the prompt on Nov 11 and re-review the 10 test sites |
| Internet or API keys fail live | Play the backup video recorded on Nov 11 |
| One partner is out for a day | Each owner pushes work to the repo daily so the other can pick it up |

**Buffer:** Nov 11 is mostly testing and fixing; nothing new is built that day.
