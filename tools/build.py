#!/usr/bin/env python3
"""Builds the Costa Mesa Jiu Jitsu landing pages from shared parts.

Usage: python3 build.py <repo-dir> <old-pages-dir>
Writes: assets/site.css, assets/pages.js, the landing pages, terms-of-service,
privacy-policy (re-wrapped, wording untouched), _redirects, sitemap.xml, robots.txt.
"""
import html, json, os, re, sys

REPO, OLD = sys.argv[1], sys.argv[2]
SITE = 'https://costamesajiujitsu.com'            # canonical domain (search engines)
SHARE = 'https://costa-mesa-jiu-jitsu.netlify.app'  # share previews until DNS moves
TODAY = '2026-11-03'
GTAG = 'GT-5TGJHX46'
PHONE, PHONE_TEL, EMAIL = '949-556-1178', '+19495561178', 'info@costamesajiujitsu.com'
STRIPE_BEGINNERS = 'https://buy.stripe.com/14AeVc7cR1OzcwNcEU3Nm00'
PLAN = 'https://www.doptraining.com/book#/pricing/buy/r/823/loc/859?plan_type=plan&amp;id='
ALL_PLANS = 'https://www.doptraining.com/book#/pricing/r/823/loc/859?group=0'

index = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()

def w(path, text):
    full = os.path.join(REPO, path)
    os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
    open(full, 'w', encoding='utf-8').write(text)

# ---------------------------------------------------------------- shared CSS
css = index[index.index('<style>') + 7: index.index('</style>')]
css += '''
/* ===== Inner pages ===== */
.header.on-page { --hfg: var(--fg); }
.page-hero { padding-block: calc(env(safe-area-inset-top, 0px) + 112px) clamp(40px, 6vw, 72px); }
.page-hero .wrap { display: grid; gap: 28px; align-items: center; grid-template-columns: minmax(0, 1fr); }
.page-hero h1 em { font-style: normal; color: var(--accent); }
.page-hero .h1 { font-size: clamp(40px, 7.4vw, 80px); }
.page-hero-copy { display: grid; gap: 18px; justify-items: start; }
.page-hero-media { position: relative; border-radius: var(--radius-lg); overflow: hidden; background: var(--bg-raised); aspect-ratio: 4 / 3; max-width: 100%; }
.page-hero-media img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.page-hero .price-tag .display { font-size: 72px; }
.crumbs { font-size: 13px; color: var(--fg-muted); display: flex; gap: 8px; flex-wrap: wrap; }
.crumbs a { color: var(--fg-muted); text-decoration: none; }
.crumbs a:hover { color: var(--accent); }
@media (min-width: 900px) {
  .page-hero { padding-top: calc(env(safe-area-inset-top, 0px) + 148px); }
  .page-hero .wrap { max-width: 1240px; grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr); gap: clamp(40px, 5vw, 80px); }
  .page-hero-media { aspect-ratio: 4 / 5; }
  .page-hero-media.wide { aspect-ratio: 4 / 3; }
}
@media (max-width: 899px) {
  .page-hero-copy { justify-items: center; text-align: center; }
  .page-hero-copy .lead { margin-inline: auto; }
  .page-hero-copy .hero-actions { justify-self: stretch; justify-content: center; }
  .page-hero-copy .checks { text-align: left; }
  .crumbs { justify-content: center; }
}
.cards3 { display: grid; gap: 16px; grid-template-columns: minmax(0, 1fr); }
@media (min-width: 760px) { .cards3 { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
.info-card { background: var(--bg-card); border: 1px solid var(--line); border-radius: var(--radius-md); padding: 24px 22px; display: grid; gap: 10px; align-content: start; }
.info-card h3 { font-family: var(--font-display); font-weight: 800; text-transform: uppercase; font-size: 19px; line-height: 1.15; color: var(--fg); margin: 0; }
.info-card p { font-size: 15px; margin: 0; }
.info-card .num { font-family: var(--font-condensed); font-size: 40px; line-height: 1; color: var(--accent); }
@media (max-width: 899px) { .info-card { text-align: center; justify-items: center; } }
.split2 { display: grid; gap: 20px; grid-template-columns: minmax(0, 1fr); }
@media (min-width: 900px) { .split2 { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 28px; align-items: start; } }
.panel { background: var(--bg-card); border: 1px solid var(--line); border-radius: var(--radius-md); padding: 26px 24px; display: grid; gap: 14px; align-content: start; }
.panel h2, .panel h3 { margin: 0; }
@media (min-width: 760px) { .programs-2 { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; } }
.gallery { display: grid; gap: 12px; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.gallery img { width: 100%; height: 100%; aspect-ratio: 3 / 2; object-fit: cover; border-radius: var(--radius-md); display: block; max-width: 100%; }
@media (min-width: 760px) { .gallery { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
.bio { display: grid; gap: 16px; font-size: 17px; max-width: 68ch; }
.bio p { margin: 0; }
.cta-band { text-align: center; display: grid; gap: 16px; justify-items: center; }
.cta-band .hero-actions { justify-content: center; }
.coach-grid { display: grid; gap: 18px; grid-template-columns: minmax(0, 1fr); max-width: 1000px; margin-inline: auto; }
.coach-grid.one { max-width: 520px; grid-template-columns: minmax(0, 1fr) !important; }
@media (min-width: 760px) { .coach-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.coach-grid .coach { grid-template-columns: minmax(0, 1fr) !important; }
.coach-grid .coach-photo { aspect-ratio: 4 / 3; height: auto; position: relative; display: block; }
.coach-grid .coach-photo img { position: absolute; inset: 0; object-position: 50% 22%; }
.coach-grid .coach-body { text-align: left; justify-items: start; }
@media (max-width: 899px) { .coach-grid .coach-body { text-align: center; justify-items: center; } .coach-grid .coach-actions { justify-content: center; } }
.legal { max-width: 760px; }
.legal h1, .legal h3.lg { margin: 0 0 24px; font-family: var(--font-display); font-weight: 800; font-size: clamp(34px, 6vw, 52px); line-height: 1.05; text-transform: uppercase; color: var(--fg); }
.legal h2, .legal h5 { margin: 36px 0 12px; font-family: var(--font-display); font-weight: 800; font-size: 20px; line-height: 1.3; color: var(--fg); text-transform: none; letter-spacing: 0; }
.legal p { margin: 0 0 16px; }
.legal ul { margin: 0 0 16px; padding-left: 22px; }
.legal li { margin: 0 0 8px; }
.legal li::marker { color: var(--accent); }
.legal li p { margin: 0; }
.legal strong { color: var(--fg); font-weight: 700; }
.legal a { color: var(--accent); }
.legal-wrap { padding-block: calc(env(safe-area-inset-top, 0px) + 120px) 72px; }
@media (max-width: 899px) {
  .page-hero { padding-top: calc(env(safe-area-inset-top, 0px) + 168px); }
  .legal-wrap { padding-top: calc(env(safe-area-inset-top, 0px) + 176px); }
}
@media (min-width: 900px) { .legal-wrap { padding-top: calc(env(safe-area-inset-top, 0px) + 150px); } }
'''
w('assets/site.css', css)

# ---------------------------------------------------------------- shared JS
pages_js = r'''(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Google Sheet lead backup (tools/google-sheet-backup.gs). Runs alongside HighLevel. Leave the URL empty to switch off.
  var SHEET_BACKUP_URL = 'https://script.google.com/macros/s/AKfycbyZ0EI_Cq5wvFBlQ_vXDkqYB94jN8FJrmQJZ3XB3CKEXAgRZ8D8JnHimtU3FHQbKXPN/exec';
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  function adTags() {
    var q = new URLSearchParams(location.search), o = {}, any = UTM_KEYS.some(function (k) { return q.get(k); });
    if (any) { UTM_KEYS.forEach(function (k) { o[k] = q.get(k) || ''; }); try { sessionStorage.setItem('cmjj-utm', JSON.stringify(o)); } catch (e) {} return o; }
    try { return JSON.parse(sessionStorage.getItem('cmjj-utm') || '{}'); } catch (e) { return {}; }
  }
  adTags();
  function backupLead(form, label) {
    if (!SHEET_BACKUP_URL || !window.fetch) return;
    var d = new URLSearchParams(new FormData(form)), t = adTags();
    d.set('form', label); d.set('page', location.pathname); d.set('referrer', document.referrer || '');
    Object.keys(t).forEach(function (k) { d.set(k, t[k]); });
    try { fetch(SHEET_BACKUP_URL, { method: 'POST', mode: 'no-cors', body: d, keepalive: true }); } catch (e) {}
  }

  // Mobile menu
  var menu = $('#menu'), openBtn = $('#menuOpen'), closeBtn = $('#menuClose');
  if (menu && openBtn && closeBtn) {
    var openMenu = function () { menu.hidden = false; openBtn.setAttribute('aria-expanded', 'true'); document.body.style.overflow = 'hidden'; closeBtn.focus(); };
    var closeMenu = function () { menu.hidden = true; openBtn.setAttribute('aria-expanded', 'false'); document.body.style.overflow = ''; };
    openBtn.addEventListener('click', openMenu);
    closeBtn.addEventListener('click', function () { closeMenu(); openBtn.focus(); });
    $$('#menu a').forEach(function (a) { a.addEventListener('click', closeMenu); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) closeMenu(); });
  }

  // Header: big logo at the top, shrinks once you scroll
  var header = $('.header');
  function onScroll() { if (header) header.classList.toggle('scrolled', window.scrollY > 24); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // Light / dark toggle (dark is the default)
  var root = document.documentElement, meta = $('meta[name="theme-color"]');
  function applyMode(mode) {
    if (mode === 'light') root.setAttribute('data-mode', 'light'); else root.removeAttribute('data-mode');
    if (meta) meta.setAttribute('content', mode === 'light' ? '#f5f5f6' : '#111113');
    $$('[data-theme-toggle]').forEach(function (b) { b.setAttribute('aria-label', mode === 'light' ? 'Switch to dark mode' : 'Switch to light mode'); });
    try { localStorage.setItem('cmjj-mode', mode); } catch (e) {}
  }
  $$('[data-theme-toggle]').forEach(function (b) { b.addEventListener('click', function () { applyMode(root.getAttribute('data-mode') === 'light' ? 'dark' : 'light'); }); });
  applyMode(root.getAttribute('data-mode') === 'light' ? 'light' : 'dark');

  // FAQ: one open at a time, smooth height animation
  var faqs = $$('.faq details');
  function animateDetails(d, open) {
    var sum = $('summary', d), start = d.offsetHeight;
    if (reduce || !d.animate) { d.open = open; return; }
    d.open = true;
    var end = open ? d.scrollHeight : sum.offsetHeight;
    d.style.height = start + 'px';
    var anim = d.animate([{ height: start + 'px' }, { height: end + 'px' }], { duration: 320, easing: 'cubic-bezier(0.16, 1, 0.3, 1)' });
    anim.onfinish = function () { d.style.height = ''; d.open = open; };
    d.style.height = end + 'px';
  }
  faqs.forEach(function (d) {
    $('summary', d).addEventListener('click', function (e) {
      e.preventDefault();
      var willOpen = !d.open;
      faqs.forEach(function (o) { if (o !== d && o.open) animateDetails(o, false); });
      animateDetails(d, willOpen);
    });
  });

  // Free class form: filter class options by age group
  var age = $('#age'), cls = $('#cls');
  if (age && cls) age.addEventListener('change', function () {
    var opt = age.options[age.selectedIndex], g = opt ? opt.getAttribute('data-g') : '';
    $$('optgroup', cls).forEach(function (og) { og.hidden = g && og.getAttribute('data-group') !== g; og.disabled = og.hidden; });
    cls.value = '';
  });

  // Lead forms: validate, then confirm on screen.
  // HighLevel's tracking script captures each submission; backupLead also saves a row in the Google Sheet.
  $$('form[data-lead]').forEach(function (form) {
    var ok = $('#' + form.getAttribute('data-ok'));
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var bad = $$('[required]', form).filter(function (el) { return !el.value || (el.type === 'email' && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(el.value)); });
      bad.forEach(function (el) { el.style.borderColor = '#f0544f'; });
      if (bad.length) { bad[0].focus(); return; }
      var name = $('[name="name"]', form), phone = $('[name="phone"]', form);
      $$('[data-ok-name]', ok).forEach(function (s) { s.textContent = (name && name.value.trim().split(' ')[0]) || 'friend'; });
      $$('[data-ok-phone]', ok).forEach(function (s) { s.textContent = phone ? phone.value.trim() : ''; });
      $$('[data-ok-class]', ok).forEach(function (s) { s.textContent = cls ? cls.value : ''; });
      var lbl = form.getAttribute('data-lead') || 'form';
      if (location.pathname.indexOf('/kids-jiu-jitsu') === 0) lbl = 'kids free class';
      backupLead(form, lbl.charAt(0).toUpperCase() + lbl.slice(1));
      form.hidden = true; ok.hidden = false; ok.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    $$('[required]', form).forEach(function (el) { el.addEventListener('input', function () { el.style.borderColor = ''; }); el.addEventListener('change', function () { el.style.borderColor = ''; }); });
  });

  // Gentle reveal on scroll
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.remove('pre'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    $$('.reveal').forEach(function (el) { if (el.getBoundingClientRect().top > window.innerHeight) { el.classList.add('pre'); io.observe(el); } });
  }

  var y = $('#year'); if (y) y.textContent = new Date().getFullYear();

  // HighLevel (LeadConnector) chat widget, loaded after the page so it never slows the first screen
  function addChat() {
    var s = document.createElement('script');
    s.src = 'https://widgets.leadconnectorhq.com/loader.js';
    s.setAttribute('data-resources-url', 'https://widgets.leadconnectorhq.com/chat-widget/loader.js');
    s.setAttribute('data-widget-id', '6a555e3882c5a91e7f43987e');
    s.setAttribute('data-source', 'WEB_USER');
    document.body.appendChild(s);
    var tries = 0, timer = setInterval(function () {
      var wdg = document.querySelector('chat-widget');
      if (wdg && wdg.shadowRoot && wdg.shadowRoot.querySelector('.lc_text-widget')) {
        var st = document.createElement('style');
        st.textContent = '@media (max-width: 899px) { .lc_text-widget, .lc_text-widget--bubble { bottom: calc(16px + env(safe-area-inset-bottom, 0px)) !important; } }';
        wdg.shadowRoot.appendChild(st); clearInterval(timer);
      } else if (++tries > 80) { clearInterval(timer); }
    }, 250);
  }
  if (document.readyState === 'complete') setTimeout(addChat, 1200);
  else window.addEventListener('load', function () { setTimeout(addChat, 1200); });
})();
'''
w('assets/pages.js', pages_js)

# ---------------------------------------------------------------- shared HTML parts
def grab(start, end):
    a = index.index(start); b = index.index(end, a) + len(end); return index[a:b]

ICONS = {
    'ig': grab('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/>', '</svg>'),
}
header_socials = grab('<div class="header-socials">', '</div>')
theme_btn = grab('<button class="icon-btn theme-btn" type="button" data-theme-toggle', '</button>')
menu_socials = grab('<div class="menu-socials">', '</div>')
cta_svgs = re.findall(r'<a class="tab[^"]*" href="#[^"]+">(<svg.*?</svg>)', grab('<nav class="cta-bar"', '</nav>'), re.S)

NAV = [('Programs', '/#programs'), ('Beginners', '/beginners-classes/'), ('Schedule', '/#schedule'),
       ('Pricing', '/pricing/'), ('Kids', '/kids-jiu-jitsu/'), ('FAQ', '/#faq'), ('Contact', '/#contact')]

QUICK_TABS = [('tab tab-primary', '/free-trial/', 'Free class'), ('tab', '/#schedule', 'Schedule'),
              ('tab', '/pricing/', 'Pricing'), ('tab', '/beginners-classes/', 'Beginners')]

def quick_tabs(active_tab):
    return '\n'.join(f'    <a class="{c}{" active" if h == active_tab else ""}" href="{h}"{" aria-current=\"page\"" if h == active_tab else ""}>{cta_svgs[i]}{t}</a>' for i, (c, h, t) in enumerate(QUICK_TABS))

def header(active, active_tab=None):
    links = '\n'.join(f'      <a href="{h}"{" class=\"active\" aria-current=\"page\"" if h == active else ""}>{t}</a>' for t, h in NAV)
    return f'''<header class="header on-page">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Costa Mesa Jiu Jitsu home">
      <img src="/photos/cmjj-badge-sm.png" width="90" height="90" alt="Costa Mesa Jiu Jitsu badge">
      <span class="brand-name"><b>Costa Mesa</b><span>Jiu Jitsu</span></span>
    </a>
    <nav class="nav" aria-label="Main">
{links}
    </nav>
    <div class="header-tools">
      {header_socials}
      {theme_btn}
      <a class="btn btn-primary header-cta" href="/free-trial/">Try a free class</a>
      <button class="menu-btn" type="button" id="menuOpen" aria-expanded="false" aria-controls="menu">
      Menu
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
    </div>
  </div>
  <nav class="cta-bar" aria-label="Quick actions">
{quick_tabs(active_tab)}
  </nav>
</header>

<div class="menu" id="menu" hidden>
  <div class="menu-top">
    <span class="brand-name"><b>Costa Mesa</b><span>Jiu Jitsu</span></span>
    <div class="header-tools">
      {theme_btn}
      <button class="menu-close" type="button" id="menuClose">Close</button>
    </div>
  </div>
  <ul class="menu-list">
    <li><a href="/">Home <span>→</span></a></li>
    <li><a href="/#programs">Programs <span>→</span></a></li>
    <li><a href="/#schedule">Schedule <span>→</span></a></li>
    <li><a href="/pricing/">Pricing <span>→</span></a></li>
    <li><a href="/beginners-classes/">Beginners program <span>→</span></a></li>
    <li><a href="/kids-jiu-jitsu/">Kids jiu jitsu <span>→</span></a></li>
    <li><a href="/private-lessons/">Private lessons <span>→</span></a></li>
    <li><a href="/upcoming-tournaments/">Tournaments <span>→</span></a></li>
    <li><a href="/#shop">Shop <span>→</span></a></li>
    <li><a href="/#faq">FAQ <span>→</span></a></li>
    <li><a href="/#contact">Contact <span>→</span></a></li>
  </ul>
  <div class="menu-actions">
    <a class="btn btn-primary btn-block" href="/free-trial/">Try a free class</a>
    <a class="btn btn-outline btn-block" href="/pricing/">See memberships</a>
    <p class="menu-phone">Questions? Call or text <a href="tel:{PHONE_TEL}">{PHONE}</a></p>
    {menu_socials}
  </div>
</div>
'''

FOOTER_LINKS = [('Home', '/'), ('Free trial', '/free-trial/'), ('Beginners program', '/beginners-classes/'), ('Pricing', '/pricing/'),
                ('Kids jiu jitsu', '/kids-jiu-jitsu/'), ('Private lessons', '/private-lessons/'), ('Tournaments', '/upcoming-tournaments/'), ('Schedule', '/#schedule'),
                ('FAQ', '/#faq'), ('Double Ops', 'https://www.doptraining.com'), ('SMS terms', '/terms-of-service/'), ('Privacy', '/privacy-policy/')]

def footer_links_html():
    out = []
    for t, h in FOOTER_LINKS:
        ext = ' target="_blank" rel="noopener"' if h.startswith('http') else ''
        out.append(f'<a href="{h}"{ext}>{t}</a>')
    return ''.join(out)

def footer(active_tab=None):
    return f'''<footer class="footer">
  <div class="wrap">
    <div class="footer-brand">
      <img src="/photos/cmjj-badge-sm.png" width="56" height="56" alt="Costa Mesa Jiu Jitsu" loading="lazy">
      <span class="sep" aria-hidden="true"></span>
      <img class="only-dark" src="/photos/dop-wordmark-white.png" width="150" height="17" alt="Double Ops" loading="lazy"><img class="only-light" src="/photos/dop-wordmark-black.png" width="150" height="17" alt="Double Ops" loading="lazy">
    </div>
    <div class="footer-links">
      {footer_links_html()}
    </div>
    <p>© <span id="year">2026</span> Costa Mesa Jiu Jitsu at Double Ops. 369 E 17th St, Suite 10, Costa Mesa, CA 92627.</p>
  </div>
</footer>
'''

ORG = {"@type": "SportsActivityLocation", "@id": SITE + "/#gym", "name": "Costa Mesa Jiu Jitsu",
       "url": SITE + "/", "telephone": "+1-949-556-1178", "email": EMAIL,
       "image": SHARE + "/photos/og-share.jpg",
       "address": {"@type": "PostalAddress", "streetAddress": "369 E 17th St, Suite 10", "addressLocality": "Costa Mesa",
                   "addressRegion": "CA", "postalCode": "92627", "addressCountry": "US"}}

def crumbs_ld(name, path):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": SITE + path}]}

def faq_ld(qas):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in qas]}

def head(title, desc, path, og_title=None, og_desc=None, image='/photos/og-share.jpg', ld=None, og_type='website', noindex=False):
    og_title = og_title or title; og_desc = og_desc or desc
    e = html.escape
    graph = {"@context": "https://schema.org", "@graph": ld or []}
    ld_html = f'<script type="application/ld+json">\n{json.dumps(graph, indent=1, ensure_ascii=False)}\n</script>' if ld else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
{'<meta name="robots" content="noindex, follow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'}
<meta name="theme-color" content="#111113">
<meta name="color-scheme" content="dark">
<link rel="icon" href="/photos/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/photos/apple-touch-icon.png">

<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Costa Mesa Jiu Jitsu">
<meta property="og:title" content="{e(og_title)}">
<meta property="og:description" content="{e(og_desc)}">
<meta property="og:url" content="{SHARE}{path}">
<meta property="og:image" content="{SHARE}{image}">
<meta property="og:image:secure_url" content="{SHARE}{image}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(og_title)}">
<meta name="twitter:description" content="{e(og_desc)}">
<meta name="twitter:image" content="{SHARE}{image}">

<!-- Google tag (same tag as the old site) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GTAG}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GTAG}');</script>
{ld_html}
<script>(function(){{try{{var m=localStorage.getItem("cmjj-mode");if(m==="light")document.documentElement.setAttribute("data-mode","light");}}catch(e){{}}}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Manrope:wght@500;600;700;800&family=Montserrat:wght@800&display=swap">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="sr-only" href="#main">Skip to content</a>
'''

HL_TRACKING = '''<!-- HighLevel external tracking: captures site form submissions as HighLevel contacts -->
<script src="https://link.msgsndr.com/js/external-tracking.js" data-tracking-id="tk_87a0beae75e04bf7aa983cbee612d188"></script>
'''

def page(title, desc, path, body, active_nav=None, active_tab=None, **kw):
    return head(title, desc, path, **kw) + header(active_nav, active_tab) + f'\n<main id="main">\n{body}\n</main>\n\n' + footer(active_tab) + '\n<script src="/assets/pages.js" defer></script>\n' + HL_TRACKING + '</body>\n</html>\n'

def faq_html(qas, first_open=True):
    items = ''.join(f'      <details{" open" if (i == 0 and first_open) else ""}><summary>{q}</summary><div class="answer">{a}</div></details>\n' for i, (q, a) in enumerate(qas))
    return f'    <div class="faq">\n{items}    </div>'

def crumbs(name):
    return f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">{name}</span></nav>'

def checks(items):
    return '<ul class="checks">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

# ---------------------------------------------------------------- reusable forms
trial_form = grab('<form class="form" id="trialForm" novalidate>', '</form>')
trial_form = trial_form.replace('<form class="form" id="trialForm" novalidate>', '<form class="form" id="trialForm" novalidate data-lead="free trial" data-ok="formOk">')
trial_ok = '''<div class="form-ok" id="formOk" hidden>
        <p class="kicker">You're in</p>
        <p class="display">See you on the mat</p>
        <p>Thanks, <span data-ok-name>friend</span>. We'll text <span data-ok-phone></span> shortly to confirm <span data-ok-class></span>. Show up 10 minutes early and wear something comfortable with no zippers.</p>
        <p class="form-fine">Questions before then? Call or text 949-556-1178.</p>
      </div>'''

# Coach Brady is back in January 2027: set this to True to add him back to private lessons.
BRADY_PRIVATES = False

def private_form(coach=None):
    f = grab('<form class="form" id="privateForm" novalidate>', '</form>')
    f = f.replace('<form class="form" id="privateForm" novalidate>', '<form class="form" id="privateForm" novalidate data-lead="private lesson" data-ok="privateOk">')
    sel = lambda c: ' selected' if coach == c else ''
    coach_field = f'''<div class="field">
          <label for="pCoach">Preferred coach</label>
          <select id="pCoach" name="coach">
            <option value="No preference"{sel(None)}>No preference</option>
            <option{sel("Coach Tony Misitano")}>Coach Tony Misitano</option>
            <option{sel("Coach Brady Fink")}>Coach Brady Fink</option>
          </select>
        </div>
        <div class="field">
          <label for="pGoal">'''
    if BRADY_PRIVATES:
        f = f.replace('<div class="field">\n          <label for="pGoal">', coach_field, 1)
        f = f.replace('No payment now. Coach Tony will text you to set it up.', 'No payment now. A coach will text you to set it up. Pricing varies by coach.')
    return f
private_ok = f'''<div class="form-ok" id="privateOk" hidden>
        <p class="kicker">Request sent</p>
        <p class="display">Talk soon</p>
        <p>Thanks, <span data-ok-name>friend</span>. {'A coach' if BRADY_PRIVATES else 'Coach Tony'} will text <span data-ok-phone></span> to find a time that works.</p>
        <p class="form-fine">Questions before then? Call or text 949-556-1178.</p>
      </div>'''

mat_bg = '<div class="mat-bg" aria-hidden="true"><picture><source media="(max-width: 767px)" srcset="/photos/mats-tall.webp"><img src="/photos/mats-wide.webp" width="1920" height="1440" alt="" loading="lazy" decoding="async"></picture></div>'

# ================================================================ /free-trial/
ft_faq = [
    ("Is the free class really free?", "Yes. One class, any program, no card required and no pressure to join. The only thing it does not cover is the beginners jiu jitsu program, which is its own $99 program."),
    ("Do I need any experience?", "No. Most of our students started with zero experience, and the coaches walk you through everything. If you want a slower on-ramp, the <a href=\"/beginners-classes/\">beginners jiu jitsu program</a> is built exactly for that."),
    ("What should I wear?", "Athletic clothes with no zippers, buttons or pockets. A rash guard and shorts work great. Bring a water bottle."),
    ("How old do kids need to be?", "Little Ninjas starts at age 4. Youth Jiu Jitsu is ages 7 to 12. Teens 13 and up train in the adult classes."),
    ("Where are you?", "Inside Double Ops at 369 E 17th St, Suite 10, Costa Mesa, in the Triangle Square area, with parking right outside."),
]
ft_body = f'''<section class="page-hero">
  <div class="wrap">
    <div class="page-hero-copy">
      {crumbs('Free trial')}
      <p class="kicker">Free trial<span class="tiny-star" aria-hidden="true">★</span>Costa Mesa, CA</p>
      <h1 class="display h1">Your first class is <em>free</em></h1>
      <p class="lead">Whether you're a beginner, an experienced practitioner, or someone seeking a fun way to stay active, our gym offers options for everyone.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#book">Book my free class</a>
        <a class="btn btn-outline" href="/#schedule">See the schedule</a>
      </div>
      <p class="kicker">No card<span class="tiny-star" aria-hidden="true">★</span>No contract<span class="tiny-star" aria-hidden="true">★</span>Kids and adults</p>
    </div>
    <div class="page-hero-media"><img src="/photos/hero-tall.webp" width="900" height="1125" alt="Adults training NoGi jiu jitsu at Double Ops in Costa Mesa" fetchpriority="high" decoding="async"></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="cards3">
      <div class="info-card reveal"><span class="num">01</span><h3>Small class sizes</h3><p>Get more one-on-one attention from coaches in a focused, supportive learning environment where you're never just a number.</p></div>
      <div class="info-card reveal"><span class="num">02</span><h3>Risk-free trial</h3><p>Try any class for free. No pressure, no contracts, just a chance to experience what makes our community so special.</p></div>
      <div class="info-card reveal"><span class="num">03</span><h3>Family-friendly culture</h3><p>Our gym is built on a welcoming, ego-free atmosphere where parents, kids, and adults of all skill levels train and grow together.</p></div>
    </div>
  </div>
</section>

<section class="section form-band mat-band" id="book">
  {mat_bg}
  <div class="wrap">
    <div class="form-grid">
      <div class="form-side">
        <p class="kicker">Free trial sign up</p>
        <h2 class="display h2">Pick your class</h2>
        <p class="lead">Show up 10 minutes early and we will take it from there.</p>
        {checks(["Any program, kids or adults", "Small classes, so coaches actually know your name", "Gear available in adult and kid sizes if you need it", "Parents welcome to watch from the mat edge"])}
        <p class="form-fine">The free trial is not valid for the beginners program. Prefer to talk to a person? Call or text <a href="tel:{PHONE_TEL}" style="color:var(--fg)">{PHONE}</a>.</p>
      </div>
      {trial_form}
      {trial_ok}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head center"><p class="kicker">Questions</p><h2 class="display h2">Good to know</h2></div>
{faq_html(ft_faq)}
  </div>
</section>'''
w('free-trial/index.html', page(
    'Free Jiu Jitsu Class in Costa Mesa | Costa Mesa Jiu Jitsu',
    'Try your first jiu jitsu class free at Costa Mesa Jiu Jitsu inside Double Ops. Kids from age 4 and adults, Gi and NoGi. No experience, no card, no contract.',
    '/free-trial/', ft_body, active_tab='/free-trial/',
    og_title='Your First Jiu Jitsu Class Is Free | Costa Mesa Jiu Jitsu',
    ld=[ORG, crumbs_ld('Free trial', '/free-trial/'), faq_ld(ft_faq)]))

# ================================================================ /beginners-classes/
bg_faq = [
    ("Do I need any experience to join?", "None. That's the whole point. Everyone in this program is starting on day one with you, so nobody is ahead of you and nobody is watching you struggle. If you've never touched a mat before, you're exactly who this was built for."),
    ("Is $99 the total price?", "Yes, $99 covers the full 6 weeks. No signup fee, no contract, no auto-renew."),
    ("When does the program start?", "Any week. It's an ongoing program, so you can join on any Tuesday. Your 6 weeks start at your first class."),
    ("Will I be sparring or rolling live right away?", "No. Your first classes are movement, position, and safety. Live rolling can be introduced later and is totally optional, only when you're ready for it. You will never get thrown into something you haven't been taught."),
    ("What happens when the 6 weeks are done?", "You'll have a real foundation and a decision to make. Most people roll into a regular membership and keep training with the same crew they started with. There's no obligation and no pressure."),
    ("What if I miss a class?", "Life happens. We'll get you caught up at the next class. Your 6 weeks keep running from your first class, so missed classes can't be saved or added on at the end."),
    ("I'm out of shape. Should I get in better shape first?", "No. Waiting until you're in shape to start is how people never start. The program is built for beginners and you go at your own pace. Jiu jitsu is what gets you in shape, not the other way around."),
    ("Who's teaching the program?", "Anthony Misitano, a black belt with more than a decade of experience on the mats. He's coached hundreds of people through their first classes. This isn't a class handed off to an assistant."),
    ("What does a class actually look like?", "Warm up, technique of the day, drilling with a partner, then positional work. Every class builds on the last one so nothing comes out of nowhere. Classes are 60 minutes."),
]
bg_body = f'''<section class="page-hero">
  <div class="wrap">
    <div class="page-hero-copy">
      {crumbs('Beginners program')}
      <p class="kicker">Tuesdays at 6:15 PM<span class="tiny-star" aria-hidden="true">★</span>Join any week</p>
      <h1 class="display h1">Beginners <em>Jiu Jitsu</em> Program</h1>
      <div class="price-tag"><span class="display">$99</span><small>for 6 weeks</small></div>
      <p class="lead">Build a real foundation with step-by-step basics and a black belt coach. Join any week: your 6 weeks start at your first class.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="{STRIPE_BEGINNERS}" target="_blank" rel="noopener">Reserve my spot</a>
        <a class="btn btn-outline" href="#faq">Read the FAQ</a>
      </div>
      <p class="kicker">No sign-up fee<span class="tiny-star" aria-hidden="true">★</span>No contract<span class="tiny-star" aria-hidden="true">★</span>No auto-renew</p>
    </div>
    <div class="page-hero-media"><img src="/photos/beginners-tall.webp" width="900" height="1200" alt="Coach demonstrating a jiu jitsu control position to beginners" fetchpriority="high" decoding="async"></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="split2">
      <div class="panel reveal">
        <p class="kicker">What you get</p>
        <h2 class="display h3">Built for true beginners</h2>
        {checks(["Clear path into regular classes after the program", "No experience needed, built for true beginners", "Learn positions that actually matter (guard, mount, back, side control)", "Escape first so you don't feel stuck or panicked", "Simple submissions and how to finish them safely", "How to stay safe while training (tapping, posture, injury prevention)"])}
      </div>
      <div class="panel reveal">
        <p class="kicker">The details</p>
        <h2 class="display h3">When, where and what to wear</h2>
        <div class="times"><div><b>Tuesday</b><span>6:15 PM</span></div></div>
        <p>You train in our beginner-friendly Tuesday NoGi class inside Double Ops, 369 E 17th St, Suite 10, Costa Mesa. Taught by Coach Tony Misitano, BJJ black belt.</p>
        <p><b style="color:var(--fg)">How it works:</b> it's an ongoing program, so you can join any week. Your 6 weeks start at your first class. It's not a class pack, so classes can't be skipped or saved for later.</p>
        <p style="margin:0;color:var(--fg)"><b>Please wear proper NoGi attire:</b></p>
        {checks(["Rash guard", "Athletic shorts with no zippers or pockets", "Optional: spats", "Bring a water bottle"])}
        <a class="btn btn-primary" href="{STRIPE_BEGINNERS}" target="_blank" rel="noopener">Reserve my spot for $99</a>
        <p class="form-fine">Not part of the free trial. Questions? Text <a href="sms:{PHONE_TEL}">{PHONE}</a>.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section-dark mat-band faq-band" id="faq">
  <div class="mat-bg" aria-hidden="true"><picture><source media="(max-width: 767px)" srcset="/photos/faq-tall.webp"><img src="/photos/faq-wide.webp" width="1920" height="1440" alt="" loading="lazy" decoding="async"></picture></div>
  <div class="wrap">
    <div class="section-head center"><p class="kicker">Frequently asked questions</p><h2 class="display h2">Good to know</h2></div>
{faq_html(bg_faq)}
  </div>
</section>

<section class="section">
  <div class="wrap cta-band">
    <p class="kicker">6 weeks<span class="tiny-star" aria-hidden="true">★</span>$99<span class="tiny-star" aria-hidden="true">★</span>Join any week</p>
    <h2 class="display h2">Start from zero, the right way</h2>
    <div class="hero-actions">
      <a class="btn btn-primary" href="{STRIPE_BEGINNERS}" target="_blank" rel="noopener">Reserve my spot</a>
      <a class="btn btn-outline" href="/free-trial/">Try a regular class free</a>
    </div>
  </div>
</section>'''
w('beginners-classes/index.html', page(
    'Beginners Jiu Jitsu Program in Costa Mesa | 6 Weeks for $99',
    'New to jiu jitsu? Our beginners program is 6 weeks for $99, Tuesdays at 6:15 PM in Costa Mesa, CA. Join any week. No experience needed, no contract.',
    '/beginners-classes/', bg_body, active_nav='/beginners-classes/', active_tab='/beginners-classes/',
    ld=[ORG, crumbs_ld('Beginners program', '/beginners-classes/'), faq_ld(bg_faq),
        {"@type": "Course", "name": "Beginners Jiu Jitsu Program", "description": "6-week beginner jiu jitsu program, Tuesdays at 6:15 PM in the beginner-friendly NoGi class, taught by a black belt coach. Join any week; your 6 weeks start at your first class.",
         "provider": {"@id": SITE + "/#gym"},
         "offers": {"@type": "Offer", "price": "99", "priceCurrency": "USD", "category": "Paid", "url": SITE + "/beginners-classes/"},
         "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Onsite", "location": {"@id": SITE + "/#gym"}, "courseSchedule": {"@type": "Schedule", "repeatFrequency": "P1W", "byDay": "https://schema.org/Tuesday", "startTime": "18:15", "duration": "PT1H", "repeatCount": 6}}}]))

# ================================================================ /pricing/
pricing_sec = grab('<div class="plans">', '<p class="plans-all">')[:-len('<p class="plans-all">')]
pricing_sec = pricing_sec.replace('href="#free-class"', 'href="/free-trial/"')
pr_faq = [
    ("Are there contracts?", "No long-term contracts. Memberships are monthly, the 10-class pack is a one-time purchase, and the beginners program is a one-time $99 for 6 weeks."),
    ("Is there a sign-up fee?", "No. You pay for the membership or pack you choose, and that's it."),
    ("Can I try a class before I buy?", "Yes. Your first class is free, any program, kids or adults. <a href=\"/free-trial/\">Book your free class</a>."),
    ("How does the Family Add-On work?", "Add a second family member to any unlimited membership for $120 a month. Call or text 949-556-1178 or email info@costamesajiujitsu.com to set it up."),
    ("How much are private lessons?", "<a href=\"/private-lessons/\">Send a quick request</a> and Coach Tony will walk you through pricing and options before anything is booked."),
]
pr_body = f'''<section class="page-hero">
  <div class="wrap" style="grid-template-columns:minmax(0,1fr)">
    <div class="page-hero-copy">
      {crumbs('Pricing')}
      <p class="kicker">Memberships<span class="tiny-star" aria-hidden="true">★</span>No long-term contracts</p>
      <h1 class="display h1">Simple <em>pricing</em></h1>
      <p class="lead">Costa Mesa Jiu Jitsu membership options. Train unlimited, add a family member, or grab a class pack. Your first class is always free.</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap">
    {pricing_sec}
    <div class="split2" style="margin-top:20px">
      <div class="panel reveal">
        <span class="plan-for">New to jiu jitsu</span>
        <div class="plan-name">Beginners Jiu Jitsu Program</div>
        <div class="plan-price"><b>$99</b><span>for 6 weeks</span></div>
        <p>Tuesdays at 6:15 PM with a black belt coach. Join any week. No sign-up fee, no contract.</p>
        <div class="hero-actions"><a class="btn btn-primary" href="{STRIPE_BEGINNERS}" target="_blank" rel="noopener">Sign up</a><a class="btn btn-ghost" href="/beginners-classes/">Learn more</a></div>
      </div>
      <div class="panel reveal">
        <span class="plan-for">1-on-1</span>
        <div class="plan-name">Private Lessons</div>
        <div class="plan-price"><b style="font-size:40px">1-on-1</b><span>with Coach Tony</span></div>
        <p>Kids and adults, any level, built around your goals.</p>
        <div class="hero-actions"><a class="btn btn-primary" href="/private-lessons/">Request a private lesson</a></div>
      </div>
    </div>
    <p class="plans-all"><a class="link" href="{ALL_PLANS}" target="_blank" rel="noopener">See all memberships, including Double Ops classes →</a></p>
  </div>
</section>

<section class="section section-dark">
  <div class="wrap">
    <div class="section-head center"><p class="kicker">Questions</p><h2 class="display h2">Good to know</h2></div>
{faq_html(pr_faq)}
  </div>
</section>'''
offers = [("Unlimited Adult Jiu Jitsu", "195", "month"), ("Unlimited Kids Jiu Jitsu", "195", "month"), ("Family Add-On", "120", "month"),
          ("10-Class Pack", "260", None), ("Beginners Jiu Jitsu Program (6 weeks)", "99", None)]
w('pricing/index.html', page(
    'Jiu Jitsu Membership Pricing | Costa Mesa Jiu Jitsu',
    'Unlimited adult or kids jiu jitsu for $195/month, family add-on $120, 10-class pack $260 and a $99 beginners program. No contracts. Costa Mesa, CA.',
    '/pricing/', pr_body, active_nav='/pricing/', active_tab='/pricing/',
    ld=[ORG, crumbs_ld('Pricing', '/pricing/'), faq_ld(pr_faq),
        {"@type": "OfferCatalog", "name": "Costa Mesa Jiu Jitsu memberships", "itemListElement": [
            dict({"@type": "Offer", "name": n, "price": p, "priceCurrency": "USD", "seller": {"@id": SITE + "/#gym"}},
                 **({"priceSpecification": {"@type": "UnitPriceSpecification", "price": p, "priceCurrency": "USD", "unitText": u}} if u else {}))
            for n, p, u in offers]}]))

# ================================================================ /private-lessons/
BRADY_CARD = r'''      <div class="coach reveal">
        <div class="coach-photo"><img src="/photos/brady-coaching.webp" width="900" height="1125" alt="Coach Brady Fink teaching a clinch position" loading="lazy" decoding="async"></div>
        <div class="coach-body">
          <p class="kicker">Black belt</p>
          <h3>Brady Fink</h3>
          <p>BJJ black belt with more than two decades in jiu jitsu and MMA, and a coach to top fighters including former UFC Middleweight Champion Michael Bisping.</p>
          <div class="coach-actions"><a class="btn btn-primary btn-sm" href="#request" data-coach="Coach Brady Fink">Request Brady</a><a class="link" href="/brady-fink/">Full bio →</a></div>
        </div>
'''
BRADY_FORM = r'''<section class="section form-band" id="request">
  <div class="wrap">
    <div class="form-grid">
      <div class="form-side">
        <p class="kicker">Interested in a private lesson?</p>
        <h2 class="display h2">Train with Brady</h2>
        <p class="lead">Tell us a little about what you want to work on and Brady will reach out to find a time. Pricing varies by coach.</p>
        <p class="form-fine">Rather talk now? Call or text <a href="tel:+19495561178">949-556-1178</a>.</p>
      </div>
      '''+private_form("Coach Brady Fink")+r'''
      '''+private_ok+r'''
    </div>
  </div>
</section>'''
BRADY_CTA = r'''<section class="section form-band">
  <div class="wrap cta-band">
    <p class="kicker">Train at Costa Mesa Jiu Jitsu</p>
    <h2 class="display h2">Your first class is free</h2>
    <p class="lead" style="margin-inline:auto">Kids and adults, Gi and NoGi, with black belt coaching inside Double Ops in Costa Mesa.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="/free-trial/">Book my free class</a>
      <a class="btn btn-outline" href="/#schedule">See the schedule</a>
    </div>
  </div>
</section>'''
pl_faq = [
    ("How much are private lessons?", "Send a request and Coach Tony will walk you through pricing and options before anything is booked."),
    ("Who are private lessons for?", "Kids and adults at any level, from nervous first-timers who want a head start to competitors fixing a specific position."),
    ("Can I bring a friend or family member?", "Yes. Lessons can be solo, with a friend, or as a family."),
    ("Where are lessons held?", "On the mats inside Double Ops at 369 E 17th St, Suite 10, Costa Mesa."),
]
pl_body = f'''<section class="page-hero">
  <div class="wrap">
    <div class="page-hero-copy">
      {crumbs('Private lessons')}
      <p class="kicker">Private lessons<span class="tiny-star" aria-hidden="true">★</span>Kids and adults</p>
      <h1 class="display h1">Train <em>1-on-1</em></h1>
      <p class="lead">The fastest way to get better. Tell us a little about what you want to work on, and Coach Tony will reach out to find a time and walk you through options.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#request">Request a private lesson</a>
        <a class="btn btn-outline" href="#team">Meet Coach Tony</a>
      </div>
    </div>
    <div class="page-hero-media"><img src="/photos/g-coaching.webp" width="800" height="800" alt="Coach teaching a kids jiu jitsu technique one-on-one" fetchpriority="high" decoding="async"></div>
  </div>
</section>

<section class="section section-dark" id="team">
  <div class="wrap">
    <div class="section-head center"><p class="kicker">{"Black belt coaches" if BRADY_PRIVATES else "Your coach"}</p><h2 class="display h2">{"Choose your coach" if BRADY_PRIVATES else "Coach Tony Misitano"}</h2></div>
    <div class="coach-grid{"" if BRADY_PRIVATES else " one"}">
      <div class="coach reveal">
        <div class="coach-photo"><img src="/photos/coach-tony.webp" width="640" height="640" alt="Coach Tony Misitano smiling in a black gi" loading="lazy" decoding="async"></div>
        <div class="coach-body">
          <p class="kicker">Head coach</p>
          <h3>Tony Misitano</h3>
          <p>BJJ black belt and IBJJF medalist. Tony started at Carlson Gracie Team Chicago and has competed at the highest level since 2018. He leads the beginners program and has coached hundreds of first-timers, kids and adults alike.</p>
          <div class="coach-actions"><a class="btn btn-primary btn-sm" href="#request" data-coach="Coach Tony Misitano">Request a lesson with Tony</a></div>
        </div>
      </div>
{BRADY_CARD if BRADY_PRIVATES else ''}      </div>
    </div>
  </div>
</section>

<section class="section form-band" id="request">
  <div class="wrap">
    <div class="form-grid">
      <div class="form-side">
        <p class="kicker">Request a lesson</p>
        <h2 class="display h2">Tell us what you want to work on</h2>
        {checks(["Kids and adults, any level", "Built around your goals, from self-defense to competition", "Great for nervous beginners who want a head start", "Solo, with a friend, or as a family"])}
        <p class="form-fine">Rather talk now? Call or text <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
      </div>
      {private_form()}
      {private_ok}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head center"><p class="kicker">Questions</p><h2 class="display h2">Good to know</h2></div>
{faq_html(pl_faq)}
  </div>
</section>
<script>document.addEventListener('click',function(e){{var a=e.target.closest('[data-coach]');if(!a)return;var s=document.getElementById('pCoach');if(s)s.value=a.getAttribute('data-coach');}});</script>'''
w('private-lessons/index.html', page(
    'Private Jiu Jitsu Lessons in Costa Mesa | Costa Mesa Jiu Jitsu',
    '1-on-1 jiu jitsu lessons for kids and adults with black belt Coach Tony Misitano in Costa Mesa, CA. Self-defense, competition prep or a head start.',
    '/private-lessons/', pl_body,
    ld=[ORG, crumbs_ld('Private lessons', '/private-lessons/'), faq_ld(pl_faq)]))

# ================================================================ /brady-fink/
bf_body = f'''<section class="page-hero">
  <div class="wrap">
    <div class="page-hero-copy">
      {crumbs('Coach Brady Fink')}
      <p class="kicker">Brazilian Jiu Jitsu black belt<span class="tiny-star" aria-hidden="true">★</span>MMA coach</p>
      <h1 class="display h1">Coach <em>Brady Fink</em></h1>
      <p class="lead">Brady Fink is a Brazilian Jiu Jitsu Black Belt &amp; Martial Artist with over two decades of experience in competing in Brazilian Jiu Jitsu, MMA, and coaching at the highest levels of the sport.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="{'#request' if BRADY_PRIVATES else '/free-trial/'}">{'Book a private with Brady' if BRADY_PRIVATES else 'Try a class free'}</a>
        <a class="btn btn-outline" href="{'/free-trial/' if BRADY_PRIVATES else '/#schedule'}">{'Try a class free' if BRADY_PRIVATES else 'See the schedule'}</a>
      </div>
    </div>
    <div class="page-hero-media"><img src="/photos/brady-coaching.webp" width="900" height="1125" alt="Coach Brady Fink teaching a clinch position at Costa Mesa Jiu Jitsu" fetchpriority="high" decoding="async"></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="split2">
      <div class="bio reveal">
        <p class="kicker">About Brady</p>
        <p>Brady combines his technical expertise with years of experience training elite fighters, making him a sought-after mentor in the martial arts world.</p>
        <p>Brady has played a pivotal role in the careers of some of the top fighters globally, including former UFC Middleweight Champion Michael Bisping. His deep understanding of MMA striking, grappling, and strategy has helped fighters excel in the Octagon and beyond.</p>
        <p>With a proven history of guiding both champions and everyday practitioners, Brady's coaching provides an inspiring and supportive environment for anyone looking to grow in martial arts.</p>
      </div>
      <div class="panel reveal">
        <p class="kicker">At a glance</p>
        {checks(["Brazilian Jiu Jitsu black belt", "20+ years competing in BJJ and MMA", "Coached former UFC Middleweight Champion Michael Bisping"] + (["Private lessons for kids and adults, any level"] if BRADY_PRIVATES else []))}
        <a class="btn btn-primary" href="{'#request' if BRADY_PRIVATES else '/free-trial/'}">{'Request a private lesson' if BRADY_PRIVATES else 'Try a class free'}</a>
      </div>
    </div>
    <div class="gallery" style="margin-top:28px">
      <img class="reveal" src="/photos/brady-seminar.webp" width="1000" height="667" alt="Coach Brady Fink with the coaching team in front of a kids class" loading="lazy" decoding="async">
      <img class="reveal" src="/photos/brady-mats.webp" width="1000" height="667" alt="Coach Brady Fink demonstrating a guard position on the mats" loading="lazy" decoding="async">
      <img class="reveal" src="/photos/brady-class.webp" width="1000" height="667" alt="Coach Brady Fink leading an adult NoGi class" loading="lazy" decoding="async">
    </div>
  </div>
</section>

{BRADY_FORM if BRADY_PRIVATES else BRADY_CTA}'''
w('brady-fink/index.html', page(
    'Coach Brady Fink | BJJ Black Belt | Costa Mesa Jiu Jitsu',
    'Brady Fink is a Brazilian Jiu Jitsu black belt with 20+ years in BJJ and MMA who has coached fighters including former UFC champion Michael Bisping.',
    '/brady-fink/', bf_body, og_type='profile', image='/photos/brady-coaching-wide.webp',
    ld=[ORG, crumbs_ld('Coach Brady Fink', '/brady-fink/'),
        {"@type": "Person", "name": "Brady Fink", "jobTitle": "Brazilian Jiu Jitsu Black Belt Coach", "worksFor": {"@id": SITE + "/#gym"},
         "image": SHARE + "/photos/brady-coaching.webp", "url": SITE + "/brady-fink/"}]))

# ================================================================ /kids-jiu-jitsu/
kid_cards = index[index.index('<a class="program reveal" href="#free-class">'):]
kid_cards = kid_cards[:kid_cards.index('<a class="program reveal" href="#free-class">', kid_cards.index('Youth Jiu Jitsu</h3>'))].strip()
kid_cards = kid_cards.replace('href="#free-class"', 'href="#book"').replace('src="photos/', 'src="/photos/')
reasons = grab('<div class="reasons"', '</div>\n    </div>\n  </div>\n</section>')
reasons = reasons[:reasons.rindex('</div>\n  </div>\n</section>')]
kid_form = trial_form.replace('<option value="Adult (13+)" data-g="adult">An adult (13+)</option>\n', '')
kid_form = kid_form[:kid_form.index('<optgroup label="Adults"')] + kid_form[kid_form.index('<optgroup label="Youth, ages 7 to 12"'):]
kid_form = kid_form.replace('<label for="age">Who is the class for?</label>', '<label for="age">How old is your child?</label>')
kids_faq = [
    ("How old do kids need to be?", "Little Ninjas starts at age 4 and runs through 6. Youth Jiu Jitsu is ages 7 to 12. Teens 13 and up train in the adult classes."),
    ("What should my child wear?", "Athletic clothes with no zippers, buttons or pockets, and a water bottle. Gi classes use a kimono, which we sell in kid sizes, but athletic clothes are fine for the free class."),
    ("Can parents watch?", "Yes. Parents are welcome to watch from the edge of the mat."),
    ("Is jiu jitsu safe for kids?", "Jiu jitsu is a grappling art, so there is no striking in our kids classes. Kids learn to tap, keep good posture and protect their training partners from day one, with coaches watching every pairing."),
    ("How often should my child train?", "Two or three classes a week is a great pace for most kids. The Unlimited Kids membership covers up to four days a week."),
    ("Do kids have to compete?", "No. Competing is totally optional. Kids who want to can train for local tournaments, and we post upcoming events on our <a href=\"/upcoming-tournaments/\">tournaments page</a>."),
    ("Do you work with homeschool families?", "Yes. We partner with iLEAD, Sage Oak and Cabrillo Point Academy, so homeschool families can often use approved education funds for classes."),
    ("How much does it cost?", "The first class is free. Unlimited Kids is $195 a month, and you can add a second family member for $120 a month. No long-term contracts."),
]
kids_body = f'''<section class="page-hero">
  <div class="wrap">
    <div class="page-hero-copy">
      {crumbs('Kids jiu jitsu')}
      <p class="kicker">Ages 4 to 12<span class="tiny-star" aria-hidden="true">★</span>Costa Mesa, CA</p>
      <h1 class="display h1">Kids <em>Jiu Jitsu</em></h1>
      <p class="lead">Confidence that lasts longer than a trophy. Our kids program is built around three things: staying safe, staying calm, and treating people well.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#book">Book a free kids class</a>
        <a class="btn btn-outline" href="#programs">See class times</a>
      </div>
      <p class="kicker">First class free<span class="tiny-star" aria-hidden="true">★</span>No contracts<span class="tiny-star" aria-hidden="true">★</span>Parents welcome to watch</p>
    </div>
    <div class="page-hero-media"><img src="/photos/g-highfive.webp" width="800" height="800" alt="Two kids in white gis high-fiving at Costa Mesa Jiu Jitsu" fetchpriority="high" decoding="async"></div>
  </div>
</section>

<section class="section" id="programs" style="padding-top:0">
  <div class="wrap">
    <div class="section-head"><p class="kicker">Two programs by age</p><h2 class="display h2">Find the right class</h2></div>
    <div class="programs programs-2">
      {kid_cards}
    </div>
  </div>
</section>

<section class="section section-dark">
  <div class="wrap">
    <div class="section-head"><p class="kicker">For parents</p><h2 class="display h2">What your kid gets out of it</h2></div>
    {reasons}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><p class="kicker">Kids memberships</p><h2 class="display h2">Simple pricing</h2></div>
    <div class="split2">
      <div class="panel reveal">
        <span class="plan-for">Kids</span>
        <div class="plan-name">Unlimited Kids</div>
        <div class="plan-price"><b>$195</b><span>/ month</span></div>
        <p>Unlimited Little Ninjas or Youth Jiu Jitsu classes, up to four days a week.</p>
        <div class="hero-actions"><a class="btn btn-primary" href="{PLAN}35614" target="_blank" rel="noopener">Sign up</a><a class="btn btn-ghost" href="#book">Try a class free</a></div>
      </div>
      <div class="panel reveal">
        <span class="plan-for">Families</span>
        <div class="plan-name">Family Add-On</div>
        <div class="plan-price"><b>$120</b><span>/ month</span></div>
        <p>Add a sibling or a parent to any unlimited membership and train together.</p>
        <div class="hero-actions"><a class="btn btn-ghost" href="tel:{PHONE_TEL}">Call to add</a></div>
        <p class="form-fine" style="margin:0">{PHONE} or <a href="mailto:{EMAIL}">email us</a></p>
      </div>
    </div>
  </div>
</section>

<section class="section form-band mat-band" id="book">
  {mat_bg}
  <div class="wrap">
    <div class="form-grid">
      <div class="form-side">
        <p class="kicker">Free kids class</p>
        <h2 class="display h2">Your child's first class is on us</h2>
        <p class="lead">Pick a class, show up 10 minutes early, and we will take it from there. No card, no contract, no pressure.</p>
        {checks(["Little Ninjas (4 to 6) and Youth (7 to 12)", "Small classes, so coaches actually know your kid's name", "Kids gear available if you need it", "Parents welcome to watch from the mat edge"])}
        <p class="form-fine">Prefer to talk to a person? Call or text <a href="tel:{PHONE_TEL}" style="color:var(--fg)">{PHONE}</a>.</p>
      </div>
      {kid_form}
      {trial_ok}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head center"><p class="kicker">Parents ask</p><h2 class="display h2">Good to know</h2></div>
{faq_html(kids_faq)}
  </div>
</section>'''
w('kids-jiu-jitsu/index.html', page(
    'Kids Jiu Jitsu in Costa Mesa | Ages 4 to 12 | Free Class',
    'Kids jiu jitsu in Costa Mesa for ages 4 to 12. Little Ninjas and Youth classes build confidence, focus and bully-proof skills. Your first class is free.',
    '/kids-jiu-jitsu/', kids_body, active_nav='/kids-jiu-jitsu/',
    og_title='Kids Jiu Jitsu in Costa Mesa | First Class Free',
    ld=[ORG, crumbs_ld('Kids jiu jitsu', '/kids-jiu-jitsu/'), faq_ld(kids_faq),
        {"@type": "Service", "name": "Kids Jiu Jitsu Classes", "serviceType": "Kids Brazilian Jiu Jitsu classes", "provider": {"@id": SITE + "/#gym"},
         "areaServed": "Costa Mesa, CA", "audience": {"@type": "PeopleAudience", "suggestedMinAge": 4, "suggestedMaxAge": 12},
         "offers": [{"@type": "Offer", "name": "Free trial class", "price": "0", "priceCurrency": "USD"},
                    {"@type": "Offer", "name": "Unlimited Kids Jiu Jitsu", "price": "195", "priceCurrency": "USD"}]}]))

# ================================================================ legal pages (wording copied exactly)
def legal_block(fn, start_pat, end_pat):
    s = open(os.path.join(OLD, fn), encoding='utf-8').read(); b = s.find('<body')
    a = s.find(start_pat, b); e = s.find(end_pat, a) + len(end_pat)
    blk = s[a:e]
    blk = re.sub(r'\s+data-(start|end)="\d+"', '', blk); blk = re.sub(r'\s+class="(isSelectedEnd)?"', '', blk)
    blk = re.sub(r'<p>[\s ]*</p>\n?', '', blk)
    blk = blk.replace('<h3 class="wp-block-heading">', '<h3 class="lg">').replace('<br data-start="3605" data-end="3608" />', '<br />')
    return blk

if os.path.isdir(OLD):   # legal pages are copied word for word from the old site's saved HTML; skipped if it isn't available
    pp_block = legal_block('privacy_policy.html', '<h3 class="wp-block-heading"', '949-556-1178</a></p>')
    tos_block = legal_block('terms_of_service.html', '<h1>SMS Terms of Service</h1>', 'reply with the keyword <strong>HELP</strong> for assistance.</p>')
    tos_block = tos_block.replace('<h1>', '<h1 class="tos-title">')
    for fn, blk, path, title, desc, name in [
        ('privacy-policy/index.html', pp_block, '/privacy-policy/', 'Privacy Policy | Costa Mesa Jiu Jitsu',
         'Privacy Policy for Costa Mesa Jiu Jitsu at Double Ops, 369 E 17th St Suite 10, Costa Mesa, CA 92627.', 'Privacy Policy'),
        ('terms-of-service/index.html', tos_block, '/terms-of-service/', 'SMS Terms of Service | Costa Mesa Jiu Jitsu',
         'SMS Terms of Service for the Costa Mesa Jiu Jitsu text messaging program: message frequency, rates, opting out with STOP and help with HELP.', 'SMS Terms of Service')]:
        body = f'<div class="legal-wrap"><div class="wrap"><article class="legal">\n{blk}\n</article></div></div>'
        w(fn, page(title, desc, path, body, ld=[ORG, crumbs_ld(name, path)]))

# ================================================================ redirects, sitemap, robots
redirects = '''# Costa Mesa Jiu Jitsu redirects (Netlify)
# Real pages always win over these rules. First match wins.
# Old WordPress URLs go to their closest new page or the home page, so nothing on the old site ends in a 404.

# Builder scripts and data are in the repo but not meant to be browsed
/tools/*                 /                         301!

# Old pages that have a new home
/coach-brady-fink        /brady-fink/              301
/author/coach-brady      /brady-fink/              301
/beginners               /beginners-classes/       301
/beginner                /beginners-classes/       301
/free-class              /free-trial/              301
/privates                /private-lessons/         301
/memberships             /pricing/                 301
/sms-terms               /terms-of-service/        301

# Old pages folded into sections of the home page
/schedule                /#schedule                301
/coaches                 /#coaches                 301
/youth                   /kids-jiu-jitsu/          301
/kids                    /kids-jiu-jitsu/          301
/youth-jiu-jitsu         /kids-jiu-jitsu/          301
/kids-bjj                /kids-jiu-jitsu/          301
/youth-bjj               /kids-jiu-jitsu/          301
/contact                 /#contact                 301
/store                   /#shop                    301
/gear-suggestions        /#shop                    301
/portfolio/*             /#shop                    301
/project-type/*          /#shop                    301

# Old sitemaps point to the new one
/sitemap_index.xml       /sitemap.xml              301
/post-sitemap.xml        /sitemap.xml              301
/page-sitemap.xml        /sitemap.xml              301
/portfolio-sitemap.xml   /sitemap.xml              301
/category-sitemap.xml    /sitemap.xml              301
/project-type-sitemap.xml /sitemap.xml             301
/author-sitemap.xml      /sitemap.xml              301
/wp-sitemap.xml          /sitemap.xml              301

# Every other old WordPress page goes to the home page
/waiver                  /                         301
/class-recaps            /                         301
/members                 /                         301
/activate                /                         301
/create-account          /                         301
/footer                  /                         301
/yoga                    /                         301
/nogi-fundamentals-september-16th-2025 /                       301
/category/*              /                         301
/author/*                /                         301
/tag/*                   /                         301
/feed                    /                         301
/comments/*              /                         301
/wp-admin/*              /                         301
/wp-admin                /                         301
/wp-login.php            /                         301
/wp-content/*            /                         301
/wp-json/*               /                         301
/xmlrpc.php              /                         301
/home                    /                         301
/index.php               /                         301
/blog                    /                         301
/blog/*                  /                         301

# Any other unknown address is caught by 404.html, which forwards visitors to the home page.
# (A catch-all "/*  /  301" rule does not work on Netlify: it is treated as a redirect loop.)
'''
w('_redirects', redirects)
w('404.html', '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Costa Mesa Jiu Jitsu</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=/">
<script>location.replace('/');</script>
<style>html,body{margin:0;height:100%;background:#111113;color:#fff;font-family:Manrope,'Helvetica Neue',Arial,sans-serif}body{display:grid;place-items:center;text-align:center}a{color:#f0544f}</style>
</head>
<body><p>Taking you to <a href="/">Costa Mesa Jiu Jitsu</a>...</p></body>
</html>
''')

urls = [('/', '1.0', 'weekly'), ('/free-trial/', '0.9', 'monthly'), ('/beginners-classes/', '0.9', 'monthly'), ('/kids-jiu-jitsu/', '0.9', 'monthly'),
        ('/pricing/', '0.8', 'monthly'), ('/private-lessons/', '0.8', 'monthly'), ('/brady-fink/', '0.6', 'yearly'), ('/upcoming-tournaments/', '0.7', 'weekly'),
        ('/privacy-policy/', '0.2', 'yearly'), ('/terms-of-service/', '0.2', 'yearly')]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    f'  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>\n' for u, p, c in urls) + '</urlset>\n'
w('sitemap.xml', sm)
w('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
print('built', [u for u, _, _ in urls])
