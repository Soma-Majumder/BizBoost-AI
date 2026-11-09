# AI explanation review: 10 test sites (issue #19)

**How to use:** for each check, read the scanner's **Evidence** first, then the **AI wrote** block. Tick the box if every number and claim in the AI text is supported by the evidence (or is a plain count of the entries). If not, write what is unsupported next to the box. Target: 0 unsupported recommendations.

Statuses: fail / warn / unavailable (could not be measured). Passed checks are not explained by the AI and are not listed.

---
## 01-buddha-bodai
- URL: https://www.veganbodhi.com/
- Overall score: **81**  |  technical seo 92, keyword optimization 69, content quality 70, local seo 83, credibility backlinks 95
- Pages scanned: 5  |  audit 15.6s, AI 13.0s  |  AI text used: True

### Top priorities (AI)

1. `technical.lcp` **Speed up the homepage on mobile** - The main content takes 16.9 seconds to appear on mobile, far above the 2.5 seconds considered good.
   - [ ] supported by evidence
2. `keyword.meta_description` **Add meta descriptions** - The summary is missing on the homepage and gallery page, and this check carries high weight.
   - [ ] supported by evidence
3. `content.word_count` **Add more text to the gallery page** - The gallery page has only 93 words, and this check carries high weight.
   - [ ] supported by evidence

### Explanations

#### `keyword.title` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.veganbodhi.com/) Title "Home - Bodhi Kosher Vegetarian Restaurant" starts with a generic word. Lead with what the business does.

**AI wrote:**
- Explanation: The homepage (https://www.veganbodhi.com/) has the title "Home - Bodhi Kosher Vegetarian Restaurant", which starts with the generic word "Home" instead of what the business does.
- Why it matters: The title is often the first thing people read about your site, so it should say right away what you offer.
- Action: Rewrite the homepage title to lead with what you do, for example starting with "Kosher Vegetarian Restaurant" followed by your name.

- [ ] supported by evidence   Notes: 

#### `keyword.meta_description` (fail/unavailable, weight 3)

**Evidence (scanner):**
- [fail] (https://www.veganbodhi.com/) Meta description tag is missing.
- [unavailable] (https://www.veganbodhi.com/contact-us/) The meta description tag could not be checked because this page is built by JavaScript.
- [fail] (https://www.veganbodhi.com/gallery/) Meta description tag is missing.
- [unavailable] (https://www.veganbodhi.com/menu/) The meta description tag could not be checked because this page is built by JavaScript.
- [unavailable] (https://www.veganbodhi.com/about/) The meta description tag could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The meta description (the short summary shown under your link in search results) is missing on https://www.veganbodhi.com/ and https://www.veganbodhi.com/gallery/. The scanner could not check it on https://www.veganbodhi.com/contact-us/, https://www.veganbodhi.com/menu/ and https://www.veganbodhi.com/about/ because those pages are built by JavaScript.
- Why it matters: Without a summary, search engines choose the snippet themselves, and it may not describe your restaurant well.
- Action: Add a short, friendly meta description to the homepage and the gallery page that says what you serve and where you are.

- [ ] supported by evidence   Notes: 

#### `keyword.h1` (fail/unavailable, weight 3)

**Evidence (scanner):**
- [unavailable] (https://www.veganbodhi.com/contact-us/) The H1 heading could not be checked because this page is built by JavaScript.
- [fail] (https://www.veganbodhi.com/gallery/) H1 heading is missing.
- [unavailable] (https://www.veganbodhi.com/menu/) The H1 heading could not be checked because this page is built by JavaScript.
- [unavailable] (https://www.veganbodhi.com/about/) The H1 heading could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The gallery page (https://www.veganbodhi.com/gallery/) has no H1 heading, which is the main title on the page itself. The scanner could not check this on https://www.veganbodhi.com/contact-us/, https://www.veganbodhi.com/menu/ and https://www.veganbodhi.com/about/ because those pages are built by JavaScript.
- Why it matters: A main heading tells visitors and search engines what the page is about.
- Action: Add one clear H1 heading to the gallery page, such as a title describing your restaurant photos.

- [ ] supported by evidence   Notes: 

#### `content.word_count` (fail/unavailable, weight 3)

**Evidence (scanner):**
- [unavailable] (https://www.veganbodhi.com/contact-us/) The amount of text could not be checked because this page is built by JavaScript.
- [fail] (https://www.veganbodhi.com/gallery/) Only 93 words of text. Pages with very little text rarely rank well.
- [unavailable] (https://www.veganbodhi.com/menu/) The amount of text could not be checked because this page is built by JavaScript.
- [unavailable] (https://www.veganbodhi.com/about/) The amount of text could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The gallery page (https://www.veganbodhi.com/gallery/) has only 93 words of text. The scanner could not check the amount of text on https://www.veganbodhi.com/contact-us/, https://www.veganbodhi.com/menu/ and https://www.veganbodhi.com/about/ because those pages are built by JavaScript.
- Why it matters: Pages with very little text give search engines little to understand and rarely rank well.
- Action: Add a few paragraphs to the gallery page describing your food, your dishes and your restaurant.

- [ ] supported by evidence   Notes: 

#### `content.image_alt` (fail, weight 2)

**Evidence (scanner):**
- [fail] (https://www.veganbodhi.com/) 12 of 14 images have no alt text, which describes them to search engines and screen readers.
- [fail] (https://www.veganbodhi.com/gallery/) 12 of 13 images have no alt text, which describes them to search engines and screen readers.

**AI wrote:**
- Explanation: On the homepage (https://www.veganbodhi.com/), 12 of 14 images have no alt text. On the gallery page (https://www.veganbodhi.com/gallery/), 12 of 13 images have none. Alt text is a short description of a picture.
- Why it matters: Alt text helps search engines and screen-reader users understand your photos, which matters for a food business with many images.
- Action: Add a short description to each image on the homepage and gallery page, such as the name of the dish shown.

- [ ] supported by evidence   Notes: 

#### `content.readability` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://www.veganbodhi.com/) Reading ease score is 49 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.

**AI wrote:**
- Explanation: The homepage (https://www.veganbodhi.com/) has a reading ease score of 49 out of 100, where 50 or more is easy to read.
- Why it matters: Text that is hard to read can lose visitors before they find your menu or details.
- Action: Edit the homepage text to use shorter sentences and simpler words.

- [ ] supported by evidence   Notes: 

#### `content.heading_structure` (warn, weight 1)

**Evidence (scanner):**
- [warn] (https://www.veganbodhi.com/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.

**AI wrote:**
- Explanation: On the homepage (https://www.veganbodhi.com/), headings skip from H2 to H4.
- Why it matters: Headings in order make the page easier to follow for visitors and for search engines.
- Action: Change the H4 headings that follow H2 to H3, or add the missing level, so the headings go in order.

- [ ] supported by evidence   Notes: 

#### `local.schema_markup` (fail, weight 2)

**Evidence (scanner):**
- [fail] No LocalBusiness structured data found. It tells search engines your address, hours and phone in a form they can read.

**AI wrote:**
- Explanation: The scanner found no LocalBusiness structured data on your site. This is hidden code that tells search engines your address, hours and phone in a form they can read.
- Why it matters: Without it, search engines have a harder time reading your basic local details.
- Action: Add LocalBusiness structured data with your address, hours and phone, using your website platform's SEO plugin or setting.

- [ ] supported by evidence   Notes: 

#### `technical.lcp` (fail, weight 2)

**Evidence (scanner):**
- [fail] The main content of the homepage takes 16.9 seconds to appear on mobile (slow, good is 2.5 seconds or less).

**AI wrote:**
- Explanation: The main content of the homepage takes 16.9 seconds to appear on mobile, while 2.5 seconds or less is considered good.
- Why it matters: A very slow first view can make people on phones give up before they see your restaurant.
- Action: Compress the large homepage images and remove any heavy elements that slow loading, then re-test.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (warn, weight 3)

**Evidence (scanner):**
- [warn] Google PageSpeed gives the homepage a mobile speed score of 58 out of 100 (room to speed up on mobile).

**AI wrote:**
- Explanation: Google PageSpeed gives the homepage a mobile speed score of 58 out of 100, which leaves room to speed up on mobile.
- Why it matters: A faster site is easier to use for visitors checking your restaurant on their phones.
- Action: Start by shrinking the homepage images, since your photos are likely a main cause of slow loading.

- [ ] supported by evidence   Notes: 

#### `credibility.privacy_policy` (warn, weight 1)

**Evidence (scanner):**
- [warn] No privacy policy or terms page found. It signals a trustworthy, professional site.

**AI wrote:**
- Explanation: The scanner found no privacy policy or terms page on your site.
- Why it matters: This kind of page signals a trustworthy, professional site.
- Action: Create a simple privacy policy page and link to it from your footer.

- [ ] supported by evidence   Notes: 

---
## 02-sen-saigon
- URL: https://sensaigon.com/
- Overall score: **75**  |  technical seo 100, keyword optimization 70, content quality 72, local seo 50, credibility backlinks 77
- Pages scanned: 10  |  audit 30.0s, AI 16.6s  |  AI text used: True

### Top priorities (AI)

1. `local.address` **Add your street address** - This is a high-weight local finding, and customers need to see where your restaurant is.
   - [ ] supported by evidence
2. `keyword.title` **Fix page titles** - Titles are a high-weight issue and affect many pages, including the home page.
   - [ ] supported by evidence
3. `keyword.meta_description` **Add missing meta descriptions** - This is a high-weight failure affecting three pages that have no search summary.
   - [ ] supported by evidence

### Explanations

#### `keyword.title` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://sensaigon.com/) Title "Home | Vegan Vietnamese Restaurant in NYC | Sen Saigon" starts with a generic word. Lead with what the business does.
- [warn] (https://sensaigon.com/catering) Title is 132 characters and may be cut off in search results. Aim for 20 to 65.
- [warn] (https://sensaigon.com/in-the-press) Title "In The Press" is only 12 characters. Aim for 20 to 65.
- [warn] (https://sensaigon.com/) Title "Home | Vegan Vietnamese Restaurant in NYC | Sen Saigon" starts with a generic word. Lead with what the business does.
- [warn] (https://sensaigon.com/about-us) Title "About Us" is only 8 characters. Aim for 20 to 65.
- [warn] (https://sensaigon.com/kosher-certificate) Title "Kosher Certificate" is only 18 characters. Aim for 20 to 65.
- [warn] (https://sensaigon.com/m/login) Title "Login" is only 5 characters. Aim for 20 to 65.
- [warn] (https://sensaigon.com/m/reset) Title "Reset your password" is only 19 characters. Aim for 20 to 65.
- [warn] (https://sensaigon.com/m/create) Title "Set your password" is only 17 characters. Aim for 20 to 65.
- [warn] (https://sensaigon.com/catering) Title is 132 characters and may be cut off in search results. Aim for 20 to 65.

**AI wrote:**
- Explanation: The home page title "Home | Vegan Vietnamese Restaurant in NYC | Sen Saigon" starts with the generic word "Home". The title on https://sensaigon.com/catering is 132 characters and may be cut off in search results. Several other pages have titles that are too short: https://sensaigon.com/in-the-press, https://sensaigon.com/about-us, https://sensaigon.com/kosher-certificate, https://sensaigon.com/m/login, https://sensaigon.com/m/reset and https://sensaigon.com/m/create.
- Why it matters: The page title is often the first thing people read about your site in search results, so a vague, cut-off or very short one wastes that space.
- Action: Rewrite each title to lead with what the page offers (for example, start the home page title with "Vegan Vietnamese Restaurant in NYC" instead of "Home") and keep it within the 20 to 65 characters the scanner suggests.

- [ ] supported by evidence   Notes: 

#### `keyword.meta_description` (fail, weight 3)

**Evidence (scanner):**
- [fail] (https://sensaigon.com/m/login) Meta description tag is missing.
- [fail] (https://sensaigon.com/m/reset) Meta description tag is missing.
- [fail] (https://sensaigon.com/m/create) Meta description tag is missing.

**AI wrote:**
- Explanation: The meta description (the short summary shown under your link in search results) is missing on https://sensaigon.com/m/login, https://sensaigon.com/m/reset and https://sensaigon.com/m/create.
- Why it matters: Without a summary, the text shown under your link is left to chance and may not describe the page well.
- Action: Add a short, clear meta description to these pages, or ask your web designer to add one.

- [ ] supported by evidence   Notes: 

#### `keyword.h1` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://sensaigon.com/) Page has 2 H1 headings. Use one main heading per page.
- [warn] (https://sensaigon.com/) Page has 2 H1 headings. Use one main heading per page.

**AI wrote:**
- Explanation: The home page (https://sensaigon.com/) has 2 H1 headings, which are the main headings on a page. The scanner recommends one main heading per page.
- Why it matters: A single clear main heading makes it obvious to visitors and search engines what the page is about.
- Action: Keep one H1 on the home page and change the other to a smaller heading level (H2).

- [ ] supported by evidence   Notes: 

#### `keyword.duplicate_titles` (fail, weight 2)

**Evidence (scanner):**
- [fail] 2 pages share the same title: https://sensaigon.com/, https://sensaigon.com/catering.

**AI wrote:**
- Explanation: 2 pages share the same title: https://sensaigon.com/ and https://sensaigon.com/catering.
- Why it matters: When two pages have the same title, it is harder for people and search engines to tell them apart.
- Action: Give the catering page its own title that describes your catering service.

- [ ] supported by evidence   Notes: 

#### `keyword.duplicate_meta_descriptions` (fail, weight 2)

**Evidence (scanner):**
- [fail] 2 pages share the same meta description: https://sensaigon.com/, https://sensaigon.com/catering.

**AI wrote:**
- Explanation: 2 pages share the same meta description: https://sensaigon.com/ and https://sensaigon.com/catering.
- Why it matters: Identical summaries make two different pages look like the same thing in search results.
- Action: Write a unique meta description for the catering page that explains your catering offer.

- [ ] supported by evidence   Notes: 

#### `content.readability` (fail/warn, weight 2)

**Evidence (scanner):**
- [fail] (https://sensaigon.com/) Reading ease score is 28 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sensaigon.com/catering) Reading ease score is 40 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sensaigon.com/in-the-press) Reading ease score is 45 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://sensaigon.com/) Reading ease score is 28 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sensaigon.com/about-us) Reading ease score is 42 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://sensaigon.com/kosher-certificate) Reading ease score is 25 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sensaigon.com/m/login) Reading ease score is 34 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sensaigon.com/m/reset) Reading ease score is 34 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sensaigon.com/m/create) Reading ease score is 32 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sensaigon.com/catering) Reading ease score is 40 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.

**AI wrote:**
- Explanation: The text on several pages is hard to read. The home page (https://sensaigon.com/) scores 28 out of 100 and https://sensaigon.com/kosher-certificate scores 25, where 50 or more is easy to read. The scanner also flagged https://sensaigon.com/catering, https://sensaigon.com/in-the-press, https://sensaigon.com/about-us, https://sensaigon.com/m/login, https://sensaigon.com/m/reset and https://sensaigon.com/m/create.
- Why it matters: Text that is easy to read is simpler for customers to take in quickly.
- Action: Edit your main pages, starting with the home page, to use shorter sentences and simpler words.

- [ ] supported by evidence   Notes: 

#### `content.heading_structure` (warn, weight 1)

**Evidence (scanner):**
- [warn] (https://sensaigon.com/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sensaigon.com/catering) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sensaigon.com/in-the-press) Headings skip from H1 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sensaigon.com/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sensaigon.com/about-us) Headings skip from H1 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sensaigon.com/kosher-certificate) Headings skip from H1 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sensaigon.com/m/login) Headings skip from H1 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sensaigon.com/m/reset) Headings skip from H1 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sensaigon.com/catering) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.

**AI wrote:**
- Explanation: Headings skip levels on several pages, from H2 to H4 on https://sensaigon.com/ and https://sensaigon.com/catering, and from H1 to H4 on https://sensaigon.com/in-the-press, https://sensaigon.com/about-us, https://sensaigon.com/kosher-certificate, https://sensaigon.com/m/login and https://sensaigon.com/m/reset.
- Why it matters: Headings in a logical order give each page a clear outline that is easier to follow.
- Action: Change the skipped headings so they follow in order (H1, then H2, then H3, and so on).

- [ ] supported by evidence   Notes: 

#### `content.word_count` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://sensaigon.com/kosher-certificate) 160 words of text. Aim for at least 250 to explain what you offer.
- [warn] (https://sensaigon.com/m/login) 148 words of text. Aim for at least 250 to explain what you offer.
- [warn] (https://sensaigon.com/m/reset) 133 words of text. Aim for at least 250 to explain what you offer.
- [warn] (https://sensaigon.com/m/create) 124 words of text. Aim for at least 250 to explain what you offer.

**AI wrote:**
- Explanation: Some pages have little text: https://sensaigon.com/kosher-certificate (160 words), https://sensaigon.com/m/login (148 words), https://sensaigon.com/m/reset (133 words) and https://sensaigon.com/m/create (124 words). The scanner suggests at least 250 words to explain what you offer.
- Why it matters: Pages with little text give visitors and search engines less to understand about your business.
- Action: Add more useful text to the Kosher Certificate page, for example what the certification means for your guests.

- [ ] supported by evidence   Notes: 

#### `content.duplicate_content` (fail, weight 2)

**Evidence (scanner):**
- [fail] 2 pages have identical text: https://sensaigon.com/, https://sensaigon.com/catering.

**AI wrote:**
- Explanation: 2 pages have identical text: https://sensaigon.com/ and https://sensaigon.com/catering.
- Why it matters: Identical text on two pages makes them compete with each other and gives visitors no reason to see both.
- Action: Rewrite the catering page so it has its own text about your catering service.

- [ ] supported by evidence   Notes: 

#### `local.address` (fail, weight 3)

**Evidence (scanner):**
- [fail] No street address found on the scanned pages. Customers and search engines look for it.

**AI wrote:**
- Explanation: The scanner found no street address on the pages it checked.
- Why it matters: Customers looking for your restaurant need to see where you are, and search engines look for an address too.
- Action: Add your full street address as text in the footer or on a contact area visible on every page.

- [ ] supported by evidence   Notes: 

#### `local.schema_markup` (fail, weight 2)

**Evidence (scanner):**
- [fail] No LocalBusiness structured data found. It tells search engines your address, hours and phone in a form they can read.

**AI wrote:**
- Explanation: No LocalBusiness structured data was found. This is hidden code that tells search engines your address, hours and phone in a form they can read.
- Why it matters: Without it, search engines have to guess your business details from the page text.
- Action: Ask your web designer, or use your website builder's SEO settings, to add LocalBusiness structured data with your address, hours and phone.

- [ ] supported by evidence   Notes: 

#### `local.map` (warn, weight 1)

**Evidence (scanner):**
- [warn] No map found. A map helps customers locate you.

**AI wrote:**
- Explanation: The scanner found no map on your site.
- Why it matters: A map helps customers see where you are at a glance.
- Action: Embed a Google Map of your restaurant location on your home page or contact area.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (unavailable, weight 3)

**Evidence (scanner):**
- [unavailable] The mobile speed score was not checked because Google PageSpeed took longer than 30 seconds.

**AI wrote:**
- Explanation: The mobile speed score could not be checked because Google PageSpeed took longer than 30 seconds.

- [ ] supported by evidence   Notes: 

#### `technical.lcp` (unavailable, weight 2)

**Evidence (scanner):**
- [unavailable] The main content load time was not checked because Google PageSpeed took longer than 30 seconds.

**AI wrote:**
- Explanation: The main content load time could not be checked because Google PageSpeed took longer than 30 seconds.

- [ ] supported by evidence   Notes: 

#### `technical.cls` (unavailable, weight 2)

**Evidence (scanner):**
- [unavailable] The layout stability was not checked because Google PageSpeed took longer than 30 seconds.

**AI wrote:**
- Explanation: Layout stability could not be checked because Google PageSpeed took longer than 30 seconds.

- [ ] supported by evidence   Notes: 

#### `technical.tbt` (unavailable, weight 1)

**Evidence (scanner):**
- [unavailable] The page responsiveness was not checked because Google PageSpeed took longer than 30 seconds.

**AI wrote:**
- Explanation: Page responsiveness could not be checked because Google PageSpeed took longer than 30 seconds.

- [ ] supported by evidence   Notes: 

#### `credibility.contact_page` (warn, weight 2)

**Evidence (scanner):**
- [warn] No contact page found, though contact details appear elsewhere. A dedicated contact page builds trust.

**AI wrote:**
- Explanation: The scanner found no contact page, though contact details appear elsewhere on the site.
- Why it matters: A dedicated contact page makes your business look more trustworthy and easier to reach.
- Action: Create a Contact page with your address, phone, email and hours, and link it in your main menu.

- [ ] supported by evidence   Notes: 

#### `credibility.privacy_policy` (warn, weight 1)

**Evidence (scanner):**
- [warn] No privacy policy or terms page found. It signals a trustworthy, professional site.

**AI wrote:**
- Explanation: No privacy policy or terms page was found.
- Why it matters: These pages signal a trustworthy, professional site, especially since your site has login and password pages.
- Action: Publish a simple privacy policy and terms page and link them in your footer.

- [ ] supported by evidence   Notes: 

#### `credibility.backlinks` (warn, weight 2)

**Evidence (scanner):**
- [warn] Only 6 referring domains found in Crawly's open web index, for example prettykosher.com, vegansexplore.com, veganuary.com. 10 or more is a healthier sign of trust. The index may be incomplete.

**AI wrote:**
- Explanation: Only 6 referring domains (other websites that link to yours) were found in Crawly's open web index, for example prettykosher.com, vegansexplore.com and veganuary.com. The index may be incomplete.
- Why it matters: Links from other sites are a sign of trust, and 10 or more is a healthier sign.
- Action: Ask food bloggers, press contacts and local partners who have featured you to link to your website.

- [ ] supported by evidence   Notes: 

---
## 03-ahimsa
- URL: https://ahimsany.com/
- Overall score: **81**  |  technical seo 94, keyword optimization 76, content quality 70, local seo 88, credibility backlinks 75
- Pages scanned: 8  |  audit 14.5s, AI 13.8s  |  AI text used: True

### Top priorities (AI)

1. `keyword.h1` **Fix the main headings** - The homepage has no H1 and the catering page has two, and this check carries a high weight.
   - [ ] supported by evidence
2. `keyword.meta_description` **Add missing meta descriptions** - Three pages have no search summary, and this check carries a high weight.
   - [ ] supported by evidence
3. `content.word_count` **Add more text to thin pages** - Four pages have very little text, and this check carries a high weight.
   - [ ] supported by evidence

### Explanations

#### `keyword.h1` (fail/warn, weight 3)

**Evidence (scanner):**
- [fail] (https://ahimsany.com/) H1 heading is missing.
- [warn] (https://ahimsany.com/catering-menu/) Page has 2 H1 headings. Use one main heading per page.
- [fail] (https://ahimsany.com/) H1 heading is missing.

**AI wrote:**
- Explanation: The homepage (https://ahimsany.com/) has no H1 heading, which is the main title on the page. The page https://ahimsany.com/catering-menu/ has 2 H1 headings instead of one.
- Why it matters: A single clear main heading tells visitors and search engines what each page is about.
- Action: Add one H1 heading to the homepage that says what you are, and remove the extra H1 on the catering menu page so only one remains.

- [ ] supported by evidence   Notes: 

#### `keyword.meta_description` (fail, weight 3)

**Evidence (scanner):**
- [fail] (https://ahimsany.com/hello-world/) Meta description tag is missing.
- [fail] (https://ahimsany.com/category/uncategorized/) Meta description tag is missing.
- [fail] (https://ahimsany.com/author/admin_0a4esdfe/) Meta description tag is missing.

**AI wrote:**
- Explanation: The meta description (the short summary shown under your link in search results) is missing on https://ahimsany.com/hello-world/, https://ahimsany.com/category/uncategorized/ and https://ahimsany.com/author/admin_0a4esdfe/.
- Why it matters: Without a summary, search engines choose their own text, which may not describe your restaurant well.
- Action: Write a short, unique description for each of these pages in your website's SEO settings, or remove the pages you don't need.

- [ ] supported by evidence   Notes: 

#### `keyword.duplicate_titles` (fail, weight 2)

**Evidence (scanner):**
- [fail] 1 pages share the same title: https://ahimsany.com/.

**AI wrote:**
- Explanation: The scanner found that https://ahimsany.com/ shares its page title with another page.
- Why it matters: Pages with the same title are harder to tell apart for visitors and search engines.
- Action: Give each page its own title that describes what is on that page.

- [ ] supported by evidence   Notes: 

#### `keyword.duplicate_meta_descriptions` (fail, weight 2)

**Evidence (scanner):**
- [fail] 1 pages share the same meta description: https://ahimsany.com/.

**AI wrote:**
- Explanation: The scanner found that https://ahimsany.com/ shares its meta description with another page.
- Why it matters: Repeating the same summary makes your pages look alike in search results.
- Action: Write a unique meta description for the homepage and for each other page that shares it.

- [ ] supported by evidence   Notes: 

#### `content.readability` (fail/warn, weight 2)

**Evidence (scanner):**
- [warn] (https://ahimsany.com/) Reading ease score is 34 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://ahimsany.com/about-us/) Reading ease score is 26 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://ahimsany.com/catering-menu/) Reading ease score is 41 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://ahimsany.com/) Reading ease score is 34 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.

**AI wrote:**
- Explanation: Text is hard to read on https://ahimsany.com/ (score 34 out of 100), https://ahimsany.com/about-us/ (26) and https://ahimsany.com/catering-menu/ (41). The scanner says 50 or more is easy to read.
- Why it matters: Visitors are more likely to understand your offer when the writing is simple and clear.
- Action: Rewrite the text on these pages with shorter sentences and simpler words, starting with the About page.

- [ ] supported by evidence   Notes: 

#### `content.heading_structure` (warn, weight 1)

**Evidence (scanner):**
- [warn] (https://ahimsany.com/) Headings skip from H2 to H6. Use headings in order so the page outline makes sense.
- [warn] (https://ahimsany.com/hello-world/) Headings skip from H1 to H3. Use headings in order so the page outline makes sense.
- [warn] (https://ahimsany.com/contact/) Headings skip from H1 to H6. Use headings in order so the page outline makes sense.
- [warn] (https://ahimsany.com/catering-menu/) Headings skip from H1 to H6. Use headings in order so the page outline makes sense.
- [warn] (https://ahimsany.com/) Headings skip from H2 to H6. Use headings in order so the page outline makes sense.

**AI wrote:**
- Explanation: Headings skip levels on https://ahimsany.com/ (H2 to H6), https://ahimsany.com/hello-world/ (H1 to H3), https://ahimsany.com/contact/ (H1 to H6) and https://ahimsany.com/catering-menu/ (H1 to H6).
- Why it matters: Headings in order make each page easier to follow and understand.
- Action: Change the headings on these pages so they go in order (H1, then H2, then H3) instead of jumping levels.

- [ ] supported by evidence   Notes: 

#### `content.word_count` (fail/warn, weight 3)

**Evidence (scanner):**
- [fail] (https://ahimsany.com/hello-world/) Only 94 words of text. Pages with very little text rarely rank well.
- [warn] (https://ahimsany.com/contact/) 116 words of text. Aim for at least 250 to explain what you offer.
- [fail] (https://ahimsany.com/category/uncategorized/) Only 62 words of text. Pages with very little text rarely rank well.
- [fail] (https://ahimsany.com/author/admin_0a4esdfe/) Only 62 words of text. Pages with very little text rarely rank well.

**AI wrote:**
- Explanation: Several pages have very little text: https://ahimsany.com/hello-world/ has 94 words, https://ahimsany.com/category/uncategorized/ and https://ahimsany.com/author/admin_0a4esdfe/ have 62 words each, and https://ahimsany.com/contact/ has 116 words.
- Why it matters: Pages with little text give visitors and search engines little to go on about what you offer.
- Action: Add useful details to the contact page, and either fill out or delete the placeholder pages (hello-world, uncategorized, author).

- [ ] supported by evidence   Notes: 

#### `content.duplicate_content` (fail, weight 2)

**Evidence (scanner):**
- [fail] 1 pages have identical text: https://ahimsany.com/.

**AI wrote:**
- Explanation: The scanner found that https://ahimsany.com/ has text identical to another page.
- Why it matters: Identical text on several pages makes it unclear which one should be shown.
- Action: Rewrite the text on one of the matching pages or remove the page you don't need.

- [ ] supported by evidence   Notes: 

#### `local.schema_markup` (warn, weight 2)

**Evidence (scanner):**
- [warn] Structured data describes an Organization but not a local business. LocalBusiness markup adds your address, hours and phone for search engines.

**AI wrote:**
- Explanation: Your site's hidden data describes an Organization but not a local business. LocalBusiness markup adds your address, hours and phone for search engines.
- Why it matters: Search engines can then better understand where your restaurant is and when it is open.
- Action: Add LocalBusiness markup with your address, hours and phone, using an SEO plugin or your web developer.

- [ ] supported by evidence   Notes: 

#### `local.directory_listings` (warn, weight 1)

**Evidence (scanner):**
- [warn] No links to local listing sites such as Yelp or Google Maps were found.

**AI wrote:**
- Explanation: No links to local listing sites such as Yelp or Google Maps were found on your site.
- Why it matters: Links to your listings help customers find you and read reviews elsewhere.
- Action: Add links to your Google Maps and Yelp listings on your contact page or footer.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (warn, weight 3)

**Evidence (scanner):**
- [warn] Google PageSpeed gives the homepage a mobile speed score of 76 out of 100 (room to speed up on mobile).

**AI wrote:**
- Explanation: Google PageSpeed gives the homepage a mobile speed score of 76 out of 100, so there is room to speed up on mobile.
- Why it matters: A faster site is easier for people to use on their phones.
- Action: Ask your web developer to compress large images and remove unneeded scripts on the homepage.

- [ ] supported by evidence   Notes: 

#### `technical.lcp` (fail, weight 2)

**Evidence (scanner):**
- [fail] The main content of the homepage takes 5.0 seconds to appear on mobile (slow, good is 2.5 seconds or less).

**AI wrote:**
- Explanation: The main content of the homepage takes 5.0 seconds to appear on mobile. The scanner says good is 2.5 seconds or less.
- Why it matters: Visitors on phones may leave if your main content takes too long to show up.
- Action: Shrink or compress the biggest image or banner at the top of the homepage so it loads faster.

- [ ] supported by evidence   Notes: 

#### `credibility.reviews` (warn, weight 2)

**Evidence (scanner):**
- [warn] No customer reviews or testimonials found. Showing them builds trust.

**AI wrote:**
- Explanation: No customer reviews or testimonials were found on the site.
- Why it matters: Showing reviews builds trust with new customers.
- Action: Add a few real customer reviews or a review widget to your homepage.

- [ ] supported by evidence   Notes: 

#### `credibility.privacy_policy` (warn, weight 1)

**Evidence (scanner):**
- [warn] No privacy policy or terms page found. It signals a trustworthy, professional site.

**AI wrote:**
- Explanation: No privacy policy or terms page was found.
- Why it matters: This kind of page signals a trustworthy, professional site.
- Action: Create a privacy policy page and link to it from your footer.

- [ ] supported by evidence   Notes: 

#### `credibility.backlinks` (warn, weight 2)

**Evidence (scanner):**
- [warn] No inbound backlinks were found in Crawly's open web index. That index may be incomplete, so this does not prove your site has none.

**AI wrote:**
- Explanation: No inbound backlinks (links from other sites to yours) were found in Crawly's open web index. That index may be incomplete, so this does not prove you have none.
- Why it matters: Links from other sites can show that your restaurant is known and trusted.
- Action: Ask local food bloggers, neighborhood groups or partners to link to your website.

- [ ] supported by evidence   Notes: 

---
## 04-next-level-vegan
- URL: https://www.nextlevelvg.com/location/next-level-burger-brooklyn/
- Overall score: **87**  |  technical seo 95, keyword optimization 91, content quality 71, local seo 83, credibility backlinks 100
- Pages scanned: 10  |  audit 17.7s, AI 12.9s  |  AI text used: True

### Top priorities (AI)

1. `technical.lcp` **Speed up homepage loading on mobile** - The homepage main content takes 12.3 seconds to appear on mobile, far above the 2.5 seconds the scanner calls good.
   - [ ] supported by evidence
2. `technical.speed_score` **Improve the mobile speed score** - The homepage scored 66 out of 100 on mobile, and this check carries high weight.
   - [ ] supported by evidence
3. `content.word_count` **Add more text to thin pages** - The hours-and-locations and events pages are below the 250-word suggestion, and this check carries high weight.
   - [ ] supported by evidence

### Explanations

#### `keyword.meta_description` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.nextlevelvg.com/hour-and-locations/) Meta description is 166 characters and may be cut off in search results. Aim for 70 to 160.
- [warn] (https://www.nextlevelvg.com/menus/) Meta description is 227 characters and may be cut off in search results. Aim for 70 to 160.
- [warn] (https://www.nextlevelvg.com/feast/) Meta description is 167 characters and may be cut off in search results. Aim for 70 to 160.
- [warn] (https://www.nextlevelvg.com/catering/) Meta description is 161 characters and may be cut off in search results. Aim for 70 to 160.

**AI wrote:**
- Explanation: The short page summary shown in search results (meta description) is longer than the scanner's suggested range on four pages: https://www.nextlevelvg.com/hour-and-locations/ (166 characters), https://www.nextlevelvg.com/menus/ (227 characters), https://www.nextlevelvg.com/feast/ (167 characters) and https://www.nextlevelvg.com/catering/ (161 characters). The scanner suggests 70 to 160.
- Why it matters: Long descriptions may be cut off in search results, so people may not see your full message.
- Action: Rewrite the meta description on each of these four pages so it falls within 70 to 160 characters, starting with the most important details.

- [ ] supported by evidence   Notes: 

#### `keyword.title` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.nextlevelvg.com/menus-NLB/) Title is 68 characters and may be cut off in search results. Aim for 20 to 65.

**AI wrote:**
- Explanation: The page title on https://www.nextlevelvg.com/menus-NLB/ is 68 characters, and the scanner suggests 20 to 65.
- Why it matters: A title that is too long may be cut off in search results.
- Action: Shorten the title of the menus-NLB page to 65 characters or fewer, keeping the key words at the start.

- [ ] supported by evidence   Notes: 

#### `keyword.h1` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.nextlevelvg.com/rewards/) Page has 2 H1 headings. Use one main heading per page.

**AI wrote:**
- Explanation: https://www.nextlevelvg.com/rewards/ has 2 H1 headings (the main headline of a page). The scanner suggests one per page.
- Why it matters: A single clear main heading makes it easier for visitors and search engines to see what the page is about.
- Action: Change one of the two H1 headings on the rewards page to a smaller heading style such as H2.

- [ ] supported by evidence   Notes: 

#### `content.readability` (fail/warn, weight 2)

**Evidence (scanner):**
- [fail] (https://www.nextlevelvg.com/location/next-level-burger-brooklyn/) Reading ease score is 18 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.nextlevelvg.com/) Reading ease score is 27 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.nextlevelvg.com/hour-and-locations/) Reading ease score is -29 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.nextlevelvg.com/menus/) Reading ease score is 50 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.nextlevelvg.com/menus-NLB/) Reading ease score is 49 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.nextlevelvg.com/feast/) Reading ease score is 35 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.nextlevelvg.com/events/) Reading ease score is -41 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.nextlevelvg.com/catering/) Reading ease score is 37 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.nextlevelvg.com/rewards/) Reading ease score is 49 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.nextlevelvg.com/our-story/) Reading ease score is 43 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.

**AI wrote:**
- Explanation: The scanner found text that is hard to read on many pages. Low scores (50 or more is easy): https://www.nextlevelvg.com/location/next-level-burger-brooklyn/ (18), https://www.nextlevelvg.com/ (27), https://www.nextlevelvg.com/hour-and-locations/ (-29), https://www.nextlevelvg.com/events/ (-41), https://www.nextlevelvg.com/feast/ (35), https://www.nextlevelvg.com/catering/ (37), https://www.nextlevelvg.com/our-story/ (43), https://www.nextlevelvg.com/menus/ (50), https://www.nextlevelvg.com/menus-NLB/ (49) and https://www.nextlevelvg.com/rewards/ (49).
- Why it matters: Text that is hard to read can make it harder for customers to quickly find what they need.
- Action: Start with the events and hours-and-locations pages: rewrite them using shorter sentences and simpler words.

- [ ] supported by evidence   Notes: 

#### `content.image_alt` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://www.nextlevelvg.com/location/next-level-burger-brooklyn/) 1 of 4 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.nextlevelvg.com/) 2 of 14 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.nextlevelvg.com/hour-and-locations/) 1 of 4 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.nextlevelvg.com/menus/) 1 of 4 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.nextlevelvg.com/menus-NLB/) 1 of 4 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.nextlevelvg.com/feast/) 1 of 4 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.nextlevelvg.com/events/) 1 of 4 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.nextlevelvg.com/catering/) 1 of 4 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.nextlevelvg.com/rewards/) 2 of 7 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.nextlevelvg.com/our-story/) 1 of 9 images have no alt text, which describes them to search engines and screen readers.

**AI wrote:**
- Explanation: Some images have no alt text (a short written description of the picture) on these pages: https://www.nextlevelvg.com/location/next-level-burger-brooklyn/ (1 of 4), https://www.nextlevelvg.com/ (2 of 14), https://www.nextlevelvg.com/hour-and-locations/ (1 of 4), https://www.nextlevelvg.com/menus/ (1 of 4), https://www.nextlevelvg.com/menus-NLB/ (1 of 4), https://www.nextlevelvg.com/feast/ (1 of 4), https://www.nextlevelvg.com/events/ (1 of 4), https://www.nextlevelvg.com/catering/ (1 of 4), https://www.nextlevelvg.com/rewards/ (2 of 7) and https://www.nextlevelvg.com/our-story/ (1 of 9).
- Why it matters: Alt text helps search engines understand your pictures and lets people using screen readers know what is shown.
- Action: Add a short description of what is in the picture to each image missing alt text, starting with the homepage.

- [ ] supported by evidence   Notes: 

#### `content.word_count` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.nextlevelvg.com/hour-and-locations/) 172 words of text. Aim for at least 250 to explain what you offer.
- [warn] (https://www.nextlevelvg.com/events/) 200 words of text. Aim for at least 250 to explain what you offer.

**AI wrote:**
- Explanation: Two pages have little text: https://www.nextlevelvg.com/hour-and-locations/ has 172 words and https://www.nextlevelvg.com/events/ has 200 words. The scanner suggests at least 250.
- Why it matters: Thin pages give visitors and search engines less information about what you offer.
- Action: Add a few more sentences to each page, such as details on what visitors can expect or answers to common questions.

- [ ] supported by evidence   Notes: 

#### `local.schema_markup` (fail, weight 2)

**Evidence (scanner):**
- [fail] No LocalBusiness structured data found. It tells search engines your address, hours and phone in a form they can read.

**AI wrote:**
- Explanation: The scanner found no LocalBusiness structured data on your site. This is hidden code that tells search engines your address, hours and phone number in a form they can read.
- Why it matters: Without it, search engines have to guess your key business details from the page text.
- Action: Add LocalBusiness structured data with your address, hours and phone number, using your website platform's SEO plugin or a developer.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (warn, weight 3)

**Evidence (scanner):**
- [warn] Google PageSpeed gives the homepage a mobile speed score of 66 out of 100 (room to speed up on mobile).

**AI wrote:**
- Explanation: Google PageSpeed gives the homepage a mobile speed score of 66 out of 100, which leaves room to speed up on mobile.
- Why it matters: A slow mobile site can frustrate people looking up your hours or menu on their phones.
- Action: Compress the largest homepage images and remove any unneeded scripts or plugins.

- [ ] supported by evidence   Notes: 

#### `technical.lcp` (fail, weight 2)

**Evidence (scanner):**
- [fail] The main content of the homepage takes 12.3 seconds to appear on mobile (slow, good is 2.5 seconds or less).

**AI wrote:**
- Explanation: The main content of the homepage takes 12.3 seconds to appear on mobile. The scanner says good is 2.5 seconds or less.
- Why it matters: Visitors on phones may leave before your page finishes loading.
- Action: Find the biggest item at the top of your homepage, usually a large image or video, and shrink or resize it so it loads faster.

- [ ] supported by evidence   Notes: 

---
## 05-slutty-vegan
- URL: https://sluttyveganatl.com/
- Overall score: **73**  |  technical seo 95, keyword optimization 48, content quality 71, local seo 75, credibility backlinks 77
- Pages scanned: 10  |  audit 30.1s, AI 40.3s  |  AI text used: True

### Top priorities (AI)

1. `keyword.meta_description` **Add meta descriptions to your pages** - It is missing on the most pages and carries high weight.
   - [ ] supported by evidence
2. `keyword.h1` **Fix main headings on each page** - Pages either have no H1 or too many, and this check carries high weight.
   - [ ] supported by evidence
3. `technical.noindex` **Review pages hidden from search** - It carries high weight and you should confirm only the right pages are hidden.
   - [ ] supported by evidence

### Explanations

#### `keyword.meta_description` (fail, weight 3)

**Evidence (scanner):**
- [fail] (https://sluttyveganatl.com/my-account/) Meta description tag is missing.
- [fail] (https://sluttyveganatl.com/lil-slut/) Meta description tag is missing.
- [fail] (https://sluttyveganatl.com/pinkycoleexperience/) Meta description tag is missing.
- [fail] (https://sluttyveganatl.com/cart/) Meta description tag is missing.
- [fail] (https://sluttyveganatl.com/cart/) Meta description tag is missing.
- [fail] (https://sluttyveganatl.com/jet/) Meta description tag is missing.
- [fail] (https://sluttyveganatl.com/luckyslut/) Meta description tag is missing.
- [fail] (https://sluttyveganatl.com/clubculture/) Meta description tag is missing.
- [fail] (https://sluttyveganatl.com/privacy-policy/) Meta description tag is missing.

**AI wrote:**
- Explanation: The scanner found no meta description (the short summary shown under your link in search results) on several pages: https://sluttyveganatl.com/my-account/, https://sluttyveganatl.com/lil-slut/, https://sluttyveganatl.com/pinkycoleexperience/, https://sluttyveganatl.com/cart/, https://sluttyveganatl.com/jet/, https://sluttyveganatl.com/luckyslut/, https://sluttyveganatl.com/clubculture/ and https://sluttyveganatl.com/privacy-policy/.
- Why it matters: Without a summary you write yourself, search engines have to pick the text shown for your page, and it may not sell your restaurant well.
- Action: Write a short, appealing summary for each of these pages in your website's SEO settings, starting with the lil-slut, pinkycoleexperience, jet, luckyslut and clubculture pages.

- [ ] supported by evidence   Notes: 

#### `keyword.h1` (fail/warn, weight 3)

**Evidence (scanner):**
- [fail] (https://sluttyveganatl.com/my-account/) H1 heading is missing.
- [warn] (https://sluttyveganatl.com/pinkycoleexperience/) Page has 3 H1 headings. Use one main heading per page.
- [fail] (https://sluttyveganatl.com/cart/) H1 heading is missing.
- [fail] (https://sluttyveganatl.com/cart/) H1 heading is missing.
- [warn] (https://sluttyveganatl.com/jet/) Page has 2 H1 headings. Use one main heading per page.
- [fail] (https://sluttyveganatl.com/luckyslut/) H1 heading is missing.
- [warn] (https://sluttyveganatl.com/clubculture/) Page has 5 H1 headings. Use one main heading per page.
- [fail] (https://sluttyveganatl.com/privacy-policy/) H1 heading is missing.

**AI wrote:**
- Explanation: Some pages have no main heading (H1): https://sluttyveganatl.com/my-account/, https://sluttyveganatl.com/cart/, https://sluttyveganatl.com/luckyslut/ and https://sluttyveganatl.com/privacy-policy/. Others have more than one: https://sluttyveganatl.com/pinkycoleexperience/ has 3, https://sluttyveganatl.com/jet/ has 2 and https://sluttyveganatl.com/clubculture/ has 5.
- Why it matters: One clear main heading tells visitors and search engines what each page is about.
- Action: Give each page exactly one H1 that describes it, and change the extra H1s on the pinkycoleexperience, jet and clubculture pages to smaller headings.

- [ ] supported by evidence   Notes: 

#### `keyword.title` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://sluttyveganatl.com/cart/) Title "Cart - Slutty Vegan" is only 19 characters. Aim for 20 to 65.
- [warn] (https://sluttyveganatl.com/cart/) Title "Cart - Slutty Vegan" is only 19 characters. Aim for 20 to 65.
- [warn] (https://sluttyveganatl.com/jet/) Title "JET - Slutty Vegan" is only 18 characters. Aim for 20 to 65.

**AI wrote:**
- Explanation: The page title is short on https://sluttyveganatl.com/cart/ ("Cart - Slutty Vegan", 19 characters) and https://sluttyveganatl.com/jet/ ("JET - Slutty Vegan", 18 characters). The scanner suggests 20 to 65 characters.
- Why it matters: The title is the clickable headline in search results, and short titles say little about what the page offers.
- Action: Lengthen the title on the jet page to say what it is, for example by adding a few descriptive words.

- [ ] supported by evidence   Notes: 

#### `keyword.duplicate_titles` (fail, weight 2)

**Evidence (scanner):**
- [fail] 1 pages share the same title: https://sluttyveganatl.com/cart/.

**AI wrote:**
- Explanation: The scanner reports that the page https://sluttyveganatl.com/cart/ shares its title with another page.
- Why it matters: Pages with the same title look identical in search results and make it harder for people to tell them apart.
- Action: Give each page its own unique title, starting with the cart page.

- [ ] supported by evidence   Notes: 

#### `content.readability` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://sluttyveganatl.com/) Reading ease score is 36 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sluttyveganatl.com/my-account/) Reading ease score is 34 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sluttyveganatl.com/lil-slut/) Reading ease score is 39 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sluttyveganatl.com/pinkycoleexperience/) Reading ease score is 35 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sluttyveganatl.com/cart/) Reading ease score is 34 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sluttyveganatl.com/cart/) Reading ease score is 34 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sluttyveganatl.com/jet/) Reading ease score is 33 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sluttyveganatl.com/luckyslut/) Reading ease score is 39 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sluttyveganatl.com/clubculture/) Reading ease score is 36 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://sluttyveganatl.com/privacy-policy/) Reading ease score is 30 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.

**AI wrote:**
- Explanation: The text on many pages is hard to read, with reading ease scores between 30 and 39 out of 100 (50 or more is easy to read). Affected pages include https://sluttyveganatl.com/, /my-account/, /lil-slut/, /pinkycoleexperience/, /cart/, /jet/, /luckyslut/, /clubculture/ and /privacy-policy/.
- Why it matters: Text that is easier to read is easier for customers to take in quickly.
- Action: Rewrite the text on your home page with shorter sentences and simpler words, then do the same for the other pages.

- [ ] supported by evidence   Notes: 

#### `content.heading_structure` (warn, weight 1)

**Evidence (scanner):**
- [warn] (https://sluttyveganatl.com/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sluttyveganatl.com/my-account/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sluttyveganatl.com/lil-slut/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sluttyveganatl.com/pinkycoleexperience/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sluttyveganatl.com/cart/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sluttyveganatl.com/cart/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sluttyveganatl.com/jet/) Headings skip from H1 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sluttyveganatl.com/luckyslut/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://sluttyveganatl.com/clubculture/) Headings skip from H1 to H3. Use headings in order so the page outline makes sense.
- [warn] (https://sluttyveganatl.com/privacy-policy/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.

**AI wrote:**
- Explanation: Headings skip levels on several pages, for example H2 to H4 on https://sluttyveganatl.com/, /my-account/, /lil-slut/, /pinkycoleexperience/, /cart/, /luckyslut/ and /privacy-policy/, and H1 to H4 or H1 to H3 on https://sluttyveganatl.com/jet/ and https://sluttyveganatl.com/clubculture/.
- Why it matters: Headings in order make a page easier to follow for visitors and for screen readers.
- Action: Edit the headings on these pages so they step down in order (H1, then H2, then H3) without skipping.

- [ ] supported by evidence   Notes: 

#### `content.image_alt` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://sluttyveganatl.com/) 2 of 33 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://sluttyveganatl.com/my-account/) 1 of 13 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://sluttyveganatl.com/lil-slut/) 1 of 19 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://sluttyveganatl.com/pinkycoleexperience/) 1 of 23 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://sluttyveganatl.com/cart/) 1 of 13 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://sluttyveganatl.com/cart/) 1 of 13 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://sluttyveganatl.com/jet/) 1 of 22 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://sluttyveganatl.com/luckyslut/) 1 of 17 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://sluttyveganatl.com/clubculture/) 1 of 13 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://sluttyveganatl.com/privacy-policy/) 1 of 13 images have no alt text, which describes them to search engines and screen readers.

**AI wrote:**
- Explanation: Some images are missing alt text (a short description of the image) on https://sluttyveganatl.com/ (2 of 33), and 1 image each on /my-account/ (of 13), /lil-slut/ (of 19), /pinkycoleexperience/ (of 23), /cart/ (of 13), /jet/ (of 22), /luckyslut/ (of 17), /clubculture/ (of 13) and /privacy-policy/ (of 13).
- Why it matters: Alt text helps people using screen readers and tells search engines what your images show.
- Action: Add a short description to each image missing alt text, starting with the 2 on your home page.

- [ ] supported by evidence   Notes: 

#### `content.duplicate_content` (fail, weight 2)

**Evidence (scanner):**
- [fail] 1 pages have identical text: https://sluttyveganatl.com/cart/.

**AI wrote:**
- Explanation: The scanner found that the page https://sluttyveganatl.com/cart/ has text identical to another page.
- Why it matters: Repeated text across pages makes it harder for search engines to tell which page to show.
- Action: Make the text on the cart page unique, or let search engines know which version is the main one.

- [ ] supported by evidence   Notes: 

#### `local.phone_consistency` (warn, weight 1)

**Evidence (scanner):**
- [warn] 2 different phone numbers appear on the site: //+18554397588; 6789748680. Use one consistent version unless you have several locations.

**AI wrote:**
- Explanation: 2 different phone numbers appear on the site: //+18554397588 and 6789748680.
- Why it matters: Different numbers can confuse customers and make your business details look unreliable.
- Action: Use one consistent phone number across the site, unless the second belongs to a different location.

- [ ] supported by evidence   Notes: 

#### `local.address_consistency` (warn, weight 1)

**Evidence (scanner):**
- [warn] 4 different addresss appear on the site: 164 N McDonough St Jonesboro, GA 30236; 476 Edgewood Ave SE Atlanta, GA 30312; 7 55th Pl S Birmingham, AL 35212; 690 Fulton St Brooklyn, NY 11217. Use one consistent version unless you have several locations.

**AI wrote:**
- Explanation: 4 different addresses appear on the site: 164 N McDonough St Jonesboro, GA 30236; 476 Edgewood Ave SE Atlanta, GA 30312; 7 55th Pl S Birmingham, AL 35212; and 690 Fulton St Brooklyn, NY 11217.
- Why it matters: Customers and search engines need to know clearly where each of your locations is.
- Action: If these are separate locations, give each its own labeled page with a consistent address format; otherwise remove the ones that don't apply.

- [ ] supported by evidence   Notes: 

#### `local.schema_markup` (warn, weight 2)

**Evidence (scanner):**
- [warn] Structured data describes an Organization but not a local business. LocalBusiness markup adds your address, hours and phone for search engines.

**AI wrote:**
- Explanation: The site's structured data (hidden labels that describe your business to search engines) describes an Organization but not a local business.
- Why it matters: Local business labels give search engines your address, hours and phone number.
- Action: Add LocalBusiness structured data with your address, hours and phone, using an SEO plugin or your web developer.

- [ ] supported by evidence   Notes: 

#### `local.map` (warn, weight 1)

**Evidence (scanner):**
- [warn] No map found. A map helps customers locate you.

**AI wrote:**
- Explanation: The scanner found no map on the site.
- Why it matters: A map helps customers find your restaurant locations.
- Action: Embed a Google Map on your locations page.

- [ ] supported by evidence   Notes: 

#### `local.directory_listings` (warn, weight 1)

**Evidence (scanner):**
- [warn] No links to local listing sites such as Yelp or Google Maps were found.

**AI wrote:**
- Explanation: No links to local listing sites such as Yelp or Google Maps were found.
- Why it matters: Links to your listings make it easy for customers to find reviews and directions.
- Action: Add links to your Google Maps and Yelp listings on your site, for example in the footer.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (unavailable, weight 3)

**Evidence (scanner):**
- [unavailable] The mobile speed score was not checked because Google PageSpeed took longer than 30 seconds.

**AI wrote:**
- Explanation: The mobile speed score could not be checked because Google PageSpeed took longer than 30 seconds.

- [ ] supported by evidence   Notes: 

#### `technical.lcp` (unavailable, weight 2)

**Evidence (scanner):**
- [unavailable] The main content load time was not checked because Google PageSpeed took longer than 30 seconds.

**AI wrote:**
- Explanation: The main content load time could not be checked because Google PageSpeed took longer than 30 seconds.

- [ ] supported by evidence   Notes: 

#### `technical.cls` (unavailable, weight 2)

**Evidence (scanner):**
- [unavailable] The layout stability was not checked because Google PageSpeed took longer than 30 seconds.

**AI wrote:**
- Explanation: Layout stability could not be checked because Google PageSpeed took longer than 30 seconds.

- [ ] supported by evidence   Notes: 

#### `technical.tbt` (unavailable, weight 1)

**Evidence (scanner):**
- [unavailable] The page responsiveness was not checked because Google PageSpeed took longer than 30 seconds.

**AI wrote:**
- Explanation: Page responsiveness could not be checked because Google PageSpeed took longer than 30 seconds.

- [ ] supported by evidence   Notes: 

#### `technical.noindex` (fail, weight 3)

**Evidence (scanner):**
- [fail] 3 page(s) tell search engines not to list them (noindex): https://sluttyveganatl.com/my-account/, https://sluttyveganatl.com/cart/, https://sluttyveganatl.com/cart/.

**AI wrote:**
- Explanation: 3 page entries tell search engines not to list them (noindex): https://sluttyveganatl.com/my-account/ and https://sluttyveganatl.com/cart/, which is listed more than once.
- Why it matters: Pages marked this way won't appear in search results, which is fine for account and cart pages but a problem if it was set by mistake.
- Action: Check that noindex is only set on pages you want hidden, such as the account and cart pages.

- [ ] supported by evidence   Notes: 

#### `credibility.contact_page` (warn, weight 2)

**Evidence (scanner):**
- [warn] No contact page found, though contact details appear elsewhere. A dedicated contact page builds trust.

**AI wrote:**
- Explanation: No contact page was found, though contact details appear elsewhere on the site.
- Why it matters: A dedicated contact page builds trust and makes it easy for customers to reach you.
- Action: Create a Contact page with your phone, email and locations and link it in your main menu.

- [ ] supported by evidence   Notes: 

#### `credibility.reviews` (warn, weight 2)

**Evidence (scanner):**
- [warn] No customer reviews or testimonials found. Showing them builds trust.

**AI wrote:**
- Explanation: No customer reviews or testimonials were found on the site.
- Why it matters: Reviews help new customers trust your restaurant.
- Action: Add a few customer reviews or testimonials to your home page.

- [ ] supported by evidence   Notes: 

#### `credibility.toxic_backlinks` (warn, weight 1)

**Evidence (scanner):**
- [warn] 5 of the 100 links listed may be harmful (marked toxic by the provider). Consider asking those sites to remove the links.

**AI wrote:**
- Explanation: 5 of the 100 links listed pointing to your site may be harmful (marked toxic by the provider).
- Why it matters: Low-quality links from other sites can hurt your site's reputation.
- Action: Contact the owners of those sites and ask them to remove the links.

- [ ] supported by evidence   Notes: 

---
## 06-kailash-parbat
- URL: https://www.kailashparbatnyc.net/
- Overall score: **91**  |  technical seo 95, keyword optimization 93, content quality 88, local seo 89, credibility backlinks 85
- Pages scanned: 10  |  audit 16.4s, AI 12.8s  |  AI text used: True

### Top priorities (AI)

1. `technical.lcp` **Speed up the homepage on mobile** - The main homepage content takes 18.2 seconds to appear on mobile, a clear failure that can drive visitors away.
   - [ ] supported by evidence
2. `keyword.meta_description` **Add a meta description to the contact page** - This is a failed check on a page where customers look for your details.
   - [ ] supported by evidence
3. `keyword.title` **Fix the three page titles** - Three pages have titles that are too long or too short, and it is a higher-weight check.
   - [ ] supported by evidence

### Explanations

#### `keyword.title` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.kailashparbatnyc.net/) Title is 73 characters and may be cut off in search results. Aim for 20 to 65.
- [warn] (https://www.kailashparbatnyc.net/contact-us) Title "Kailash Parbat" is only 14 characters. Aim for 20 to 65.
- [warn] (https://www.kailashparbatnyc.net/about-us) Title is 68 characters and may be cut off in search results. Aim for 20 to 65.

**AI wrote:**
- Explanation: Three page titles are flagged. The titles on https://www.kailashparbatnyc.net/ (73 characters) and https://www.kailashparbatnyc.net/about-us (68 characters) may be cut off in search results, while the title on https://www.kailashparbatnyc.net/contact-us ("Kailash Parbat", 14 characters) is very short.
- Why it matters: The page title is often the first thing people see in search results, so a cut-off or bare title makes your listing less clear.
- Action: Rewrite these three titles to fit within the scanner's 20 to 65 character range, and add what you offer and your area to the contact page title.

- [ ] supported by evidence   Notes: 

#### `keyword.meta_description` (fail, weight 3)

**Evidence (scanner):**
- [fail] (https://www.kailashparbatnyc.net/contact-us) Meta description tag is missing.

**AI wrote:**
- Explanation: The meta description (the short summary shown under your title in search results) is missing on https://www.kailashparbatnyc.net/contact-us.
- Why it matters: Without it, search engines have to pick their own snippet, which may not describe your page well.
- Action: Add a short, friendly meta description to the contact page that mentions your restaurant, location and how to reach you.

- [ ] supported by evidence   Notes: 

#### `content.readability` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://www.kailashparbatnyc.net/) Reading ease score is 49 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.kailashparbatnyc.net/about-us) Reading ease score is 46 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.kailashparbatnyc.net/menu) Reading ease score is 42 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.kailashparbatnyc.net/menu/diwani-handi) Reading ease score is 35 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.kailashparbatnyc.net/menu/veg-biryani) Reading ease score is 36 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.kailashparbatnyc.net/menu/north-indian) Reading ease score is 39 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.kailashparbatnyc.net/menu/street-food) Reading ease score is 42 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.kailashparbatnyc.net/menu/vegetarian) Reading ease score is 41 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.kailashparbatnyc.net/menu/delivery) Reading ease score is 44 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.

**AI wrote:**
- Explanation: Several pages scored below the scanner's easy-reading mark of 50: https://www.kailashparbatnyc.net/ (49), /about-us (46), /menu (42), /menu/diwani-handi (35), /menu/veg-biryani (36), /menu/north-indian (39), /menu/street-food (42), /menu/vegetarian (41) and /menu/delivery (44).
- Why it matters: Text that is hard to read can lose visitors who just want a quick answer about your food or ordering.
- Action: Start with the lowest-scoring page, /menu/diwani-handi, and rewrite its text using shorter sentences and simpler words.

- [ ] supported by evidence   Notes: 

#### `content.word_count` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.kailashparbatnyc.net/contact-us) 100 words of text. Aim for at least 250 to explain what you offer.

**AI wrote:**
- Explanation: The page https://www.kailashparbatnyc.net/contact-us has only 100 words of text, and the scanner suggests at least 250 to explain what you offer.
- Why it matters: A thin page gives visitors and search engines little to understand about your restaurant.
- Action: Add a few paragraphs to the contact page covering your location, opening hours, how to reach you and what guests can expect.

- [ ] supported by evidence   Notes: 

#### `local.phone_consistency` (warn, weight 1)

**Evidence (scanner):**
- [warn] 2 different phone numbers appear on the site: +12126794238; 123-456-7890. Use one consistent version unless you have several locations.

**AI wrote:**
- Explanation: Two different phone numbers appear on the site: +12126794238 and 123-456-7890.
- Why it matters: Mixed contact details can confuse customers, and the second one looks like a placeholder that won't reach you.
- Action: Find where 123-456-7890 appears and replace it with your real phone number, written the same way everywhere.

- [ ] supported by evidence   Notes: 

#### `local.address_consistency` (warn, weight 1)

**Evidence (scanner):**
- [warn] 2 different addresss appear on the site: , , , , 99 Lexington Ave, New York, New York, 10016, US ,; 99 Lexington Ave, New York, New York, 10016. Use one consistent version unless you have several locations.

**AI wrote:**
- Explanation: Two different versions of your address appear on the site, both for 99 Lexington Ave, New York, New York, 10016, but one has extra commas and "US" in it.
- Why it matters: Matching address details everywhere make it clearer to customers and search tools that this is one location.
- Action: Pick one clean address format and use it on every page and in your site footer.

- [ ] supported by evidence   Notes: 

#### `local.directory_listings` (warn, weight 1)

**Evidence (scanner):**
- [warn] No links to local listing sites such as Yelp or Google Maps were found.

**AI wrote:**
- Explanation: No links to local listing sites such as Yelp or Google Maps were found on the site.
- Why it matters: Links to your listings make it easier for customers to find reviews, directions and hours.
- Action: Add links to your Google Maps and Yelp listings in your site footer or on the contact page.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (warn, weight 3)

**Evidence (scanner):**
- [warn] Google PageSpeed gives the homepage a mobile speed score of 55 out of 100 (room to speed up on mobile).

**AI wrote:**
- Explanation: Google PageSpeed gives the homepage a mobile speed score of 55 out of 100, which leaves room to speed up on mobile.
- Why it matters: A slow site on phones is frustrating for people trying to check your menu or hours.
- Action: Ask your web developer to work through the PageSpeed report for the homepage, starting with compressing large images.

- [ ] supported by evidence   Notes: 

#### `technical.lcp` (fail, weight 2)

**Evidence (scanner):**
- [fail] The main content of the homepage takes 18.2 seconds to appear on mobile (slow, good is 2.5 seconds or less).

**AI wrote:**
- Explanation: The main content of the homepage takes 18.2 seconds to appear on mobile, while 2.5 seconds or less is considered good.
- Why it matters: Visitors on phones may leave before your homepage shows anything useful.
- Action: Ask your web developer to find what is slowing the main homepage content, such as a large hero image or video, and shrink or defer it.

- [ ] supported by evidence   Notes: 

#### `credibility.privacy_policy` (warn, weight 1)

**Evidence (scanner):**
- [warn] No privacy policy or terms page found. It signals a trustworthy, professional site.

**AI wrote:**
- Explanation: No privacy policy or terms page was found on the site.
- Why it matters: Such a page signals that your site is trustworthy and professional.
- Action: Create a simple privacy policy page and link to it from your site footer.

- [ ] supported by evidence   Notes: 

#### `credibility.backlinks` (warn, weight 2)

**Evidence (scanner):**
- [warn] No inbound backlinks were found in Crawly's open web index. That index may be incomplete, so this does not prove your site has none.

**AI wrote:**
- Explanation: No inbound backlinks (links from other websites to yours) were found in Crawly's open web index, which may be incomplete, so this does not prove you have none.
- Why it matters: Links from other sites can show that others know and recommend your business.
- Action: Ask local food bloggers, nearby business groups or your delivery partners to link to your website.

- [ ] supported by evidence   Notes: 

---
## 07-jajaja
- URL: https://www.jajajamexicana.com/
- Overall score: **84**  |  technical seo 96, keyword optimization 92, content quality 63, local seo 79, credibility backlinks 82
- Pages scanned: 10  |  audit 11.7s, AI 13.5s  |  AI text used: True

### Top priorities (AI)

1. `content.word_count` **Add more text to thin pages** - It has the highest weight and affects the most pages, with several pages failing for very little text.
   - [ ] supported by evidence
2. `keyword.title` **Improve your page titles** - It has a high weight and the homepage title starts with the generic word "Home" instead of what you do.
   - [ ] supported by evidence
3. `local.phone` **Show your phone number on the homepage** - It has a high weight and customers landing on your homepage can't find your number there.
   - [ ] supported by evidence

### Explanations

#### `keyword.title` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.jajajamexicana.com/) Title "Home - Jajaja Mexicana" starts with a generic word. Lead with what the business does.
- [warn] (https://www.jajajamexicana.com/cinco-de-mexico) Title is 68 characters and may be cut off in search results. Aim for 20 to 65.

**AI wrote:**
- Explanation: The homepage title "Home - Jajaja Mexicana" (https://www.jajajamexicana.com/) starts with a generic word. The title on https://www.jajajamexicana.com/cinco-de-mexico is 68 characters and may be cut off in search results.
- Why it matters: The title is often the first thing people read about your business, so it should say what you do and show in full.
- Action: Rewrite the homepage title to lead with what you offer (for example your food and city) instead of "Home", and shorten the Cinco de Mexico page title so it fits.

- [ ] supported by evidence   Notes: 

#### `keyword.meta_description` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.jajajamexicana.com/brunch) Meta description is 165 characters and may be cut off in search results. Aim for 70 to 160.
- [warn] (https://www.jajajamexicana.com/desserts) Meta description is 164 characters and may be cut off in search results. Aim for 70 to 160.

**AI wrote:**
- Explanation: The meta description (the short summary shown under your link in search results) is 165 characters on https://www.jajajamexicana.com/brunch and 164 characters on https://www.jajajamexicana.com/desserts, so it may be cut off.
- Why it matters: A cut-off summary can hide the part that convinces people to click.
- Action: Shorten the meta descriptions on the brunch and desserts pages to within the 70 to 160 character range the scanner suggests.

- [ ] supported by evidence   Notes: 

#### `keyword.duplicate_meta_descriptions` (fail, weight 2)

**Evidence (scanner):**
- [fail] 4 pages share the same meta description: https://www.jajajamexicana.com/about, https://www.jajajamexicana.com/cinco-de-email, https://www.jajajamexicana.com/cinco-de-mexico, https://www.jajajamexicana.com/gallery.

**AI wrote:**
- Explanation: 4 pages share the same meta description: https://www.jajajamexicana.com/about, https://www.jajajamexicana.com/cinco-de-email, https://www.jajajamexicana.com/cinco-de-mexico and https://www.jajajamexicana.com/gallery.
- Why it matters: Identical summaries make different pages look the same in search results and don't tell people what each page offers.
- Action: Write a unique meta description for each of those 4 pages that describes what that page is about.

- [ ] supported by evidence   Notes: 

#### `content.word_count` (fail/warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.jajajamexicana.com/) 167 words of text. Aim for at least 250 to explain what you offer.
- [fail] (https://www.jajajamexicana.com/about) Only 53 words of text. Pages with very little text rarely rank well.
- [warn] (https://www.jajajamexicana.com/brunch) 132 words of text. Aim for at least 250 to explain what you offer.
- [fail] (https://www.jajajamexicana.com/catering) Only 80 words of text. Pages with very little text rarely rank well.
- [warn] (https://www.jajajamexicana.com/cinco-de-email) 103 words of text. Aim for at least 250 to explain what you offer.
- [warn] (https://www.jajajamexicana.com/cinco-de-mexico) 156 words of text. Aim for at least 250 to explain what you offer.
- [fail] (https://www.jajajamexicana.com/contact) Only 97 words of text. Pages with very little text rarely rank well.
- [warn] (https://www.jajajamexicana.com/desserts) 109 words of text. Aim for at least 250 to explain what you offer.
- [fail] (https://www.jajajamexicana.com/events) Only 51 words of text. Pages with very little text rarely rank well.
- [fail] (https://www.jajajamexicana.com/gallery) Only 51 words of text. Pages with very little text rarely rank well.

**AI wrote:**
- Explanation: Many pages have very little text. Failing pages: https://www.jajajamexicana.com/about (53 words), https://www.jajajamexicana.com/catering (80), https://www.jajajamexicana.com/contact (97), https://www.jajajamexicana.com/events (51), https://www.jajajamexicana.com/gallery (51). Warnings: the homepage (167), /brunch (132), /cinco-de-email (103), /cinco-de-mexico (156) and /desserts (109).
- Why it matters: Pages with little text give visitors and search engines little to understand about what you offer.
- Action: Add a few short paragraphs to each page, starting with the pages that failed, describing your food, services, and what visitors can expect.

- [ ] supported by evidence   Notes: 

#### `content.readability` (fail/warn, weight 2)

**Evidence (scanner):**
- [warn] (https://www.jajajamexicana.com/) Reading ease score is 31 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.jajajamexicana.com/brunch) Reading ease score is 28 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.jajajamexicana.com/cinco-de-mexico) Reading ease score is 28 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.jajajamexicana.com/desserts) Reading ease score is 22 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.

**AI wrote:**
- Explanation: The text is hard to read on several pages. Reading ease scores (50 or more is easy) are 31 on the homepage, 28 on https://www.jajajamexicana.com/brunch, 28 on https://www.jajajamexicana.com/cinco-de-mexico and 22 on https://www.jajajamexicana.com/desserts.
- Why it matters: Hard-to-read text makes it harder for visitors to quickly understand what you offer.
- Action: Rewrite the text on these pages using shorter sentences and simpler words.

- [ ] supported by evidence   Notes: 

#### `local.phone` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.jajajamexicana.com/) Phone number found on https://www.jajajamexicana.com/contact but not on the homepage. Show it where visitors land.

**AI wrote:**
- Explanation: Your phone number appears on https://www.jajajamexicana.com/contact but not on the homepage.
- Why it matters: Customers who land on your homepage may not find an easy way to call you.
- Action: Add your phone number to the homepage header or footer.

- [ ] supported by evidence   Notes: 

#### `local.address_consistency` (warn, weight 1)

**Evidence (scanner):**
- [warn] 5 different addresss appear on the site: 63 Carmine St, New York, NY, 10014; 119 Kent Ave, Brooklyn, NY, 11249; 450 W 33rd Street, New York, NY, 10001; 2775 NW 3rd Ave, Miami, FL, 33127; 162 E Broadway, New York, NY, 10002. Use one consistent version unless you have several locations.

**AI wrote:**
- Explanation: 5 different addresses appear on the site: 63 Carmine St, New York; 119 Kent Ave, Brooklyn; 450 W 33rd Street, New York; 2775 NW 3rd Ave, Miami; and 162 E Broadway, New York.
- Why it matters: Mixed addresses can confuse customers unless each one is clearly a separate location.
- Action: If these are separate locations, label each one clearly; if not, use a single consistent address everywhere.

- [ ] supported by evidence   Notes: 

#### `local.map` (warn, weight 1)

**Evidence (scanner):**
- [warn] No map found. A map helps customers locate you.

**AI wrote:**
- Explanation: The scanner found no map on the site.
- Why it matters: A map helps customers find where you are.
- Action: Embed a Google Map on your contact page or location pages.

- [ ] supported by evidence   Notes: 

#### `local.directory_listings` (warn, weight 1)

**Evidence (scanner):**
- [warn] No links to local listing sites such as Yelp or Google Maps were found.

**AI wrote:**
- Explanation: No links to local listing sites such as Yelp or Google Maps were found.
- Why it matters: Links to these listings help customers find reviews and directions for you.
- Action: Add links to your Google Maps and Yelp listings in your footer or contact page.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (warn, weight 3)

**Evidence (scanner):**
- [warn] Google PageSpeed gives the homepage a mobile speed score of 86 out of 100 (room to speed up on mobile).

**AI wrote:**
- Explanation: Google PageSpeed gives the homepage a mobile speed score of 86 out of 100, so there is room to speed up on mobile.
- Why it matters: A faster site is nicer to use on a phone.
- Action: Ask your web person to compress large images and remove unneeded scripts on the homepage.

- [ ] supported by evidence   Notes: 

#### `technical.lcp` (warn, weight 2)

**Evidence (scanner):**
- [warn] The main content of the homepage takes 3.9 seconds to appear on mobile (needs improvement, good is 2.5 seconds or less).

**AI wrote:**
- Explanation: The main content of the homepage takes 3.9 seconds to appear on mobile; good is 2.5 seconds or less.
- Why it matters: Visitors on phones wait longer than they should to see your main content.
- Action: Shrink the biggest image or banner at the top of the homepage so it loads faster.

- [ ] supported by evidence   Notes: 

#### `credibility.social_profiles` (warn, weight 1)

**Evidence (scanner):**
- [warn] No links to social media profiles found. Active profiles show customers you are real.

**AI wrote:**
- Explanation: No links to social media profiles were found on the site.
- Why it matters: Social links show customers you are a real, active business.
- Action: Add links to your active social media accounts in the header or footer.

- [ ] supported by evidence   Notes: 

#### `credibility.reviews` (warn, weight 2)

**Evidence (scanner):**
- [warn] No customer reviews or testimonials found. Showing them builds trust.

**AI wrote:**
- Explanation: No customer reviews or testimonials were found on the site.
- Why it matters: Reviews build trust with people who are new to your restaurant.
- Action: Add a few real customer quotes or a reviews section to your homepage.

- [ ] supported by evidence   Notes: 

#### `credibility.privacy_policy` (warn, weight 1)

**Evidence (scanner):**
- [warn] No privacy policy or terms page found. It signals a trustworthy, professional site.

**AI wrote:**
- Explanation: No privacy policy or terms page was found.
- Why it matters: Having one makes your site look professional and trustworthy.
- Action: Create a simple privacy policy page and link it in your footer.

- [ ] supported by evidence   Notes: 

---
## 08-coletta
- URL: https://www.colettanyc.com/
- Overall score: **89**  |  technical seo 95, keyword optimization 99, content quality 72, local seo 86, credibility backlinks 86
- Pages scanned: 10  |  audit 15.1s, AI 28.2s  |  AI text used: True

### Top priorities (AI)

1. `technical.lcp` **Speed up how fast your homepage appears on mobile** - The main content takes 32.9 seconds to appear on mobile, far above the 2.5 second target.
   - [ ] supported by evidence
2. `technical.speed_score` **Improve the mobile speed score** - The homepage scores 55 out of 100 on mobile, and this check carries high weight.
   - [ ] supported by evidence
3. `content.readability` **Simplify your page text** - Hard-to-read text affects the homepage and nine other pages, and the homepage scored lowest at 7 out of 100.
   - [ ] supported by evidence

### Explanations

#### `technical.lcp` (fail, weight 2)

**Evidence (scanner):**
- [fail] The main content of the homepage takes 32.9 seconds to appear on mobile (slow, good is 2.5 seconds or less).

**AI wrote:**
- Explanation: The scanner found that the main content of your homepage takes 32.9 seconds to appear on mobile, and the target is 2.5 seconds or less.
- Why it matters: A page that takes this long to show anything useful can frustrate people on their phones before they see your menu or details.
- Action: Ask your web developer to compress the large images on the homepage and remove heavy scripts that load first.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (warn, weight 3)

**Evidence (scanner):**
- [warn] Google PageSpeed gives the homepage a mobile speed score of 55 out of 100 (room to speed up on mobile).

**AI wrote:**
- Explanation: Google PageSpeed gives the homepage a mobile speed score of 55 out of 100, which leaves room to speed up on mobile.
- Why it matters: A slow site is harder for people to use on their phones.
- Action: Ask your web developer to run the PageSpeed report and fix the top suggestions, starting with image sizes.

- [ ] supported by evidence   Notes: 

#### `content.readability` (fail/warn, weight 2)

**Evidence (scanner):**
- [fail] (https://www.colettanyc.com/) Reading ease score is 7 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.colettanyc.com/kombucha-bellini/) Reading ease score is 37 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.colettanyc.com/skin-contact-orange-wine/) Reading ease score is 38 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.colettanyc.com/rosemary-margarita/) Reading ease score is 37 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.colettanyc.com/white-negroni-recipe/) Reading ease score is 40 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.colettanyc.com/risotto-gluten-free/) Reading ease score is 38 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.colettanyc.com/rice-risotto-mushroom-recipe/) Reading ease score is 39 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.colettanyc.com/delicious-chardonnay/) Reading ease score is 37 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.colettanyc.com/guido-berta-moscato/) Reading ease score is 34 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.colettanyc.com/prosecco-treviso-brut/) Reading ease score is 38 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.

**AI wrote:**
- Explanation: The scanner found hard-to-read text on https://www.colettanyc.com/ (7 out of 100, where 50 or more is easy to read). It also flagged https://www.colettanyc.com/kombucha-bellini/ (37), https://www.colettanyc.com/skin-contact-orange-wine/ (38), https://www.colettanyc.com/rosemary-margarita/ (37), https://www.colettanyc.com/white-negroni-recipe/ (40), https://www.colettanyc.com/risotto-gluten-free/ (38), https://www.colettanyc.com/rice-risotto-mushroom-recipe/ (39), https://www.colettanyc.com/delicious-chardonnay/ (37), https://www.colettanyc.com/guido-berta-moscato/ (34) and https://www.colettanyc.com/prosecco-treviso-brut/ (38).
- Why it matters: Visitors are more likely to read and understand text that uses plain words and short sentences.
- Action: Start with the homepage and rewrite its text using shorter sentences and simpler words.

- [ ] supported by evidence   Notes: 

#### `keyword.h1` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.colettanyc.com/) Page has 2 H1 headings. Use one main heading per page.

**AI wrote:**
- Explanation: The homepage https://www.colettanyc.com/ has 2 H1 headings (main page titles), and the scanner recommends one per page.
- Why it matters: A single clear main heading tells visitors and search engines what the page is about.
- Action: Change one of the two H1 headings on the homepage to an H2 so only one main heading remains.

- [ ] supported by evidence   Notes: 

#### `content.heading_structure` (warn, weight 1)

**Evidence (scanner):**
- [warn] (https://www.colettanyc.com/) Headings skip from H1 to H3. Use headings in order so the page outline makes sense.
- [warn] (https://www.colettanyc.com/kombucha-bellini/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://www.colettanyc.com/skin-contact-orange-wine/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://www.colettanyc.com/rosemary-margarita/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://www.colettanyc.com/white-negroni-recipe/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://www.colettanyc.com/risotto-gluten-free/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://www.colettanyc.com/rice-risotto-mushroom-recipe/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://www.colettanyc.com/delicious-chardonnay/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://www.colettanyc.com/guido-berta-moscato/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.
- [warn] (https://www.colettanyc.com/prosecco-treviso-brut/) Headings skip from H2 to H4. Use headings in order so the page outline makes sense.

**AI wrote:**
- Explanation: Headings skip levels on https://www.colettanyc.com/ (H1 to H3) and on these pages, which skip from H2 to H4: https://www.colettanyc.com/kombucha-bellini/, https://www.colettanyc.com/skin-contact-orange-wine/, https://www.colettanyc.com/rosemary-margarita/, https://www.colettanyc.com/white-negroni-recipe/, https://www.colettanyc.com/risotto-gluten-free/, https://www.colettanyc.com/rice-risotto-mushroom-recipe/, https://www.colettanyc.com/delicious-chardonnay/, https://www.colettanyc.com/guido-berta-moscato/ and https://www.colettanyc.com/prosecco-treviso-brut/.
- Why it matters: Headings in order make the page outline easier to follow for readers and screen readers.
- Action: Edit the skipped headings so they follow in order (H1, H2, H3, H4), most likely in your page template.

- [ ] supported by evidence   Notes: 

#### `content.image_alt` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://www.colettanyc.com/) 1 of 35 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.colettanyc.com/kombucha-bellini/) 1 of 15 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.colettanyc.com/skin-contact-orange-wine/) 1 of 15 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.colettanyc.com/rosemary-margarita/) 1 of 14 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.colettanyc.com/white-negroni-recipe/) 1 of 14 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.colettanyc.com/risotto-gluten-free/) 1 of 14 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.colettanyc.com/rice-risotto-mushroom-recipe/) 1 of 14 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.colettanyc.com/delicious-chardonnay/) 1 of 15 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.colettanyc.com/guido-berta-moscato/) 1 of 15 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.colettanyc.com/prosecco-treviso-brut/) 1 of 15 images have no alt text, which describes them to search engines and screen readers.

**AI wrote:**
- Explanation: Each of these pages has one image with no alt text (a short description of the picture): https://www.colettanyc.com/ (1 of 35), https://www.colettanyc.com/kombucha-bellini/, https://www.colettanyc.com/skin-contact-orange-wine/, https://www.colettanyc.com/rosemary-margarita/, https://www.colettanyc.com/white-negroni-recipe/, https://www.colettanyc.com/risotto-gluten-free/, https://www.colettanyc.com/rice-risotto-mushroom-recipe/, https://www.colettanyc.com/delicious-chardonnay/, https://www.colettanyc.com/guido-berta-moscato/ and https://www.colettanyc.com/prosecco-treviso-brut/.
- Why it matters: Alt text helps visitors using screen readers and tells search engines what the image shows.
- Action: Add a short description to the one image missing alt text on each page.

- [ ] supported by evidence   Notes: 

#### `local.city_in_title` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://www.colettanyc.com/) Your structured data lists "New York" but it is not in the homepage title, description or main heading. Local searchers look for the city name.

**AI wrote:**
- Explanation: Your structured data lists New York, but the city is not in the homepage title, description or main heading at https://www.colettanyc.com/.
- Why it matters: People searching locally look for the city name.
- Action: Add New York to your homepage title and main heading.

- [ ] supported by evidence   Notes: 

#### `credibility.reviews` (warn, weight 2)

**Evidence (scanner):**
- [warn] No customer reviews or testimonials found. Showing them builds trust.

**AI wrote:**
- Explanation: The scanner found no customer reviews or testimonials on the site.
- Why it matters: Reviews help new customers trust your restaurant.
- Action: Add a section with a few real customer reviews to your homepage.

- [ ] supported by evidence   Notes: 

#### `local.directory_listings` (warn, weight 1)

**Evidence (scanner):**
- [warn] No links to local listing sites such as Yelp or Google Maps were found.

**AI wrote:**
- Explanation: No links to local listing sites such as Yelp or Google Maps were found.
- Why it matters: Links to your listings help customers find you and read about you elsewhere.
- Action: Add links to your Google Maps and Yelp listings in your site footer or contact page.

- [ ] supported by evidence   Notes: 

#### `local.address_consistency` (warn, weight 1)

**Evidence (scanner):**
- [warn] 2 different addresss appear on the site: 365 3rd Ave, New York, NY, 10016; 365 3rd Avenue, New York, NY 10016. Use one consistent version unless you have several locations.

**AI wrote:**
- Explanation: Two different versions of your address appear on the site: 365 3rd Ave, New York, NY, 10016 and 365 3rd Avenue, New York, NY 10016.
- Why it matters: A consistent address avoids confusion for customers and search engines.
- Action: Pick one version of the address and use it everywhere on your site.

- [ ] supported by evidence   Notes: 

#### `credibility.privacy_policy` (warn, weight 1)

**Evidence (scanner):**
- [warn] No privacy policy or terms page found. It signals a trustworthy, professional site.

**AI wrote:**
- Explanation: The scanner found no privacy policy or terms page.
- Why it matters: These pages signal a trustworthy, professional site.
- Action: Publish a simple privacy policy page and link it in your footer.

- [ ] supported by evidence   Notes: 

---
## 09-natural-blends
- URL: https://naturalblendcafe.com/
- Overall score: **88**  |  technical seo 75, keyword optimization 100, local seo 83, credibility backlinks 100
- Pages scanned: 1  |  audit 12.3s, AI 10.5s  |  AI text used: True

### Top priorities (AI)

1. `technical.lcp` **Speed up the main content on mobile** - The homepage's main content takes 16.0 seconds to appear on mobile, which is a failing result.
   - [ ] supported by evidence
2. `technical.sitemap` **Add an XML sitemap** - The scanner found no sitemap, which is a failing result and an easy fix.
   - [ ] supported by evidence
3. `technical.canonical` **Fix the canonical tag on your homepage** - It points to a different address, so search engines may ignore your homepage.
   - [ ] supported by evidence

### Explanations

#### `local.directory_listings` (warn, weight 1)

**Evidence (scanner):**
- [warn] No links to local listing sites such as Yelp or Google Maps were found.

**AI wrote:**
- Explanation: The scanner found no links to local listing sites such as Yelp or Google Maps.
- Why it matters: Links to your listings help people find your cafe's profiles and reviews from your website.
- Action: Add links to your Yelp and Google Maps listings in your website footer or on a contact section.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (warn, weight 3)

**Evidence (scanner):**
- [warn] Google PageSpeed gives the homepage a mobile speed score of 69 out of 100 (room to speed up on mobile).

**AI wrote:**
- Explanation: Google PageSpeed gives the homepage a mobile speed score of 69 out of 100, which leaves room to speed up on mobile.
- Why it matters: A faster site is easier for people on their phones to use.
- Action: Compress large images on your homepage and remove any scripts or widgets you do not need.

- [ ] supported by evidence   Notes: 

#### `technical.lcp` (fail, weight 2)

**Evidence (scanner):**
- [fail] The main content of the homepage takes 16.0 seconds to appear on mobile (slow, good is 2.5 seconds or less).

**AI wrote:**
- Explanation: The main content of the homepage takes 16.0 seconds to appear on mobile, while 2.5 seconds or less is considered good.
- Why it matters: A page that is this slow to show its main content can frustrate people on their phones.
- Action: Find the biggest item at the top of your homepage, usually a large photo, and shrink or compress it so it loads sooner.

- [ ] supported by evidence   Notes: 

#### `technical.sitemap` (fail, weight 2)

**Evidence (scanner):**
- [fail] No XML sitemap was found, so search engines have no list of your pages.

**AI wrote:**
- Explanation: The scanner found no XML sitemap, so search engines have no list of your pages.
- Why it matters: A sitemap helps search engines find all the pages on your site.
- Action: Generate a sitemap file with your website builder or a sitemap plugin and publish it on your site.

- [ ] supported by evidence   Notes: 

#### `technical.canonical` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://naturalblendcafe.com/) Canonical tag points to a different address: https://natural-blend-finder.lovable.app/. Search engines may ignore this page.

**AI wrote:**
- Explanation: On https://naturalblendcafe.com/ the canonical tag (a tag telling search engines which address is the main one) points to a different address: https://natural-blend-finder.lovable.app/. Search engines may ignore this page.
- Why it matters: Your real website address may be overlooked if the page tells search engines that another address is the main one.
- Action: Change the canonical tag on your homepage so it points to https://naturalblendcafe.com/.

- [ ] supported by evidence   Notes: 

#### `keyword.h1` (unavailable, weight 3)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The H1 heading could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The main heading (H1) on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `content.word_count` (unavailable, weight 3)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The amount of text could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The amount of text on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `content.image_alt` (unavailable, weight 2)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The images could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The images on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `content.internal_links` (unavailable, weight 1)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The internal links could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The internal links on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `local.phone` (unavailable, weight 3)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The phone number could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The phone number on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `local.address` (unavailable, weight 3)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The street address could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The street address on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `local.map` (unavailable, weight 1)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) A map could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: A map on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `credibility.contact_page` (unavailable, weight 2)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The contact page could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The contact page could not be checked from https://naturalblendcafe.com/ because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `credibility.about_page` (unavailable, weight 2)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The about page could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The about page could not be checked from https://naturalblendcafe.com/ because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `credibility.social_profiles` (unavailable, weight 1)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The social links could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The social links on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `credibility.reviews` (unavailable, weight 2)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The reviews could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The reviews on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

#### `credibility.privacy_policy` (unavailable, weight 1)

**Evidence (scanner):**
- [unavailable] (https://naturalblendcafe.com/) The privacy policy could not be checked because this page is built by JavaScript.

**AI wrote:**
- Explanation: The privacy policy on https://naturalblendcafe.com/ could not be checked because the page is built by JavaScript.

- [ ] supported by evidence   Notes: 

---
## 10-spicy-moon
- URL: https://www.spicymoonnyc.com/
- Overall score: **69**  |  technical seo 94, keyword optimization 59, content quality 59, local seo 64, credibility backlinks 68
- Pages scanned: 10  |  audit 11.8s, AI 17.2s  |  AI text used: True

### Top priorities (AI)

1. `keyword.h1` **Fix missing and multiple main headings** - It affects the most pages: 8 pages have no H1 and 2 have three, and each one carries high weight.
   - [ ] supported by evidence
2. `local.phone` **Add your phone number** - It's a high-weight finding and makes it easy for customers to contact you.
   - [ ] supported by evidence
3. `content.word_count` **Add a little more text to short pages** - It's a high-weight finding on 5 pages and needs only small additions.
   - [ ] supported by evidence

### Explanations

#### `keyword.h1` (fail/warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.spicymoonnyc.com/) Page has 3 H1 headings. Use one main heading per page.
- [warn] (https://www.spicymoonnyc.com/home) Page has 3 H1 headings. Use one main heading per page.
- [fail] (https://www.spicymoonnyc.com/contact) H1 heading is missing.
- [fail] (https://www.spicymoonnyc.com/privateevents) H1 heading is missing.
- [fail] (https://www.spicymoonnyc.com/cateringmenu) H1 heading is missing.
- [fail] (https://www.spicymoonnyc.com/event-calendar) H1 heading is missing.
- [fail] (https://www.spicymoonnyc.com/happy-hour) H1 heading is missing.
- [fail] (https://www.spicymoonnyc.com/west-village) H1 heading is missing.
- [fail] (https://www.spicymoonnyc.com/bowery) H1 heading is missing.
- [fail] (https://www.spicymoonnyc.com/craftbeer) H1 heading is missing.

**AI wrote:**
- Explanation: The main page heading (H1) is missing on https://www.spicymoonnyc.com/contact, /privateevents, /cateringmenu, /event-calendar, /happy-hour, /west-village, /bowery and /craftbeer. The pages https://www.spicymoonnyc.com/ and https://www.spicymoonnyc.com/home each have 3 H1 headings instead of one.
- Why it matters: The main heading tells visitors and search engines what each page is about, so missing or multiple ones make pages less clear.
- Action: Give each page exactly one H1 that states what the page is about, such as the location or service name, and change the extra H1s on the home pages to lower-level headings.

- [ ] supported by evidence   Notes: 

#### `keyword.meta_description` (fail/warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.spicymoonnyc.com/) Meta description is 164 characters and may be cut off in search results. Aim for 70 to 160.
- [warn] (https://www.spicymoonnyc.com/home) Meta description is 164 characters and may be cut off in search results. Aim for 70 to 160.
- [fail] (https://www.spicymoonnyc.com/event-calendar) Meta description tag is missing.
- [warn] (https://www.spicymoonnyc.com/happy-hour) Meta description is 162 characters and may be cut off in search results. Aim for 70 to 160.
- [warn] (https://www.spicymoonnyc.com/bowery) Meta description is 164 characters and may be cut off in search results. Aim for 70 to 160.

**AI wrote:**
- Explanation: The meta description (the short summary shown in search results) is missing on https://www.spicymoonnyc.com/event-calendar. It is flagged as too long and possibly cut off on https://www.spicymoonnyc.com/ (164 characters), /home (164), /happy-hour (162) and /bowery (164).
- Why it matters: A missing or cut-off summary can make your search listing less clear and less appealing to people deciding what to click.
- Action: Write a short summary for the event calendar page and trim the others to fit within the scanner's suggested 70 to 160 characters.

- [ ] supported by evidence   Notes: 

#### `keyword.title` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.spicymoonnyc.com/cateringmenu) Title is 70 characters and may be cut off in search results. Aim for 20 to 65.
- [warn] (https://www.spicymoonnyc.com/west-village) Title is 67 characters and may be cut off in search results. Aim for 20 to 65.

**AI wrote:**
- Explanation: The page title is too long and may be cut off in search results on https://www.spicymoonnyc.com/cateringmenu (70 characters) and https://www.spicymoonnyc.com/west-village (67 characters).
- Why it matters: A cut-off title can hide key words, such as your name or what you offer, from people browsing results.
- Action: Shorten both titles to within the scanner's suggested 20 to 65 characters, putting the most important words first.

- [ ] supported by evidence   Notes: 

#### `keyword.duplicate_titles` (fail, weight 2)

**Evidence (scanner):**
- [fail] 2 pages share the same title: https://www.spicymoonnyc.com/, https://www.spicymoonnyc.com/home.

**AI wrote:**
- Explanation: 2 pages share the same title: https://www.spicymoonnyc.com/ and https://www.spicymoonnyc.com/home.
- Why it matters: Identical titles make it hard for search engines and customers to tell the pages apart.
- Action: Give /home its own distinct title, or make the /home page redirect to the main homepage so only one version exists.

- [ ] supported by evidence   Notes: 

#### `keyword.duplicate_meta_descriptions` (fail, weight 2)

**Evidence (scanner):**
- [fail] 2 pages share the same meta description: https://www.spicymoonnyc.com/, https://www.spicymoonnyc.com/home.

**AI wrote:**
- Explanation: 2 pages share the same meta description: https://www.spicymoonnyc.com/ and https://www.spicymoonnyc.com/home.
- Why it matters: Repeated summaries make your listings look identical and don't help each page stand out.
- Action: Write a unique meta description for /home, or redirect /home to the main homepage.

- [ ] supported by evidence   Notes: 

#### `content.readability` (fail/warn, weight 2)

**Evidence (scanner):**
- [fail] (https://www.spicymoonnyc.com/) Reading ease score is -33 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.spicymoonnyc.com/home) Reading ease score is -20 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.spicymoonnyc.com/contact) Reading ease score is -77 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.spicymoonnyc.com/privateevents) Reading ease score is -46 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.spicymoonnyc.com/cateringmenu) Reading ease score is -80 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [warn] (https://www.spicymoonnyc.com/event-calendar) Reading ease score is 32 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.spicymoonnyc.com/happy-hour) Reading ease score is -81 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.spicymoonnyc.com/west-village) Reading ease score is -83 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.spicymoonnyc.com/bowery) Reading ease score is -83 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.
- [fail] (https://www.spicymoonnyc.com/craftbeer) Reading ease score is 17 out of 100 (50 or more is easy to read). Shorter sentences and simpler words would help.

**AI wrote:**
- Explanation: The text is hard to read on most scanned pages, including https://www.spicymoonnyc.com/ (-33), /home (-20), /contact (-77), /privateevents (-46), /cateringmenu (-80), /happy-hour (-81), /west-village (-83), /bowery (-83) and /craftbeer (17). /event-calendar scored 32. The scanner says 50 or more is easy to read.
- Why it matters: Long, complicated sentences make it harder for customers to quickly find what they need, like your menu or hours.
- Action: Rewrite the text on these pages using shorter sentences and simpler words, starting with the homepage.

- [ ] supported by evidence   Notes: 

#### `content.heading_structure` (warn, weight 1)

**Evidence (scanner):**
- [warn] (https://www.spicymoonnyc.com/) Headings skip from H1 to H3. Use headings in order so the page outline makes sense.
- [warn] (https://www.spicymoonnyc.com/home) Headings skip from H1 to H3. Use headings in order so the page outline makes sense.

**AI wrote:**
- Explanation: Headings skip from H1 to H3 on https://www.spicymoonnyc.com/ and https://www.spicymoonnyc.com/home.
- Why it matters: Headings in the right order make the page easier to follow for visitors and screen readers.
- Action: Change the H3 headings that follow the H1 to H2, or add an H2 between them.

- [ ] supported by evidence   Notes: 

#### `content.image_alt` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://www.spicymoonnyc.com/) 1 of 22 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.spicymoonnyc.com/home) 1 of 22 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.spicymoonnyc.com/contact) 1 of 5 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.spicymoonnyc.com/privateevents) 1 of 8 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.spicymoonnyc.com/cateringmenu) 1 of 6 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.spicymoonnyc.com/event-calendar) 1 of 7 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.spicymoonnyc.com/happy-hour) 1 of 6 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.spicymoonnyc.com/west-village) 1 of 6 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.spicymoonnyc.com/bowery) 1 of 6 images have no alt text, which describes them to search engines and screen readers.
- [warn] (https://www.spicymoonnyc.com/craftbeer) 1 of 8 images have no alt text, which describes them to search engines and screen readers.

**AI wrote:**
- Explanation: Each of these pages has 1 image with no alt text (a short description of the picture): https://www.spicymoonnyc.com/ (1 of 22), /home (1 of 22), /contact (1 of 5), /privateevents (1 of 8), /cateringmenu (1 of 6), /event-calendar (1 of 7), /happy-hour (1 of 6), /west-village (1 of 6), /bowery (1 of 6) and /craftbeer (1 of 8).
- Why it matters: Alt text helps people using screen readers and tells search engines what your photos show.
- Action: Add a short, plain description to the one image missing alt text on each of these pages.

- [ ] supported by evidence   Notes: 

#### `content.word_count` (warn, weight 3)

**Evidence (scanner):**
- [warn] (https://www.spicymoonnyc.com/contact) 233 words of text. Aim for at least 250 to explain what you offer.
- [warn] (https://www.spicymoonnyc.com/cateringmenu) 241 words of text. Aim for at least 250 to explain what you offer.
- [warn] (https://www.spicymoonnyc.com/happy-hour) 245 words of text. Aim for at least 250 to explain what you offer.
- [warn] (https://www.spicymoonnyc.com/west-village) 244 words of text. Aim for at least 250 to explain what you offer.
- [warn] (https://www.spicymoonnyc.com/bowery) 245 words of text. Aim for at least 250 to explain what you offer.

**AI wrote:**
- Explanation: Some pages have slightly less text than the scanner's suggested minimum of 250 words: https://www.spicymoonnyc.com/contact (233), /cateringmenu (241), /happy-hour (245), /west-village (244) and /bowery (245).
- Why it matters: A bit more text gives customers and search engines a clearer picture of what you offer.
- Action: Add a few more sentences to each of these pages about what you offer, such as dishes, hours or what makes the location special.

- [ ] supported by evidence   Notes: 

#### `local.phone` (fail, weight 3)

**Evidence (scanner):**
- [fail] No phone number found on the scanned pages. Customers and search engines look for it.

**AI wrote:**
- Explanation: No phone number was found on the scanned pages.
- Why it matters: Customers who want to book, ask about an event or check hours need an easy way to call you.
- Action: Add your phone number as text to the header or footer of every page.

- [ ] supported by evidence   Notes: 

#### `local.map` (warn, weight 1)

**Evidence (scanner):**
- [warn] No map found. A map helps customers locate you.

**AI wrote:**
- Explanation: No map was found on the scanned pages.
- Why it matters: A map helps customers find your locations quickly.
- Action: Embed a Google Map on your contact page and on each location page.

- [ ] supported by evidence   Notes: 

#### `local.directory_listings` (warn, weight 1)

**Evidence (scanner):**
- [warn] No links to local listing sites such as Yelp or Google Maps were found.

**AI wrote:**
- Explanation: No links to local listing sites such as Yelp or Google Maps were found.
- Why it matters: Links to your listings help customers find reviews and directions and show your business is real.
- Action: Add links to your Google Maps and Yelp listings in your footer or contact page.

- [ ] supported by evidence   Notes: 

#### `technical.speed_score` (warn, weight 3)

**Evidence (scanner):**
- [warn] Google PageSpeed gives the homepage a mobile speed score of 62 out of 100 (room to speed up on mobile).

**AI wrote:**
- Explanation: Google PageSpeed gives the homepage a mobile speed score of 62 out of 100, which leaves room to speed up on mobile.
- Why it matters: A slow site is frustrating for people browsing on their phones.
- Action: Compress the large images on your homepage and remove any scripts or widgets you don't need.

- [ ] supported by evidence   Notes: 

#### `technical.lcp` (fail, weight 2)

**Evidence (scanner):**
- [fail] The main content of the homepage takes 16.5 seconds to appear on mobile (slow, good is 2.5 seconds or less).

**AI wrote:**
- Explanation: The main content of the homepage takes 16.5 seconds to appear on mobile. The scanner says good is 2.5 seconds or less.
- Why it matters: Visitors on phones may leave before your homepage shows them anything useful.
- Action: Shrink or resize the biggest image or video at the top of the homepage so it loads faster.

- [ ] supported by evidence   Notes: 

#### `technical.canonical` (warn, weight 2)

**Evidence (scanner):**
- [warn] (https://www.spicymoonnyc.com/home) Canonical tag points to a different address: https://www.spicymoonnyc.com. Search engines may ignore this page.

**AI wrote:**
- Explanation: On https://www.spicymoonnyc.com/home, the canonical tag (which tells search engines the preferred version of a page) points to a different address: https://www.spicymoonnyc.com.
- Why it matters: Search engines may ignore this page in favor of the other address.
- Action: If /home is a duplicate of your homepage, redirect it to the main address; otherwise, set its canonical tag to point to itself.

- [ ] supported by evidence   Notes: 

#### `credibility.about_page` (fail, weight 2)

**Evidence (scanner):**
- [fail] No about page found among the scanned pages. Visitors look for one to trust a business.

**AI wrote:**
- Explanation: No about page was found among the scanned pages.
- Why it matters: Visitors like to know who is behind a restaurant before they trust it.
- Action: Create an About page telling your story, your food and your team, and link it in your main menu.

- [ ] supported by evidence   Notes: 

#### `credibility.reviews` (warn, weight 2)

**Evidence (scanner):**
- [warn] No customer reviews or testimonials found. Showing them builds trust.

**AI wrote:**
- Explanation: No customer reviews or testimonials were found on the scanned pages.
- Why it matters: Seeing what other customers say builds trust with new visitors.
- Action: Add a few real customer quotes or a review section to your homepage.

- [ ] supported by evidence   Notes: 

#### `credibility.privacy_policy` (warn, weight 1)

**Evidence (scanner):**
- [warn] No privacy policy or terms page found. It signals a trustworthy, professional site.

**AI wrote:**
- Explanation: No privacy policy or terms page was found.
- Why it matters: These pages make your site look professional and trustworthy.
- Action: Add a simple privacy policy and terms page and link them in your footer.

- [ ] supported by evidence   Notes: 
