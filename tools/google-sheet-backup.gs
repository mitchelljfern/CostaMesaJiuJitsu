/**
 * Costa Mesa Jiu Jitsu: website lead backup + spam check
 *
 * Every form on costamesajiujitsu.com (free class, kids class, private lessons, rashguard)
 * sends its details here first (assets/lead-gate.js). This script:
 *   1. checks the invisible Cloudflare Turnstile token and a few bot signals,
 *   2. saves real leads to the "Leads" tab and spam to the "Spam" tab (created automatically),
 *   3. answers the website: real leads are then passed on to HighLevel, spam never reaches it.
 * It runs separately from HighLevel, so leads are kept even if HighLevel has a problem.
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
const ALERT_EMAIL = '';   // for example 'info@costamesajiujitsu.com'. Leave empty for no emails.
const OUR_HOSTS = ['costamesajiujitsu.com', 'www.costamesajiujitsu.com', 'costa-mesa-jiu-jitsu.netlify.app', 'staging--costa-mesa-jiu-jitsu.netlify.app', 'localhost'];

function doPost(e) {
  const p = (e && e.parameter) || {};
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
          subject: 'New website lead: ' + (p.form || 'form') + ' from ' + (p.name || 'someone'),
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
  const caseFlips = (name.match(/[a-z](?=[A-Z])|[A-Z](?=[a-z])/g) || []).length;

  if (ts === null) add(1, 'no Turnstile token');
  if (p.ms && Number(p.ms) < 3000) add(1, 'sent within 3 seconds of opening the page');
  if (p.touched === '0') add(1, 'no tap, click or keypress on the page');
  if (name && !/\s/.test(name) && name.length >= 10 && caseFlips >= 8) add(1, 'random-letter name');
  if (/@(gmail|googlemail)\./.test(email) && (local.match(/\./g) || []).length >= 3) add(1, 'dotted-up Gmail address');
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
