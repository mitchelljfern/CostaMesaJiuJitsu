# Costa Mesa Jiu Jitsu website

The website for Costa Mesa Jiu Jitsu at Double Ops, 369 E 17th St, Suite 10, Costa Mesa, CA.

| | URL | Updates when |
|---|---|---|
| **Live site** | https://costa-mesa-jiu-jitsu.netlify.app | Mitchell merges a pull request into `main` |
| **Staging site** | https://staging--costa-mesa-jiu-jitsu.netlify.app | Anyone merges or pushes to `staging` |

> **The one rule:** never push to `main`. `main` is the live site and is locked. Do your work on `staging`. Mitchell reviews it there and decides when it goes live.

---

## How a change goes live

```
your branch ──► staging ──► (staging site, check it) ──► pull request into main ──► Mitchell approves + merges ──► live site
```

1. **Start from staging**
   ```bash
   git checkout staging
   git pull
   git checkout -b update-saturday-times     # name it after what you're changing
   ```
2. **Make your edit** (see "Common edits" below) and preview it locally.
3. **Push your branch and open a pull request into `staging`.** You can merge it yourself once it looks right.
   Your branch on its own does **not** build on Netlify. Only `staging` and `main` do.
4. **Check the staging site** on desktop and on your phone:
   https://staging--costa-mesa-jiu-jitsu.netlify.app
   (It updates about a minute after `staging` changes.)
5. **Open a pull request from `staging` into `main`** and tag @mitchelljfern.
   Use the checklist in the pull request template.
6. **Mitchell approves and merges.** That is the only way the live site changes.

### Why it's set up this way

- **Mitchell approves every live change.** `main` is protected on GitHub. Nobody can push to it directly, and every pull request into it needs Mitchell's approval (see `.github/CODEOWNERS`).
- **It saves Netlify build credits.** Netlify only builds `main` and `staging`. Every other branch and every pull request preview is skipped by the `ignore` rule in `netlify.toml`.
- **Batch your changes.** Each push to `staging` is one Netlify build, so group several edits into one push instead of pushing every small tweak.

---

## Preview on your own computer

There's no build step. It's one HTML file and a folder of photos.

```bash
# from the repo folder
python3 -m http.server 8000
# then open http://localhost:8000
```

Opening `index.html` straight from your file browser mostly works too, but the videos and fonts behave better through the little server above.

---

## What's in here

```
index.html               home page: content, styles and scripts in one file
free-trial/              /free-trial/ landing page (free class sign-up)
beginners-classes/       /beginners-classes/ landing page ($99 for 6 weeks)
pricing/                 /pricing/ memberships page
private-lessons/         /private-lessons/ request page
brady-fink/              /brady-fink/ Coach Brady Fink bio
upcoming-tournaments/    /upcoming-tournaments/ SoCal tournament cards (built from tools/tournaments.json)
privacy-policy/          privacy policy (wording copied exactly from the old site, do not edit)
terms-of-service/        SMS terms of service (wording copied exactly from the old site, do not edit)
assets/site.css          shared styles for the inner pages (a copy of the styles in index.html plus inner-page styles)
assets/pages.js          shared script for the inner pages (menu, theme, FAQ, forms, chat widget)
_redirects               every old WordPress URL forwarded to its new page or the home page (no 404s)
sitemap.xml, robots.txt  search engine files (robots.txt welcomes Google, Bing and the AI assistants by name)
llms.txt                 plain-English summary of the gym for AI assistants (ChatGPT, Claude, Perplexity, Gemini)
tools/                   page builder scripts and the tournament list (see "Updating tournaments")
photos/                  images (.webp), videos (.mp4), logos and icons
netlify.toml             Netlify settings: what deploys, caching, security headers
.github/CODEOWNERS       makes Mitchell the required reviewer for main
```

**Styles:** the home page keeps its styles inline for speed. Inner pages load `assets/site.css`. If you change a shared style (buttons, colors, header) in `index.html`, make the same change in `assets/site.css`.

**Header, footer and menu** are repeated in every page. If you change a nav link or footer link, update it in each page folder too.

---

## Common edits

Everything lives in `index.html`. Search the file for the text you want to change.

### Changing the schedule (three places)

A class time shows up in three spots. Update all three or they'll disagree:

1. **The weekly schedule cards.** Search for `id="week"`. Each day is a `<div class="day" data-day="...">` with one link per class:
   ```html
   <a class="cls t-adult" href="https://www.doptraining.com/book#" ...>
     <span class="cls-time">6:15 PM</span> ... Adult Jiu Jitsu ... NoGi
   </a>
   ```
   The color comes from the second class name:
   `t-ninja` purple (Little Ninjas), `t-youth` blue (Youth), `t-adult` red (Adult and Beginners), `t-strike` amber (BOXHIIT), `t-open` green (Open Mat).
2. **The "Next Class" box in the hero.** Search for `var SCHED`. One line per class:
   `[day, hour, minute, 'Name', 'Detail']`. Day: 0 is Sunday, 1 Monday, ... 6 Saturday. Hours are 24-hour (6:15 PM is `18,15`).
3. **The free class form's class list.** Search for `id="cls"`. Each option is one class time. The same list is also in `free-trial/index.html`, so update both.

The program cards (Little Ninjas, Youth, Adult) also list their days and times. Search for `class="times"`.

### Prices and purchase links

Search for `id="pricing"`. Each membership card has its price and a **Sign up** link that goes straight to that plan's checkout on doptraining.com. The Beginners Jiu Jitsu Program card (search `id="beginners"`) links to its Stripe checkout.

### Photos

- Put new images in `photos/` as `.webp`, about 1000px wide for cards and 1920px for full-width backgrounds. Keep each one under about 200 KB.
- Real gym photos only, no stock.
- When replacing a photo, keep the same file name so you don't have to edit `index.html`. Browsers may show the old one for up to a week, so if it needs to change right away, use a new file name and update the reference.

### Social sharing image and title

When someone shares the link (iMessage, Facebook, Instagram DMs, Google results), this is what shows:

- **Image:** `photos/og-share.jpg`, 1200 × 630 px. Keep the title and blurb inside the left half so nothing gets cropped.
- **Tags:** the `og:` and `twitter:` lines at the top of `index.html`, plus `<title>` and the meta description.
- **Changing the image:** use a **new file name** (for example `og-share-2.jpg`) and update all three image URLs in `index.html`. Facebook and iMessage cache the old image for weeks, and a new name forces a refresh.
- After it's live, paste the URL into https://developers.facebook.com/tools/debug/ and click **Scrape Again** to refresh Facebook's preview.

### SEO and redirects

- Every page has its own `<title>`, meta description, canonical URL, Open Graph tags and structured data (JSON-LD) in its `<head>`.
- Canonical URLs and `sitemap.xml` use `https://costamesajiujitsu.com`. Share previews (`og:url`, `og:image`) use `https://costa-mesa-jiu-jitsu.netlify.app` until the domain moves to Netlify.
- **When the domain moves:** find and replace `https://costa-mesa-jiu-jitsu.netlify.app` with `https://costamesajiujitsu.com` in every page, then submit `https://costamesajiujitsu.com/sitemap.xml` in Google Search Console.
- Google tag `GT-5TGJHX46` (same as the old site) is in every page's `<head>`.
- **Adding a new page:** create `new-page/index.html`, add it to `sitemap.xml`, and it will automatically take priority over the catch-all redirect.
- **`llms.txt` and `robots.txt` are generated** by `tools/build.py`. Edit `tools/llms.txt` (schedule, prices, links), then rebuild. Keep it in step with the site when the schedule or prices change.
- **Staging is hidden from Google.** Staging builds add an `X-Robots-Tag: noindex` header (see `[context.staging]` in `netlify.toml`). The live site never gets it.
- **Redirects** live in `_redirects`. Real pages always win over redirect rules, and the last rule sends any unknown URL to the home page.

### Updating tournaments

The tournament cards are built from `tools/tournaments.json`. Each event has its dates, venue, Gi/NoGi, divisions, price tiers (with "until" dates) and registration links.

1. Edit `tools/tournaments.json` (add, change or remove events).
2. Rebuild the page: `python3 tools/tournaments.py . /no-old-pages tools/tournaments.json YYYY-MM-DD` (use today's date; it shows as "Updated" on the page).
3. Check it locally, then push to `staging`.

Past events hide themselves automatically, and each card's price moves to the next tier on its own as deadlines pass. Prices and dates change, so re-check the organizations' sites every month or so.

### Coming back in January

- **Coach Brady privates:** set `BRADY_PRIVATES = True` in `tools/build.py` and rebuild (`python3 tools/build.py . /no-old-pages`). This adds him back to the private lessons page, the private lesson forms and his own page.
- **Waiver:** a ready-made online waiver is saved on the `waiver-draft` branch. Connect its form first (like the other forms), then merge it into `staging`.
- **Kickboxing and yoga:** add them back to the schedule, programs and FAQ when they return.

### Brand rules

- Colors: near-black and white with one red accent (`#f0544f`). Red is only for buttons, stars and small highlights.
- Fonts: Montserrat ExtraBold for headlines, Manrope for body text, Bebas Neue for prices, times and day names.
- Never use em dashes in site copy.
- The site has a light and a dark mode. Check both after design changes (moon/sun button in the header).

---

## Forms and leads

Every form (free class, kids class, private lessons, rashguard backorder) is captured two ways:

1. **HighLevel** (main): the HighLevel external tracking script at the bottom of every page turns each submission into a contact, with the page and UTM tags. Submissions show in HighLevel under Sites > Forms > Submissions > External Forms. Form IDs: `trialForm` (free class, including the kids page), `privateForm` (private lessons), `rashForm` (rashguard).
2. **Google Sheet backup**: each submission is also added as a row to the "CMJJ Website Leads (backup)" sheet through a Google Apps Script (`tools/google-sheet-backup.gs`, setup steps at the top of that file). The script's web app URL goes in `SHEET_BACKUP_URL` in two places: the script at the bottom of `index.html` and `pages_js` in `tools/build.py` (then rebuild). Leave it empty to switch the backup off.

Ad tags (utm_source and friends) are remembered for the whole visit, so a lead is credited to the right ad even if the visitor clicks around first.

## Netlify settings (Mitchell)

These are set in the Netlify dashboard for the `costa-mesa-jiu-jitsu` project, under Project configuration → Build & deploy → Continuous deployment:

- **Repository:** `mitchelljfern/CostaMesaJiuJitsu`
- **Production branch:** `main`
- **Branch deploys:** "Let me add individual branches" → `staging`
- **Deploy previews:** "Don't deploy pull requests"
- **Build command:** empty. **Publish directory:** `.`
