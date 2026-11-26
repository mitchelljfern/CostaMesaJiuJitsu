# Costa Mesa Jiu Jitsu website

> **2026 octopus brand (launched Nov 2026).** Costa Mesa Jiu Jitsu is its own gym at **2428 Newport Blvd, Unit 7, Costa Mesa, CA 92627** (no longer inside Double Ops).
> - Booking, memberships, payments and the member account all go to the El Dojo portal: https://eldojo.ossdojo.com/member (`BOOK` in `tools/build.py`).
> - Logo files, icons, favicons, share image and the brand kit zip live in `photos/brand/`; the brand guide is at `/brand-kit/` (noindex).
> - Tentacles: cutouts from the logo art (`photos/brand/tentacle-*.webp`) placed behind card groups with `.has-grip` + `<span class="grip g-...">`. The card sits on top so the cut end stays hidden. On the home page they move with the scroll (script at the bottom of `index.html`).
> - Share image source: `tools/brand/og-share.html` (screenshot it at 1200 × 630).

The website for Costa Mesa Jiu Jitsu, 2428 Newport Blvd, Unit 7, Costa Mesa, CA 92627.

| | URL | Updates when |
|---|---|---|
| **Live site** | https://costamesajiujitsu.com | Mitchell merges a pull request into `main` |
| **Staging site** | https://staging--costa-mesa-jiu-jitsu.netlify.app | Anyone merges or pushes to `staging` |

> **The one rule:** never push to `main`. `main` is the live site and is locked. Do your work on `staging`. Mitchell reviews it there and decides when it goes live.
>
> **Using an AI tool (Cursor, Claude, Grok, Copilot)?** It must read [`AGENTS.md`](AGENTS.md) first. That file is the full rulebook: where things live, what never to touch, and the check to run before every push. Cursor and Claude pick it up on their own. For any other tool, tell it: "Read AGENTS.md and follow it."

---

## How a change goes live

```
edit on staging ──► python3 tools/check.py ──► push to staging ──► check the staging site ──► pull request into main ──► Mitchell approves ──► live site
```

1. **Start from `staging`.** Either work on `staging` directly, or make a branch from it and open a pull request back into `staging` (you can merge that one yourself). AI tools that open their own pull requests must use `staging` as the base branch.
2. **Make your edit.** See "Common edits" below and the full rules in [`AGENTS.md`](AGENTS.md).
3. **Run the check:** `python3 tools/check.py`. It rebuilds the generated pages and looks for the common mistakes (a class time changed in one place but not another, a hand-edited generated page, a missing consent checkbox). Fix anything it reports.
4. **Push to `staging`** and look at the staging site on a computer and a phone:
   https://staging--costa-mesa-jiu-jitsu.netlify.app (updates about a minute after the push).
5. **Open a pull request from `staging` into `main`** and say in plain English what changed.
6. **Mitchell approves and merges.** That is the only way the live site changes.

### Simplest way, no tools needed

For a small text change you can edit right on github.com: switch the branch dropdown to `staging`, open the file, click the pencil, and commit to `staging`. Then tell Mitchell, because generated pages will need a rebuild before it goes live.

### Why it's set up this way

- **Mitchell approves every live change.** `main` is protected by a GitHub ruleset ("Protect main"). Nobody can push to it directly, and every pull request into it needs Mitchell's own approval as Code Owner (see `.github/CODEOWNERS`). Another collaborator's approval does not count.
- **It saves Netlify credits.** Each publish to the live site costs 15 credits. Staging builds are free. Netlify only builds `main` and `staging`; every other branch and every pull request preview is skipped by the `ignore` rule in `netlify.toml`.
- **Batch your changes.** Put a whole day's edits into one pull request into `main`, so they go live with one publish.

---

## Preview on your own computer

```bash
# from the repo folder
python3 tools/check.py          # rebuild the generated pages and run the checks
python3 -m http.server 8000     # then open http://localhost:8000
```

You only need Python 3. There is nothing to install.

---

## What's in here

**Edit these (source):**

```
index.html               home page, plus the shared header, footer, styles, forms and pricing cards every other page copies
tools/build.py           builds the inner pages, redirects, sitemap and robots.txt
tools/tournaments.json   the tournament list (tools/tournaments.py turns it into the page)
tools/llms.txt           plain-English summary of the gym for AI assistants
tools/legal-*.html       privacy policy and SMS terms wording
tools/check.py           rebuilds everything and checks for mistakes. Run before every push.
brand-kit/index.html     brand kit page (hand-written)
photos/                  images (.webp), videos (.mp4), logos and icons
AGENTS.md                the rulebook for AI tools and editors
```

**Do not edit these by hand (the build writes them):**

```
free-trial/  kids-jiu-jitsu/  pricing/  private-lessons/  brady-fink/
upcoming-tournaments/  privacy-policy/  terms-of-service/  waiver/
assets/site.css  assets/pages.js
_redirects  sitemap.xml  robots.txt  404.html  llms.txt
```

**Settings (ask Mitchell first):** `netlify.toml`, `.github/CODEOWNERS`, `.cursor/rules/`.

**Styles** live in the `<style>` block of `index.html`. The build copies them to `assets/site.css` for the inner pages, so change them in `index.html` only.

**Header, footer and menu** come from `index.html` and `tools/build.py`. Change them there and rebuild, and every page updates.

---

## Common edits

Search the source file for the text you want to change, edit it, then run `python3 tools/check.py`.

### Changing the schedule

A class time shows up in eight places. The full list, with what to search for, is in [`AGENTS.md`](AGENTS.md) under "Changing the schedule". `tools/check.py` compares them and tells you if any disagree.

The color of a schedule card comes from its second class name:
`t-ninja` purple (Little Ninjas), `t-youth` blue (Youth), `t-adult` red (Adult), `t-open` green (Open Mat).

### Prices and purchase links

A price shows up in four places: the pricing cards and the Google data in `index.html`, `tools/build.py`, and `tools/llms.txt`. See "Changing a price" in [`AGENTS.md`](AGENTS.md). Each membership card's **Sign up** link goes to the El Dojo member portal.

### Photos

- Put new images in `photos/` as `.webp`, about 1000px wide for cards and 1920px for full-width backgrounds. Keep each one under about 200 KB.
- Real gym photos only, no stock.
- When replacing a photo, keep the same file name so you don't have to edit `index.html`. Browsers may show the old one for up to a week, so if it needs to change right away, use a new file name and update the reference.

### Social sharing image and title

When someone shares the link (iMessage, Facebook, Instagram DMs, Google results), this is what shows:

- **Image:** `photos/brand/og-share-2026b.jpg`, 1200 × 630 px. Its source is `tools/brand/og-share.html` (open it in a browser at 1200 × 630 and screenshot it).
- **Tags:** the `og:` and `twitter:` lines at the top of `index.html`, plus `<title>` and the meta description.
- **Changing the image:** save it under a **new file name** and replace the old name everywhere it appears in `index.html`, `tools/build.py` and `brand-kit/index.html`, then rebuild. Facebook and iMessage cache the old image for weeks, and a new name forces a refresh.
- After it's live, paste the URL into https://developers.facebook.com/tools/debug/ and click **Scrape Again** to refresh Facebook's preview.

### SEO and redirects

- Every page has its own `<title>`, meta description, canonical URL, Open Graph tags and structured data (JSON-LD) in its `<head>`.
- Canonical URLs and `sitemap.xml` use `https://costamesajiujitsu.com`. Share previews (`og:url`, `og:image`) use it too.
- Google tag `GT-5TGJHX46` (same as the old site) is in every page's `<head>`.
- **Adding a new page:** ask Mitchell first. New pages are added in `tools/build.py` so they share the header, footer and styles.
- **`llms.txt` and `robots.txt` are generated** by `tools/build.py`. Edit `tools/llms.txt` (schedule, prices, links), then rebuild. Keep it in step with the site when the schedule or prices change.
- **Staging is hidden from Google.** Staging builds add an `X-Robots-Tag: noindex` header (see `[context.staging]` in `netlify.toml`). The live site never gets it.
- **Redirects** are written by `tools/build.py` into `_redirects`. Real pages always win over redirect rules, and the last rule sends any unknown URL to the home page.

### Updating tournaments

The tournament cards are built from `tools/tournaments.json`. Each event has its dates, venue, Gi/NoGi, divisions, price tiers (with "until" dates) and registration links.

1. Edit `tools/tournaments.json` (add, change or remove events).
2. If you re-checked the events against the organizers' sites, set `"checked"` at the top of the file to today's date (it shows as "Updated" on the page).
3. Rebuild and check: `python3 tools/check.py`.
4. Look at it locally, then push to `staging`.

Past events hide themselves automatically, and each card's price moves to the next tier on its own as deadlines pass. Prices and dates change, so re-check the organizations' sites every month or so.

### Coming back in January

- **Coach Brady privates:** set `BRADY_PRIVATES = True` in `tools/build.py` and rebuild. This adds him back to the private lessons page, the private lesson forms and his own page.
- **Kickboxing and yoga:** add them back to the schedule, programs and FAQ when they return.

### Removed, do not add back

- **The $99 Beginners Jiu Jitsu Program** (removed November 2026). Its old address redirects to the free trial page.

### Brand rules

- Colors, fonts, logos and icons are documented on the brand kit page, `/brand-kit/`. Use what is there.
- Never use em dashes in site copy.
- The address is always "2428 Newport Blvd, Unit 7, Costa Mesa, CA 92627".
- Real gym photos only, no stock.
- The site has a light and a dark mode. Check both after design changes (moon/sun button in the header).

---

## Forms and leads

**Text message consent (carrier requirement).** Every lead form that asks for a phone number has an unchecked, required consent checkbox at the bottom of the form, just above the submit button (`<label class="consent">`, field name `sms_consent`). The phone carriers review this wording, plus `/privacy-policy/` and `/terms-of-service/`, to approve the gym's texting number. Do not pre-check the box, make it optional, or reword it. The policy wording lives in `tools/legal-privacy.html` and `tools/legal-sms-terms.html` and matches the El Dojo portal pages (eldojo.ossdojo.com/privacy and /sms-terms); edit those files and rebuild, and keep the text messaging lines word for word.

Every form (free class, kids class, private lessons, rashguard backorder) is captured two ways:

1. **HighLevel** (main): the HighLevel external tracking script at the bottom of every page turns each submission into a contact, with the page and UTM tags. Submissions show in HighLevel under Sites > Forms > Submissions > External Forms. Form IDs: `trialForm` (free class, including the kids page), `privateForm` (private lessons), `rashForm` (rashguard).
2. **Google Sheet backup**: each submission is also checked for spam and added as a row to the "CMJJ Website Leads (backup)" sheet through a Google Apps Script (`tools/google-sheet-backup.gs`, setup steps at the top of that file). The script's web app URL goes in `SHEET_BACKUP_URL` in two places: the script at the bottom of `index.html` and `pages_js` in `tools/build.py` (then rebuild). Leave it empty to switch the backup off.

Ad tags (utm_source and friends) are remembered for the whole visit, so a lead is credited to the right ad even if the visitor clicks around first.

### Spam protection

`assets/lead-gate.js` (loaded on every page) checks each form before it reaches HighLevel:

- It catches the submit click first (HighLevel's tracker otherwise captures on the click itself), gets an **invisible Cloudflare Turnstile** token (no puzzle for visitors) and sends the lead to the Apps Script.
- The Apps Script verifies the token and scores the lead: a hidden trap field, how fast it was sent, no taps or clicks, random-letter names, dotted-up Gmail addresses, links in the form. A filled trap or failed Turnstile check is spam on its own; otherwise it takes two warning signs.
- Real leads go to the **Leads** tab and on to HighLevel. Spam goes to the **Spam** tab (with the reason) and never reaches HighLevel. Glance at the Spam tab now and then for anything real.
- If the check doesn't answer within 9 seconds, the lead goes through anyway, so nothing real is lost.

Keys: the Turnstile **site key** (public) goes in `TURNSTILE_SITEKEY` at the top of `assets/lead-gate.js`. The **secret key** goes only in the Apps Script, under Project Settings > Script Properties as `TURNSTILE_SECRET`.

Form tags need `data-lead="..."` (the label in the sheet) and `data-ok="..."` (the id of the thank-you box) for the check to apply.

Every real lead also sends a `generate_lead` event to Google Analytics (GA4 property G-9HM2039EZ2, through Google tag GT-5TGJHX46).

## Netlify settings (Mitchell)

These are set in the Netlify dashboard for the `costa-mesa-jiu-jitsu` project, under Project configuration → Build & deploy → Continuous deployment:

- **Repository:** `mitchelljfern/CostaMesaJiuJitsu`
- **Production branch:** `main`
- **Branch deploys:** "Let me add individual branches" → `staging`
- **Deploy previews:** "Don't deploy pull requests"
- **Build command:** empty. **Publish directory:** `.`
