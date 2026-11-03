#!/usr/bin/env python3
"""Builds /upcoming-tournaments/ from a JSON list of events.

Usage: python3 tournaments.py <repo-dir> <old-pages-dir> <events.json> <checked-date YYYY-MM-DD>
Reuses the shared parts (head, header, footer, page) from build.py in the same folder.
"""
import datetime as dt, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO, OLD, EVENTS, CHECKED = sys.argv[1:5]
src = open(os.path.join(HERE, 'build.py'), encoding='utf-8').read()
shared = src.split('# ================================================================ /free-trial/')[0]
sys.argv = [sys.argv[0], REPO, OLD]
exec(compile(shared, 'build.py', 'exec'))   # defines head, header, footer, page, crumbs, ORG, SITE, SHARE, w, ...

doc = json.load(open(EVENTS, encoding='utf-8'))
events, NOTE = doc['events'], doc.get('note', '')
events.sort(key=lambda e: (e['start'], e['org'], e['name']))
e = html.escape

ORG_COLORS = {'IBJJF': '#3b82f6', 'NABJJF': '#22c3a6', 'NAGA': '#f0544f', 'JJWL': '#a78bfa', 'ADCC': '#f5b84a',
              'Grappling Industries': '#f472b6', 'AGF': '#94a3b8', 'SJJIF': '#84cc16'}

def fmt_day(d):
    x = dt.date.fromisoformat(d); return x.strftime('%a'), x.strftime('%b'), str(x.day)

def fmt_range(a, b):
    x, y = dt.date.fromisoformat(a), dt.date.fromisoformat(b or a)
    if x == y: return x.strftime('%A, %B ') + str(x.day) + x.strftime(', %Y')
    if x.month == y.month: return x.strftime('%a %b ') + f'{x.day} to ' + y.strftime('%a %b ') + f'{y.day}, {y.year}'
    return x.strftime('%a %b ') + f'{x.day} to ' + y.strftime('%a %b ') + f'{y.day}, {y.year}'

def style_chips(styles):
    return ''.join(f'<span class="t-chip {"gi" if s == "Gi" else "nogi"}">{e(s)}</span>' for s in styles)

for ev in events:   # current price as of the check date (the page updates it live in the browser)
    tier = next((t for t in ev.get('prices', []) if not t.get('sold_out') and (not t.get('until') or t['until'] >= CHECKED)), None)
    ev['price_from'] = tier['amount'] if tier else ''
    ev['price_from_num'] = float(tier['amount'].strip('$').replace(',', '')) if tier else None

cards = []
for i, ev in enumerate(events):
    wd, mo, dy = fmt_day(ev['start'])
    multi = ev.get('end') and ev['end'] != ev['start']
    if multi:
        _, mo2, dy2 = fmt_day(ev['end']); day_html = f'{dy}<small>to {dy2 if mo2 == mo else mo2 + " " + dy2}</small>'
    else:
        day_html = dy
    color = ORG_COLORS.get(ev['org'], '#94a3b8')
    groups = ' '.join(g for g, on in [('kids', ev.get('kids')), ('adults', ev.get('adults'))] if on)
    price = ev.get('price_from') or ''
    cards.append(f'''      <li class="t-item" data-org="{e(ev['org'])}" data-style="{e(' '.join(ev['style']))}" data-groups="{groups}" data-end="{e(ev.get('end') or ev['start'])}">
        <button class="t-card" type="button" data-i="{i}" aria-haspopup="dialog">
          <span class="t-date" aria-hidden="true"><span>{wd}</span><b>{day_html}</b><span>{mo}</span></span>
          <span class="t-main">
            <span class="t-org" style="--org:{color}">{e(ev['org'])}</span>
            <span class="t-name">{e(ev['name'])}</span>
            <span class="t-where">{e(ev['city'])}{(' · ' + e(ev['venue'])) if ev.get('venue') else ''}</span>
            <span class="t-tags">{style_chips(ev['style'])}<span class="t-chip plain">{e(ev.get('levels_short') or '')}</span></span>
          </span>
          <span class="t-side">
            {'<span class="t-price muted">Registration closed</span>' if ev.get('closed') else (f'<span class="t-price" data-price><small>{e(ev.get("price_label") or "now")}</small>{e(price)}</span>' if price else '<span class="t-price muted">Prices TBA</span>')}
            <span class="t-more">Details <span aria-hidden="true">→</span></span>
          </span>
          <span class="sr-only">{e(fmt_range(ev['start'], ev.get('end')))}</span>
        </button>
      </li>''')

orgs = []
for ev in events:
    if ev['org'] not in orgs: orgs.append(ev['org'])
org_filters = ''.join(f'<button type="button" class="t-filter" data-f="org" data-v="{e(o)}" aria-pressed="false"><i style="background:{ORG_COLORS.get(o, "#94a3b8")}"></i>{e(o)}</button>' for o in orgs)

css = '''<style>
.t-intro { display: grid; gap: 16px; }
.t-filters { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 18px; }
.t-filter { font: inherit; font-size: 13px; font-weight: 700; letter-spacing: 0.04em; padding: 9px 14px; border-radius: 8px; border: 1px solid var(--line-strong); background: transparent; color: var(--fg-body); cursor: pointer; display: inline-flex; align-items: center; gap: 8px; min-height: 40px; }
.t-filter i { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.t-filter[aria-pressed="true"] { background: var(--fg); color: var(--bg); border-color: var(--fg); }
.t-filter:focus-visible, .t-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.t-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; grid-template-columns: minmax(0, 1fr); }
@media (min-width: 1000px) { .t-list { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.t-item[hidden] { display: none; }
.t-card { width: 100%; font: inherit; color: inherit; text-align: left; cursor: pointer; display: grid; grid-template-columns: 72px minmax(0, 1fr) auto; gap: 16px; align-items: center; background: var(--bg-card); border: 1px solid var(--line); border-radius: var(--radius-md); padding: 14px 16px 14px 14px; transition: border-color 160ms var(--ease), transform 160ms var(--ease); }
.t-card:hover { border-color: var(--line-strong); transform: translateY(-1px); }
.t-date { display: grid; justify-items: center; align-content: center; gap: 0; background: var(--bg-raised); border-radius: 10px; padding: 8px 4px; min-height: 84px; font-family: var(--font-condensed); text-transform: uppercase; color: var(--fg-muted); font-size: 15px; letter-spacing: 0.06em; line-height: 1.1; }
.t-date b { font-weight: 400; font-size: 36px; line-height: 1; color: var(--fg); display: grid; justify-items: center; }
.t-date b small { font-size: 12px; color: var(--fg-muted); letter-spacing: 0.04em; }
.t-main { display: grid; gap: 4px; min-width: 0; }
.t-org { font-size: 11px; font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase; color: var(--org); }
.t-name { font-family: var(--font-display); font-weight: 800; text-transform: uppercase; font-size: 16px; line-height: 1.15; color: var(--fg); letter-spacing: -0.005em; }
.t-where { font-size: 14px; color: var(--fg-muted); }
.t-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.t-chip { font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; padding: 4px 8px; border-radius: 6px; border: 1px solid var(--line-strong); color: var(--fg-body); }
.t-chip.gi { background: rgba(255,255,255,0.92); color: #111113; border-color: transparent; }
.t-chip.nogi { background: #0a0a0b; color: #ffffff; border-color: rgba(255,255,255,0.28); }
html[data-mode="light"] .t-chip.gi { background: #ffffff; color: #111113; border-color: var(--line-strong); }
html[data-mode="light"] .t-chip.nogi { background: #111113; color: #ffffff; border-color: transparent; }
.t-chip.plain:empty { display: none; }
.t-side { display: grid; justify-items: end; gap: 6px; text-align: right; }
.t-price { font-family: var(--font-condensed); font-size: 30px; line-height: 1; color: var(--fg); display: grid; justify-items: end; }
.t-price small { font-family: var(--font-body); font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--fg-muted); }
.t-price.muted { font-size: 18px; color: var(--fg-muted); }
.t-more { font-size: 12px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); white-space: nowrap; }
@media (max-width: 520px) {
  .t-card { grid-template-columns: 60px minmax(0, 1fr); padding: 12px; gap: 12px; }
  .t-date { min-height: 72px; }
  .t-date b { font-size: 30px; }
  .t-side { grid-column: 2; justify-items: start; text-align: left; grid-auto-flow: column; align-items: end; justify-content: space-between; }
  .t-price { justify-items: start; }
}
.t-empty { text-align: center; color: var(--fg-muted); padding: 32px 0; }
.t-note { font-size: 13px; color: var(--fg-muted); margin-top: 18px; }

dialog.t-dialog { border: 1px solid var(--line-strong); border-radius: var(--radius-lg); padding: 0; width: min(680px, calc(100vw - 24px)); max-height: min(88vh, 900px); background: var(--bg-card); color: var(--fg-body); overscroll-behavior: contain; }
dialog.t-dialog::backdrop { background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); }
.t-d-head { position: sticky; top: 0; z-index: 1; background: var(--bg-card); padding: 20px 22px 14px; border-bottom: 1px solid var(--line); display: grid; gap: 6px; }
.t-d-head h2 { margin: 0; font-family: var(--font-display); font-weight: 800; text-transform: uppercase; font-size: clamp(22px, 4vw, 30px); line-height: 1.05; color: var(--fg); padding-right: 44px; }
.t-close { position: absolute; top: 14px; right: 14px; width: 40px; height: 40px; border-radius: 8px; border: 1px solid var(--line-strong); background: transparent; color: var(--fg); cursor: pointer; display: grid; place-items: center; }
.t-close svg { width: 18px; height: 18px; }
.t-d-body { padding: 18px 22px 22px; display: grid; gap: 18px; }
.t-facts { display: grid; gap: 10px; grid-template-columns: minmax(0, 1fr); margin: 0; }
@media (min-width: 560px) { .t-facts { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.t-facts div { background: var(--bg-raised); border-radius: 10px; padding: 12px 14px; display: grid; gap: 2px; }
.t-facts dt { font-size: 11px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: var(--fg-muted); }
.t-facts dd { margin: 0; color: var(--fg); font-weight: 600; font-size: 15px; }
.t-facts dd a { color: var(--accent); font-size: 13px; font-weight: 700; }
.t-sec h3 { margin: 0 0 8px; font-size: 12px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: var(--fg-muted); }
.t-prices { width: 100%; border-collapse: collapse; font-size: 15px; }
.t-prices td { padding: 9px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
.t-prices td:last-child { text-align: right; font-family: var(--font-condensed); font-size: 22px; color: var(--fg); white-space: nowrap; padding-left: 12px; }
.t-prices tr.past td { opacity: 0.45; text-decoration: line-through; }
.t-prices tr.now td:first-child::after { content: "Current price"; margin-left: 8px; font-size: 10px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); border: 1px solid var(--accent); border-radius: 4px; padding: 1px 5px; vertical-align: 2px; }
.t-list-plain { margin: 0; padding-left: 18px; display: grid; gap: 6px; }
.t-list-plain li::marker { color: var(--accent); }
.t-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.t-actions .btn { flex: 1 1 200px; }
.t-src { font-size: 12px; color: var(--fg-muted); }
.t-src a { color: var(--fg-muted); }
.t-coach { background: var(--bg-raised); border-radius: 10px; padding: 14px 16px; font-size: 14px; }
.t-coach a { color: var(--accent); font-weight: 700; }
</style>
'''

body = f'''<section class="page-hero">
  <div class="wrap" style="grid-template-columns:minmax(0,1fr)">
    <div class="page-hero-copy">
      {crumbs('Upcoming tournaments')}
      <p class="kicker">Southern California<span class="tiny-star" aria-hidden="true">★</span>Updated {dt.date.fromisoformat(CHECKED).strftime('%B %-d, %Y')}</p>
      <h1 class="display h1">Upcoming <em>tournaments</em></h1>
      <p class="lead">IBJJF, NABJJF, NAGA, JJWL, ADCC and Grappling Industries events near Costa Mesa. Tap any event for divisions, prices, deadlines and the registration link.</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="t-filters" role="group" aria-label="Filter tournaments">
      <button type="button" class="t-filter" data-f="all" aria-pressed="true">All events</button>
      <button type="button" class="t-filter" data-f="style" data-v="Gi" aria-pressed="false">Gi</button>
      <button type="button" class="t-filter" data-f="style" data-v="NoGi" aria-pressed="false">NoGi</button>
      <button type="button" class="t-filter" data-f="groups" data-v="kids" aria-pressed="false">Kids divisions</button>
      {org_filters}
    </div>
    <ul class="t-list" id="tList">
{chr(10).join(cards)}
    </ul>
    <p class="t-empty" id="tEmpty" hidden>No events match these filters. <button type="button" class="link" data-f="all" style="background:none;border:0;cursor:pointer;font:inherit;color:var(--accent)">Show all events</button></p>
    <p class="t-note">{e(NOTE)} Dates, prices and deadlines come from each organization's website and can change. Always confirm on the event page before you register.</p>
  </div>
</section>

<section class="section section-dark">
  <div class="wrap cta-band">
    <p class="kicker">Competing?</p>
    <h2 class="display h2">Let your coach know</h2>
    <p class="lead" style="margin-inline:auto">Tell a coach which event you're signing up for so we can help you pick a division and get ready. A few private lessons before a tournament go a long way.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="/private-lessons/">Book a private lesson</a>
      <a class="btn btn-outline" href="/#schedule">See the class schedule</a>
    </div>
  </div>
</section>

<dialog class="t-dialog" id="tDialog" aria-labelledby="tTitle">
  <div class="t-d-head">
    <span class="t-org" id="tOrg"></span>
    <h2 id="tTitle"></h2>
    <div class="t-tags" id="tTags"></div>
    <button class="t-close" type="button" id="tClose" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  </div>
  <div class="t-d-body" id="tBody"></div>
</dialog>

<script type="application/json" id="tData">{json.dumps(events, ensure_ascii=False).replace('</', '<\\/')}</script>
<script>
(function () {{
  var data = JSON.parse(document.getElementById('tData').textContent);
  var list = document.getElementById('tList'), items = Array.prototype.slice.call(list.children), empty = document.getElementById('tEmpty');
  var today = new Date(); today.setHours(0, 0, 0, 0);
  function d(s) {{ var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }}
  // Current price on each card, based on today's date
  function currentTier(e) {{ var t = null; (e.prices || []).forEach(function (p) {{ if (!t && !p.sold_out && (!p.until || d(p.until) >= today)) t = p; }}); return t; }}
  items.forEach(function (li) {{
    var e = data[+li.querySelector('.t-card').getAttribute('data-i')], el = li.querySelector('[data-price]'), t = currentTier(e);
    if (el && t) el.innerHTML = '<small>' + (e.price_label || 'now') + '</small>' + t.amount;
    if (!e.closed && e.prices && e.prices.length && !t && el) el.outerHTML = '<span class="t-price muted">Registration closed</span>';
  }});
  // Hide events that already happened
  items.forEach(function (li) {{ if (d(li.getAttribute('data-end')) < today) li.setAttribute('data-past', ''); }});
  var state = {{ style: null, groups: null, org: null }};
  var btns = Array.prototype.slice.call(document.querySelectorAll('.t-filter'));
  function apply() {{
    var shown = 0;
    items.forEach(function (li) {{
      var ok = !li.hasAttribute('data-past')
        && (!state.style || li.getAttribute('data-style').split(' ').indexOf(state.style) > -1)
        && (!state.groups || li.getAttribute('data-groups').split(' ').indexOf(state.groups) > -1)
        && (!state.org || li.getAttribute('data-org') === state.org);
      li.hidden = !ok; if (ok) shown++;
    }});
    empty.hidden = shown > 0;
    btns.forEach(function (b) {{
      var f = b.getAttribute('data-f'), v = b.getAttribute('data-v');
      b.setAttribute('aria-pressed', f === 'all' ? String(!state.style && !state.groups && !state.org) : String(state[f] === v));
    }});
  }}
  document.addEventListener('click', function (ev) {{
    var b = ev.target.closest('[data-f]'); if (!b) return;
    var f = b.getAttribute('data-f'), v = b.getAttribute('data-v');
    if (f === 'all') state = {{ style: null, groups: null, org: null }};
    else state[f] = state[f] === v ? null : v;
    apply();
  }});
  apply();

  // Details panel
  var dlg = document.getElementById('tDialog'), body = document.getElementById('tBody'), lastCard = null;
  function esc(s) {{ return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {{ return {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }}[c]; }}); }}
  var MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], DAY = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  function nice(s) {{ var x = d(s); return DAY[x.getDay()] + ', ' + MON[x.getMonth()] + ' ' + x.getDate() + ', ' + x.getFullYear(); }}
  function when(e) {{ return e.end && e.end !== e.start ? nice(e.start) + ' to ' + nice(e.end) : nice(e.start); }}
  function gcal(e) {{
    var s = e.start.replace(/-/g, ''), x = d(e.end || e.start); x.setDate(x.getDate() + 1);
    var en = x.getFullYear() + ('0' + (x.getMonth() + 1)).slice(-2) + ('0' + x.getDate()).slice(-2);
    return 'https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + encodeURIComponent(e.org + ' ' + e.name) + '&dates=' + s + '/' + en + '&location=' + encodeURIComponent([e.venue, e.address || e.city].filter(Boolean).join(', ')) + '&details=' + encodeURIComponent('Register: ' + (e.register_url || e.event_url));
  }}
  function open(i, card) {{
    var e = data[i]; lastCard = card;
    document.getElementById('tOrg').textContent = e.org;
    document.getElementById('tOrg').style.setProperty('--org', card.querySelector('.t-org').style.getPropertyValue('--org'));
    document.getElementById('tTitle').textContent = e.name;
    document.getElementById('tTags').innerHTML = e.style.map(function (s) {{ return '<span class="t-chip ' + (s === 'Gi' ? 'gi' : 'nogi') + '">' + esc(s) + '</span>'; }}).join('');
    var map = 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent([e.venue, e.address || e.city].filter(Boolean).join(', '));
    var html = '<dl class="t-facts">'
      + '<div><dt>Date</dt><dd>' + esc(when(e)) + '</dd></div>'
      + '<div><dt>Where</dt><dd>' + esc(e.venue || e.city) + (e.address ? '<br><span style="font-weight:500;color:var(--fg-body);font-size:14px">' + esc(e.address) + '</span>' : (e.venue ? '<br><span style="font-weight:500;color:var(--fg-body);font-size:14px">' + esc(e.city) + '</span>' : '')) + '<br><a href="' + map + '" target="_blank" rel="noopener">Open in Maps →</a></dd></div>'
      + '<div><dt>Style</dt><dd>' + esc(e.style.join(' and ')) + (e.style_note ? '<br><span style="font-weight:500;color:var(--fg-body);font-size:14px">' + esc(e.style_note) + '</span>' : '') + '</dd></div>'
      + '<div><dt>Divisions</dt><dd>' + esc(e.divisions || 'See event page') + '</dd></div>'
      + '</dl>';
    if (e.levels) html += '<div class="t-sec"><h3>Belts and levels</h3><p style="margin:0">' + esc(e.levels) + '</p></div>';
    if (e.prices && e.prices.length) {{
      var cur = -1;
      e.prices.forEach(function (p, k) {{ if (cur < 0 && !p.sold_out && (!p.until || d(p.until) >= today)) cur = k; }});
      html += '<div class="t-sec"><h3>Registration prices</h3><table class="t-prices"><tbody>' + e.prices.map(function (p, k) {{
        var cls = (p.sold_out || (p.until && d(p.until) < today)) ? 'past' : (k === cur ? 'now' : '');
        return '<tr class="' + cls + '"><td>' + esc(p.label) + (p.until ? '<br><span style="font-size:13px;color:var(--fg-muted)">Until ' + esc(nice(p.until)) + '</span>' : '') + (p.member ? '<br><span style="font-size:13px;color:var(--fg-muted)">NABJJF members ' + esc(p.member) + '</span>' : '') + '</td><td>' + esc(p.amount) + '</td></tr>';
      }}).join('') + '</tbody></table>' + (e.price_note ? '<p class="t-src" style="margin:8px 0 0">' + esc(e.price_note) + '</p>' : '') + '</div>';
    }} else {{
      html += '<div class="t-sec"><h3>Registration prices</h3><p style="margin:0">' + esc(e.price_note || 'Not published yet. Check the event page.') + '</p></div>';
    }}
    if (e.deadlines && e.deadlines.length) html += '<div class="t-sec"><h3>Key deadlines</h3><ul class="t-list-plain">' + e.deadlines.map(function (x) {{ return '<li><b style="color:var(--fg)">' + esc(x.label) + ':</b> ' + esc(x.date ? nice(x.date) : x.text) + (x.date && x.text ? ' (' + esc(x.text) + ')' : '') + '</li>'; }}).join('') + '</ul></div>';
    if (e.notes && e.notes.length) html += '<div class="t-sec"><h3>Good to know</h3><ul class="t-list-plain">' + e.notes.map(function (n) {{ return '<li>' + esc(n) + '</li>'; }}).join('') + '</ul></div>';
    var regs = e.register_links && e.register_links.length ? e.register_links : [{{ label: 'Register on ' + (e.register_label || e.org), url: e.register_url || e.event_url }}];
    if (e.closed) html += '<div class="t-coach" style="border:1px solid var(--accent)"><b style="color:var(--fg)">Registration is closed.</b> ' + esc(e.closed_note || 'Spectators are welcome.') + '</div>';
    html += '<div class="t-actions">'
      + (e.closed ? '' : regs.map(function (r, k) {{ return '<a class="btn ' + (k === 0 || regs.length > 1 ? 'btn-primary' : 'btn-outline') + '" href="' + esc(r.url) + '" target="_blank" rel="noopener">' + esc(r.label) + '</a>'; }}).join(''))
      + (e.event_url && e.event_url !== e.register_url ? '<a class="btn btn-outline" href="' + esc(e.event_url) + '" target="_blank" rel="noopener">Event page</a>' : '')
      + '<a class="btn btn-ghost" href="' + gcal(e) + '" target="_blank" rel="noopener">Add to Google Calendar</a>'
      + '</div>'
      + '<div class="t-coach">Signing up? Tell a coach so we can help you prepare, or <a href="/private-lessons/">book a private lesson</a> before the event.</div>'
      + '<p class="t-src" style="margin:0">Details checked {dt.date.fromisoformat(CHECKED).strftime('%B %-d, %Y')} on the ' + esc(e.org) + ' website. Confirm on the event page before registering.</p>';
    body.innerHTML = html;
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    body.scrollTop = 0; dlg.scrollTop = 0;
    document.body.style.overflow = 'hidden';
  }}
  list.addEventListener('click', function (ev) {{ var c = ev.target.closest('.t-card'); if (c) open(+c.getAttribute('data-i'), c); }});
  function close() {{ if (dlg.open) dlg.close(); }}
  document.getElementById('tClose').addEventListener('click', close);
  dlg.addEventListener('close', function () {{ document.body.style.overflow = ''; if (lastCard) lastCard.focus(); }});
  dlg.addEventListener('click', function (ev) {{ if (ev.target === dlg) close(); }});
}})();
</script>'''

def event_ld(ev):
    loc = {"@type": "Place", "name": ev.get('venue') or ev['city'],
           "address": {"@type": "PostalAddress", "streetAddress": ev.get('street', ''), "addressLocality": ev.get('locality') or ev['city'].split(',')[0],
                       "addressRegion": "CA", "addressCountry": "US"}}
    if not ev.get('street'): del loc['address']['streetAddress']
    o = {"@type": "SportsEvent", "name": f"{ev['org']} {ev['name']}" if not ev['name'].startswith(ev['org']) else ev['name'],
         "startDate": ev['start'], "endDate": ev.get('end') or ev['start'], "eventStatus": "https://schema.org/EventScheduled",
         "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "location": loc,
         "organizer": {"@type": "Organization", "name": ev.get('org_full') or ev['org'], "url": ev.get('org_url', ev.get('event_url'))},
         "url": ev.get('event_url') or ev.get('register_url'), "sport": "Brazilian Jiu Jitsu",
         "image": SHARE + '/photos/og-share.jpg',
         "description": f"{' and '.join(ev['style'])} jiu jitsu tournament in {ev['city']}. {ev.get('divisions') or ''}".strip()}
    if ev.get('price_from_num'):
        o['offers'] = {"@type": "Offer", "price": str(ev['price_from_num']), "priceCurrency": "USD", "url": ev.get('register_url') or ev.get('event_url'),
                       "availability": "https://schema.org/InStock"}
    return o

html_page = page('Upcoming BJJ Tournaments in Southern California | Costa Mesa Jiu Jitsu',
    'Upcoming IBJJF, NABJJF, NAGA, JJWL and ADCC jiu jitsu tournaments in Southern California: dates, Gi or NoGi, belts, prices, deadlines and how to register.',
    '/upcoming-tournaments/', body,
    ld=[ORG, crumbs_ld('Upcoming tournaments', '/upcoming-tournaments/'),
        {"@type": "ItemList", "name": "Upcoming jiu jitsu tournaments in Southern California",
         "itemListElement": [{"@type": "ListItem", "position": k + 1, "item": event_ld(ev)} for k, ev in enumerate(events)]}])
html_page = html_page.replace('</head>', css + '</head>', 1)
w('upcoming-tournaments/index.html', html_page)
print('tournaments page:', len(events), 'events')
