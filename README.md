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
index.html          the whole site: content, styles and scripts in one file
photos/             images (.webp), videos (.mp4), logos and icons
netlify.toml        Netlify settings: what deploys, caching, security headers
.github/CODEOWNERS  makes Mitchell the required reviewer for main
```

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
3. **The free class form's class list.** Search for `id="cls"`. Each option is one class time.

The program cards (Little Ninjas, Youth, Adult) also list their days and times. Search for `class="times"`.

### Prices and purchase links

Search for `id="pricing"`. Each membership card has its price and a **Sign up** link that goes straight to that plan's checkout on doptraining.com. The Beginners Jiu Jitsu Program card (search `id="beginners"`) links to its Stripe checkout.

### Photos

- Put new images in `photos/` as `.webp`, about 1000px wide for cards and 1920px for full-width backgrounds. Keep each one under about 200 KB.
- Real gym photos only, no stock.
- When replacing a photo, keep the same file name so you don't have to edit `index.html`. Browsers may show the old one for up to a week, so if it needs to change right away, use a new file name and update the reference.

### Brand rules

- Colors: near-black and white with one red accent (`#f0544f`). Red is only for buttons, stars and small highlights.
- Fonts: Montserrat ExtraBold for headlines, Manrope for body text, Bebas Neue for prices, times and day names.
- Never use em dashes in site copy.
- The site has a light and a dark mode. Check both after design changes (moon/sun button in the header).

---

## Forms (needs setup before launch)

The site has three forms. Right now they only show a "thanks" message on screen. **They don't send the details anywhere yet.**

| Form | Where | Suggested tag |
|---|---|---|
| Free class | `id="trialForm"` | free trial |
| Private lesson request | `id="privateForm"` | private lesson |
| Rashguard backorder | `id="rashForm"` | rashguard backorder |

Each form's submit handler in the script at the bottom of `index.html` has a comment marking where to send the data, for example to the HighLevel webhook.

---

## Netlify settings (Mitchell)

These are set in the Netlify dashboard for the `costa-mesa-jiu-jitsu` project, under Project configuration → Build & deploy → Continuous deployment:

- **Repository:** `mitchelljfern/CostaMesaJiuJitsu`
- **Production branch:** `main`
- **Branch deploys:** "Let me add individual branches" → `staging`
- **Deploy previews:** "Don't deploy pull requests"
- **Build command:** empty. **Publish directory:** `.`
