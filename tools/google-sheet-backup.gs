/**
 * Costa Mesa Jiu Jitsu: website lead backup + spam check
 *
 * Every form on costamesajiujitsu.com (free class, kids class, private lessons, rashguard)
 * sends its details here first (assets/lead-gate.js). This script:
 *   1. checks the invisible Cloudflare Turnstile token and a few bot signals,
 *   2. saves real leads to the "Leads" tab and spam to the "Spam" tab (created automatically),
 *   3. answers the website: real leads are then passed on to HighLevel, spam never reaches it.
 * It runs separately from HighLevel, so leads are kept even if HighLevel has a problem.
 * It also receives signed liability waivers from /waiver/ (see the bottom of this file).
 *
 * Setup (one time, about 3 minutes):
 *   1. Open the "CMJJ Website Leads (backup)" Google Sheet.
 *   2. Extensions > Apps Script. Delete what's there, paste this whole file, click Save.
 *   3. Turnstile secret: Project Settings (gear icon, left side) > Script Properties > Add script property
 *        Property: TURNSTILE_SECRET    Value: the Secret Key from Cloudflare Turnstile
 *      (Without it, the script still blocks spam using the other signals.)
 *   4. Optional: put an email address in ALERT_EMAIL below to get an email for every real lead.
 *   5. Deploy > Manage deployments > edit (pencil) > Version: New version > Deploy.
 *      The URL stays the same, so the website needs no change.
 *      (First time ever: Deploy > New deployment > Web app, Execute as: Me, Who has access: Anyone.)
 */

const SHEET_NAME = 'Leads';
const SPAM_SHEET = 'Spam';
const ALERT_EMAIL = 'mitchell@socialupgrades.com, info@costamesajiujitsu.com';   // lead alert emails. Leave '' for none.
const OUR_HOSTS = ['costamesajiujitsu.com', 'www.costamesajiujitsu.com', 'costa-mesa-jiu-jitsu.netlify.app', 'staging--costa-mesa-jiu-jitsu.netlify.app', 'localhost'];

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p.kind === 'waiver') return handleWaiver(p);   // signed liability waivers, see the bottom of this file
  const ts = verifyTurnstile(p);
  const verdict = judge(p, ts);

  const lock = LockService.getScriptLock();
  lock.tryLock(10000);
  try {
    const clean = (v) => {
      v = String(v == null ? '' : v).slice(0, 500);
      return /^[=+\-@]/.test(v) ? "'" + v : v;          // keep spreadsheet formulas out
    };
    const classOrItem = p.cls || (p.size ? [p.size, p.rank ? p.rank + ' belt' : ''].filter(String).join(', ') : '');
    const row = [
      new Date(), p.form, p.name, p.phone, p.email, p.age || p.who, classOrItem, p.when, p.goal, p.coach,
      p.heard, p.page, p.utm_source, p.utm_medium, p.utm_campaign, p.utm_content, p.utm_term, p.referrer
    ].map((v, i) => (i === 0 ? v : clean(v)));

    if (verdict.spam) {
      spamSheet().appendRow(row.concat([verdict.reasons.join(', ')]));
    } else {
      SpreadsheetApp.getActive().getSheetByName(SHEET_NAME).appendRow(row);
      if (ALERT_EMAIL) {
        MailApp.sendEmail({
          to: ALERT_EMAIL,
          subject: 'New CMJJ Site Lead: ' + (p.form || 'form') + ' from ' + (p.name || 'someone'),
          body: ['Form: ' + p.form, 'Name: ' + p.name, 'Phone: ' + p.phone, 'Email: ' + p.email,
                 'Who / age: ' + (p.age || p.who || ''), 'Class: ' + classOrItem, 'Page: ' + p.page,
                 'Source: ' + [p.utm_source, p.utm_campaign].filter(String).join(' / ')].join('\n')
        });
      }
    }
  } finally {
    lock.releaseLock();
  }
  return json({ ok: true, spam: verdict.spam });
}

/**
 * Decide if a submission is spam. Hard stops: the hidden trap field was filled in, or Turnstile
 * said no. Otherwise two or more warning signs together count as spam (one alone never does).
 */
function judge(p, ts) {
  const reasons = [];
  if (p.hp || p.website) return { spam: true, reasons: ['filled the hidden trap field'] };
  if (ts === false) return { spam: true, reasons: ['failed the Turnstile check'] };

  let score = 0;
  const add = (pts, why) => { score += pts; reasons.push(why); };
  const name = String(p.name || '').trim();
  const email = String(p.email || '').trim().toLowerCase();
  const local = email.split('@')[0] || '';
  const caps = (name.slice(1).match(/[A-Z]/g) || []).length;
  const dots = (local.match(/\./g) || []).length;

  if (ts === null) add(1, 'no Turnstile token');
  if (p.ms && Number(p.ms) < 3000) add(1, 'sent within 3 seconds of opening the page');
  if (p.touched === '0') add(1, 'no tap, click or keypress on the page');
  // Bots seen on the site: one-word random-letter names ("VntxReJJywsegiWVFQl") and Gmail addresses full of dots
  if (name && !/\s/.test(name) && name.length >= 12) {
    add(1, 'long one-word name');
    if (caps >= 4) add(1, 'random capitals in the name');
  }
  if (/@(gmail|googlemail)\./.test(email) && dots >= 3) {
    add(1, 'dotted-up Gmail address');
    if (dots >= 5) add(1, 'very dotted Gmail address');
  }
  if (/https?:|www\.|<a |\[url/i.test([name, p.goal, p.when].join(' '))) add(2, 'link in the form');
  if (p.host && OUR_HOSTS.indexOf(String(p.host).toLowerCase()) === -1) add(1, 'sent from another website');

  return { spam: score >= 2, reasons: reasons };
}

/** true = Turnstile passed, false = it failed, null = no token sent or no secret set (not judged). */
function verifyTurnstile(p) {
  const secret = PropertiesService.getScriptProperties().getProperty('TURNSTILE_SECRET');
  if (!secret) return undefined;              // Turnstile not set up yet: skip it entirely
  if (!p.cf_token) return null;
  try {
    const res = UrlFetchApp.fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'post', payload: { secret: secret, response: p.cf_token }, muteHttpExceptions: true
    });
    const out = JSON.parse(res.getContentText());
    return out.success === true;
  } catch (err) {
    return undefined;                           // Cloudflare unreachable: don't punish the visitor
  }
}

function spamSheet() {
  const ss = SpreadsheetApp.getActive();
  let sh = ss.getSheetByName(SPAM_SHEET);
  if (!sh) {
    sh = ss.insertSheet(SPAM_SHEET);
    const head = ss.getSheetByName(SHEET_NAME).getRange(1, 1, 1, 18).getValues()[0].concat(['Why it was flagged']);
    sh.getRange(1, 1, 1, head.length).setValues([head]).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function doGet() {
  return json({ ok: true, message: 'CMJJ lead backup is running.' });
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/* ============================================================== Liability waivers (/waiver/)
 * The waiver page posts kind=waiver. This builds a signed PDF from the frozen agreement text at
 * <site>/waiver/terms/<version>.html, saves it to the "CMJJ Signed Waivers" Drive folder and the
 * "Waivers" tab, and emails it to WAIVER_EMAIL plus a copy to the signer. The page only shows
 * "You're all set" after this answers { ok: true, waiver: true }.
 */
const WAIVER_EMAIL = 'info@costamesajiujitsu.com, mitchell@socialupgrades.com';
const WAIVER_SHEET = 'Waivers';
const WAIVER_FOLDER = 'CMJJ Signed Waivers';
const SEND_SIGNER_COPY = true;
const WAIVER_TZ = 'America/Los_Angeles';

function handleWaiver(p) {
  // Bots: trap field filled, or "signed" faster than anyone could read and sign. Answer quietly, save nothing.
  if (p.hp || (p.ms && Number(p.ms) < 15000)) return json({ ok: true, waiver: true, id: 'W-0' });
  // Flood guard: at most 60 waivers an hour
  const cache = CacheService.getScriptCache(), hourKey = 'wv-' + Utilities.formatDate(new Date(), 'UTC', 'yyyyMMddHH');
  const count = Number(cache.get(hourKey) || 0);
  if (count >= 60) return json({ ok: false, error: 'busy' });
  cache.put(hourKey, String(count + 1), 3700);

  const now = new Date();
  const id = 'W-' + Utilities.formatDate(now, WAIVER_TZ, 'yyMMdd-HHmm') + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();
  const signedAt = Utilities.formatDate(now, WAIVER_TZ, "MMMM d, yyyy 'at' h:mm:ss a z");
  const t = (v, n) => String(v == null ? '' : v).trim().slice(0, n || 200);
  const esc = (v) => t(v, 2000).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const forKids = p.mode === 'minors' || p.mode === 'both', forMe = p.mode !== 'minors';
  const minors = [];
  for (let i = 1; i <= 6; i++) if (t(p['minor_' + i + '_name'])) minors.push({ name: t(p['minor_' + i + '_name']), dob: t(p['minor_' + i + '_dob'], 10), sig: t(p['minor_' + i + '_sig']) });
  const people = (forMe ? [t(p.name)] : []).concat(minors.map((m) => m.name));
  const email = t(p.email, 120), emailOk = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
  if (!t(p.name) || !emailOk || !people.length || !t(p.typed_name)) return json({ ok: false, error: 'missing' });
  const sig = String(p.signature || '');
  const sigOk = /^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(sig) && sig.length < 600000;
  const version = /^[0-9a-z-]{4,40}$/.test(String(p.version || '')) ? String(p.version) : 'unknown';
  const terms = waiverTerms(version, p.host);
  const fmtDob = (d) => (/^\d{4}-\d{2}-\d{2}$/.test(d) ? Utilities.formatDate(new Date(d + 'T12:00:00'), WAIVER_TZ, 'MMM d, yyyy') : esc(d));
  const row = (k, v) => '<tr><th>' + k + '</th><td>' + (v || '<span class="muted">None</span>') + '</td></tr>';
  const inits = [['risk', '4. Assumption of risk'], ['release', '5. Release'], ['indemnity', '8. Indemnity'], ['info', '11. Concussion and cardiac arrest info sheets'], ['minors', '13. Minors']]
    .filter(([k]) => k !== 'minors' || forKids).map(([k, l]) => row(l, esc(p['init_' + k]))).join('');
  const kidsRows = minors.map((m, i) => row('Child ' + (i + 1), esc(m.name) + ', born ' + fmtDob(m.dob) + (m.sig ? '<br><span class="muted">Child acknowledged info sheets, typed: "' + esc(m.sig) + '"</span>' : ''))).join('');

  const html = '<html><head><meta charset="utf-8"><style>' +
    'body{font-family:Helvetica,Arial,sans-serif;font-size:10.5pt;color:#111;line-height:1.45}' +
    'h1{font-size:17pt;margin:0 0 2pt}h2{font-size:12.5pt;margin:16pt 0 6pt;text-transform:uppercase}h3{font-size:10.5pt;margin:10pt 0 3pt}' +
    'table{border-collapse:collapse;width:100%;margin:4pt 0 8pt}th,td{border:1px solid #ccc;padding:4pt 6pt;text-align:left;vertical-align:top}th{width:34%;background:#f2f6f7}' +
    '.muted{color:#666}.box{border:2px solid #111;padding:8pt 10pt;margin:10pt 0}.w-warn{font-weight:bold;text-transform:uppercase}ul{margin:0 0 6pt 16pt;padding:0}p{margin:0 0 6pt}' +
    '</style></head><body>' +
    '<h1>Costa Mesa Jiu Jitsu: Signed Liability Waiver</h1>' +
    '<p class="muted">2428 Newport Blvd, Costa Mesa, CA 92627 &middot; Confirmation ' + id + ' &middot; Agreement version ' + esc(version) + '</p>' +
    '<h2>Signer and participants</h2><table>' +
    row('Signed by', esc(p.name)) + row('Signer date of birth', fmtDob(t(p.dob, 10))) + row('Email', esc(email)) + row('Phone', esc(p.phone)) +
    row('Waiver covers', esc(people.join(', '))) + (forKids ? row('Relationship to children', esc(p.relationship)) + kidsRows : '') +
    row('Emergency contact', esc(p.emergency_name) + ', ' + esc(p.emergency_phone) + (p.emergency_relationship ? ' (' + esc(p.emergency_relationship) + ')' : '')) +
    row('Medical notes', esc(p.medical)) +
    row('Photos and video', p.media === 'yes' ? 'Yes, may be used in marketing' : 'No, please do not feature') + '</table>' +
    '<h2>Initials</h2><table>' + inits + '</table>' +
    '<h2>Signature</h2><div class="box">' +
    '<p>&#9745; Agreed to sign electronically. &#9745; Read the entire agreement and understands substantial legal rights are given up, including the right to sue for negligence.</p>' +
    '<p>Typed name: <b>' + esc(p.typed_name) + '</b></p>' +
    (sigOk ? '<p><img src="' + sig + '" style="width:300px;height:90px;border-bottom:1px solid #111"></p>' : '<p><b>Drawn signature missing</b></p>') +
    '<p>Signed ' + signedAt + '</p></div>' +
    '<h2>Agreement as signed</h2>' + (terms || '<p><b>The agreement text for version ' + esc(version) + ' could not be loaded when this PDF was made.</b> It is published at costamesajiujitsu.com/waiver/terms/' + esc(version) + '.html</p>') +
    '<h2>Signing record</h2><table>' +
    row('Received by server', signedAt) + row('Device clock', esc(p.client_time) + ' ' + esc(p.client_tz)) + row('Website', esc(p.host) + esc(p.page)) +
    row('Browser', esc(p.ua)) + row('Agreement text fingerprint (SHA-256)', esc(p.terms_hash)) + row('Agreement version', esc(version)) + row('Confirmation', id) + '</table>' +
    '</body></html>';

  const fileName = 'CMJJ Waiver - ' + people.join(', ').replace(/[\\/:*?"<>|]/g, '') + ' - ' + Utilities.formatDate(now, WAIVER_TZ, 'yyyy-MM-dd') + '.pdf';
  const pdf = Utilities.newBlob(html, 'text/html', 'waiver.html').getAs(MimeType.PDF).setName(fileName);

  let link = '';
  try { link = waiverFolder().createFile(pdf.copyBlob().setName(fileName)).getUrl(); } catch (err) { link = 'Not saved to Drive: ' + err.message; }
  try {
    const sh = waiverSheet();
    const clean = (v) => { v = String(v == null ? '' : v).slice(0, 500); return /^[=+\-@]/.test(v) ? "'" + v : v; };
    sh.appendRow([now, id, p.name, email, p.phone, p.dob, people.join(', '), forKids ? p.relationship : '', minors.map((m) => m.name + ' (' + m.dob + ')').join('; '),
      [p.emergency_name, p.emergency_phone, p.emergency_relationship].filter(String).join(', '), p.medical, p.media, version, link].map((v, i) => (i === 0 ? v : clean(v))));
  } catch (err) {}

  const list = people.map(esc).join(', ');
  MailApp.sendEmail({
    to: WAIVER_EMAIL,
    subject: 'Signed CMJJ Waiver: ' + people.join(', '),
    htmlBody: '<p><b>New signed waiver</b> (' + id + ')</p><p>Covers: ' + list + '<br>Signed by: ' + esc(p.name) + ', ' + esc(email) + ', ' + esc(p.phone) +
      '<br>Emergency contact: ' + esc(p.emergency_name) + ', ' + esc(p.emergency_phone) + '<br>Medical notes: ' + (esc(p.medical) || 'None') +
      '<br>Photos and video: ' + (p.media === 'yes' ? 'Yes' : 'No') + '</p><p>The signed PDF is attached' + (/^https:/.test(link) ? ' and saved in Drive: <a href="' + link + '">open</a>' : '') + '.</p>',
    attachments: [pdf],
    name: 'Costa Mesa Jiu Jitsu Website',
    replyTo: email
  });
  if (SEND_SIGNER_COPY) {
    MailApp.sendEmail({
      to: email,
      subject: 'Your Costa Mesa Jiu Jitsu waiver',
      htmlBody: '<p>Hi ' + esc(t(p.name).split(' ')[0]) + ',</p><p>Thanks for signing. Your waiver for ' + list + ' is on file, and a copy is attached for your records. ' +
        'Confirmation number: ' + id + '.</p><p>See you on the mat!<br>Costa Mesa Jiu Jitsu<br>2428 Newport Blvd, Costa Mesa, CA 92627<br>949-556-1178</p>' +
        '<p style="color:#666;font-size:12px">Questions, or want a paper copy? Reply to this email or write to info@costamesajiujitsu.com.</p>',
      attachments: [pdf],
      name: 'Costa Mesa Jiu Jitsu',
      replyTo: 'info@costamesajiujitsu.com'
    });
  }
  return json({ ok: true, waiver: true, id: id });
}

/** The frozen agreement text for a version, from the site that sent the waiver (cached for 6 hours). */
function waiverTerms(version, host) {
  if (version === 'unknown') return '';
  host = String(host || '').toLowerCase();
  const site = OUR_HOSTS.indexOf(host) > -1 && host !== 'localhost' ? 'https://' + host : 'https://costamesajiujitsu.com';
  const key = 'terms-' + site + '-' + version, cache = CacheService.getScriptCache();
  const hit = cache.get(key);
  if (hit) return hit;
  try {
    const res = UrlFetchApp.fetch(site + '/waiver/terms/' + version + '.html', { muteHttpExceptions: true, followRedirects: true });
    const m = res.getResponseCode() === 200 && res.getContentText().match(/<!--TERMS-->([\s\S]*?)<!--\/TERMS-->/);
    if (!m) return '';
    const body = m[1].replace(/<script[\s\S]*?<\/script>/gi, '');
    if (body.length < 90000) cache.put(key, body, 21600);
    return body;
  } catch (err) {
    return '';
  }
}

function waiverFolder() {
  const it = DriveApp.getFoldersByName(WAIVER_FOLDER);
  return it.hasNext() ? it.next() : DriveApp.createFolder(WAIVER_FOLDER);
}

function waiverSheet() {
  const ss = SpreadsheetApp.getActive();
  let sh = ss.getSheetByName(WAIVER_SHEET);
  if (!sh) {
    sh = ss.insertSheet(WAIVER_SHEET);
    const head = ['Signed at', 'Confirmation', 'Signed by', 'Email', 'Phone', 'Signer DOB', 'Waiver covers', 'Relationship', 'Children (DOB)', 'Emergency contact', 'Medical notes', 'Photos OK', 'Agreement version', 'PDF'];
    sh.getRange(1, 1, 1, head.length).setValues([head]).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

/** Run once from the editor (select testWaiverEmail, click Run) to send yourself a sample signed waiver. */
function testWaiverEmail() {
  const out = handleWaiver({ kind: 'waiver', mode: 'both', name: 'Mitchell Testing', dob: '1990-01-01', email: 'mitchell@socialupgrades.com', phone: '9495550123',
    relationship: 'Parent', minor_1_name: 'Kid Testing', minor_1_dob: '2016-05-05', minor_1_sig: 'Kid Testing', emergency_name: 'Test Contact', emergency_phone: '9495550199',
    emergency_relationship: 'Spouse', medical: '', init_risk: 'MT', init_release: 'MT', init_indemnity: 'MT', init_info: 'MT', init_minors: 'MT', media: 'no',
    typed_name: 'Mitchell Testing', version: '2026-11-22', host: 'staging--costa-mesa-jiu-jitsu.netlify.app', page: '/waiver/', ms: '120000' });
  Logger.log(out.getContent());
}
