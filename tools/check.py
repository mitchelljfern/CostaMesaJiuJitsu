#!/usr/bin/env python3
"""Rebuilds the site and checks it for the mistakes that are easy to make.

Run this before every push:    python3 tools/check.py

It rebuilds every generated page, then checks that:
  - the generated pages were up to date (nobody hand-edited one or forgot to rebuild)
  - the schedule says the same thing everywhere
  - membership prices match between the cards and the data Google reads
  - every lead form still has the required, unchecked text message consent box
  - the carrier-required texting lines are still in the policy pages
  - no em dashes, no removed programs, and the address always includes Unit 7
  - nothing new was bolted on (frameworks, package files, extra stylesheets or scripts)

Exit code 0 means everything passed. Anything else means read the list it prints.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
os.chdir(REPO)
problems, notes = [], []


def rd(p):
    return open(os.path.join(REPO, p), encoding='utf-8').read()


def bad(msg):
    problems.append(msg)


# ---------------------------------------------------------------- 1. rebuild, and see if anything was stale
def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True).stdout


before = git('status', '--porcelain')
for script in ('build.py', 'tournaments.py'):
    r = subprocess.run([sys.executable, os.path.join(HERE, script)], capture_output=True, text=True)
    if r.returncode != 0:
        bad(f'tools/{script} crashed:\n' + (r.stderr.strip().splitlines() or ['(no error text)'])[-1])
after = git('status', '--porcelain')
stale = sorted(set(l[3:] for l in after.splitlines()) - set(l[3:] for l in before.splitlines()))
if stale and not before.strip():
    # Nothing was being edited, yet the build changed files: what was committed did not match its source.
    bad('These generated files did not match their source and have just been rebuilt. Commit them:\n    ' + '\n    '.join(stale)
        + '\n    (If one was edited by hand, that edit is gone. Make the change in index.html or tools/ instead.)')
elif stale:
    notes.append('Rebuilt from your edits (commit these along with your change): ' + ', '.join(stale))

pages = [p for p in ('index.html', 'free-trial/index.html', 'kids-jiu-jitsu/index.html', 'pricing/index.html',
                     'private-lessons/index.html', 'brady-fink/index.html', 'upcoming-tournaments/index.html',
                     'privacy-policy/index.html', 'terms-of-service/index.html', 'waiver/index.html', '404.html')
         if os.path.exists(os.path.join(REPO, p))]
home = rd('index.html')

# ---------------------------------------------------------------- 2. schedule agrees everywhere
DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def fmt(h, m):
    return f"{h % 12 or 12}:{m:02d} {'PM' if h >= 12 else 'AM'}"


sched = set()
m = re.search(r'var SCHED = \[(.*?)\];', home, re.S)
if not m:
    bad('index.html: could not find "var SCHED" (the Next Class data).')
else:
    for d, h, mi in re.findall(r'\[(\d),(\d+),(\d+),', m.group(1)):
        sched.add((int(d), fmt(int(h), int(mi))))

cards = set()
wk = re.search(r'id="week">(.*?)<p class="schedule-note">', home, re.S)
if not wk:
    bad('index.html: could not find the weekly schedule (id="week").')
else:
    for d, body in re.findall(r'<div class="day" data-day="(\d)">(.*?)(?=<div class="day" data-day=|$)', wk.group(1), re.S):
        for t in re.findall(r'<span class="cls-time">([^<]+)</span>', body):
            cards.add((int(d), t.strip()))
if sched and cards and sched != cards:
    only_c = sorted(cards - sched); only_s = sorted(sched - cards)
    bad('The schedule cards and the Next Class data (var SCHED) disagree.'
        + (''.join(f'\n    only in the cards: {DAYS[d]} {t}' for d, t in only_c))
        + (''.join(f'\n    only in SCHED:     {DAYS[d]} {t}' for d, t in only_s)))


def options(html):
    sel = re.search(r'<select id="cls".*?</select>', html, re.S)
    return re.findall(r'<option>([^<]+)</option>', sel.group(0)) if sel else None


home_opts = options(home)
if home_opts is None:
    bad('index.html: could not find the free class form\'s class list (id="cls").')
else:
    for o in home_opts:
        mm = re.match(r'(\w+) (\d{1,2}:\d{2} [AP]M)', o)
        if not mm or mm.group(1) not in DAYS or (DAYS.index(mm.group(1)), mm.group(2)) not in sched:
            bad(f'Free class form lists "{o}", which is not a class in the schedule.')
    listed = set()
    for o in home_opts:
        mm = re.match(r'(\w+) (\d{1,2}:\d{2} [AP]M)', o)
        if mm and mm.group(1) in DAYS:
            listed.add((DAYS.index(mm.group(1)), mm.group(2)))
    for d, t in sorted(sched - listed):
        bad(f'{DAYS[d]} {t} is in the schedule but missing from the free class form\'s class list.')
    for p in ('free-trial/index.html', 'kids-jiu-jitsu/index.html'):
        if os.path.exists(p):
            o2 = options(rd(p))
            if o2 is not None and not set(o2) <= set(home_opts):   # the kids page lists only the kids classes
                bad(f'{p}: its class list has times the home page does not. Run the build (do not edit this file by hand).')

llms = rd('tools/llms.txt')
for d, t in sorted(sched):
    line = next((l for l in llms.splitlines() if l.startswith(f'- {DAYS[d]}:')), '')
    if t not in line:
        bad(f'tools/llms.txt: the {DAYS[d]} line does not mention {t}.')

# ---------------------------------------------------------------- 3. prices agree
card = dict((n.strip(), p) for n, p in re.findall(r'<div class="plan-name">([^<]+)</div>\s*<div class="plan-price"><b>\$(\d+)</b>', home))
ld = dict((n, p) for n, p in re.findall(r'"name": "(Unlimited (?:Adult|Kids)) Jiu Jitsu", "price": "(\d+)"', home))
for plan in ('Unlimited Adult', 'Unlimited Kids'):
    if plan in card and plan in ld and card[plan] != ld[plan]:
        bad(f'{plan}: the pricing card says ${card[plan]} but the data Google reads (top of index.html) says ${ld[plan]}.')
    if plan in card and f'{plan} ${card[plan]}/month' not in llms:
        bad(f'tools/llms.txt does not say "{plan} ${card[plan]}/month".')

# ---------------------------------------------------------------- 4. text message consent (carrier requirement)
CONSENT = 'I agree to receive recurring automated text messages from Costa Mesa Jiu Jitsu at the mobile number I provide.'
for p in pages:
    s = rd(p)
    for form in re.findall(r'<form[^>]*data-lead=.*?</form>', s, re.S):
        fid = (re.search(r'id="(\w+)"', form) or [None, '?'])[1]
        if 'type="tel"' not in form:
            continue
        box = re.search(r'<input[^>]*name="sms_consent"[^>]*>', form)
        if not box:
            bad(f'{p}: form "{fid}" asks for a phone number but has no text message consent checkbox.')
        else:
            if 'required' not in box.group(0):
                bad(f'{p}: form "{fid}": the consent checkbox must be required.')
            if re.search(r'\schecked', box.group(0)):
                bad(f'{p}: form "{fid}": the consent checkbox must NOT be pre-checked.')
            if CONSENT not in form:
                bad(f'{p}: form "{fid}": the consent wording was changed. It must stay word for word.')
            if form.index('name="sms_consent"') > form.rindex('type="submit"'):
                bad(f'{p}: form "{fid}": the consent checkbox must sit above the submit button.')

LEGAL = ['No mobile information will be shared with third parties/affiliates for marketing/promotional purposes. Text messaging originator opt-in data and consent will not be shared with any third parties.',
         'Msg &amp; data rates may apply.', 'Carriers are not liable for delayed or undelivered messages.']
for p in ('privacy-policy/index.html', 'terms-of-service/index.html'):
    s = rd(p)
    for line in LEGAL:
        if line not in s:
            bad(f'{p}: a carrier-required line is missing or reworded: "{line[:60]}..."')

# ---------------------------------------------------------------- 5. copy rules
for p in pages + ['llms.txt', 'tools/llms.txt']:
    s = rd(p)
    if '—' in s:
        bad(f'{p}: contains an em dash. Use a comma, period or parentheses instead.')
    if p.startswith('waiver') or 'waiver' in p:
        continue
    if re.search(r'2428 Newport Blvd(?!, Unit 7)', s):
        bad(f'{p}: the address must be written "2428 Newport Blvd, Unit 7".')
    for phrase, why in (('Beginners Jiu Jitsu Program', 'the $99 Beginners program was removed in November 2026'),
                        ('beginners-classes', 'the Beginners program page was removed'),
                        ('Darby', 'Coach Darby no longer works here')):
        if phrase.lower() in s.lower():
            bad(f'{p}: mentions "{phrase}" ({why}).')

# ---------------------------------------------------------------- 6. nothing bolted on
for f in ('package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'node_modules', 'vite.config.js', 'tailwind.config.js', 'next.config.js', 'requirements.txt'):
    if os.path.exists(os.path.join(REPO, f)):
        bad(f'{f} was added. This site has no frameworks or packages on purpose. Remove it.')
ok_assets = {'lead-gate.js', 'pages.js', 'site.css', 'waiver.js'}
extra = sorted(set(os.listdir('assets')) - ok_assets)
if extra:
    bad('New files in assets/: ' + ', '.join(extra) + '. Put styles in index.html and scripts in the existing files instead of adding new ones.')
for p in pages:
    for src in re.findall(r'<(?:script|link)[^>]+(?:src|href)="(https?://[^"]+)"', rd(p)):
        host = src.split('/')[2]
        if not any(host == h or host.endswith('.' + h) for h in ('costamesajiujitsu.com', 'googleapis.com', 'gstatic.com', 'googletagmanager.com',
                                                                    'leadconnectorhq.com', 'msgsndr.com', 'cloudflare.com', 'ossdojo.com', 'netlify.app')):
            bad(f'{p}: loads something from a new outside site ({host}). Ask Mitchell before adding outside scripts or styles.')

# ---------------------------------------------------------------- report
if problems:
    for n in notes:
        print(n)
    print(f'\n{len(problems)} problem(s) found:\n')
    for i, p in enumerate(problems, 1):
        print(f'{i}. {p}\n')
    sys.exit(1)
for n in notes:
    print(n)
print(f'All checks passed. {len(sched)} classes a week, {len(pages)} pages checked.')
