/**
 * Costa Mesa Jiu Jitsu: website lead backup
 *
 * Every form on costamesajiujitsu.com (free class, kids class, private lessons, rashguard)
 * also sends its details here, and this script adds a row to the "Leads" tab.
 * It runs separately from HighLevel, so leads are kept even if HighLevel has a problem.
 *
 * Setup (one time, about 2 minutes):
 *   1. Open the "CMJJ Website Leads (backup)" Google Sheet.
 *   2. Extensions > Apps Script. Delete what's there, paste this whole file, click Save.
 *   3. Optional: put an email address in ALERT_EMAIL below to get an email for every lead.
 *   4. Deploy > New deployment > gear icon > Web app.
 *        Execute as: Me
 *        Who has access: Anyone
 *      Click Deploy, approve the Google permission prompts, and copy the Web app URL.
 *   5. Send that URL to whoever maintains the site. It goes in SHEET_BACKUP_URL.
 *
 * If you ever edit this script: Deploy > Manage deployments > edit (pencil) > Version: New version > Deploy.
 * The URL stays the same.
 */

const SHEET_NAME = 'Leads';
const ALERT_EMAIL = '';   // for example 'info@costamesajiujitsu.com'. Leave empty for no emails.

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.tryLock(10000);
  try {
    const p = (e && e.parameter) || {};
    if (p.website) return json({ ok: true });            // spam trap: real visitors never fill this in

    const clean = (v) => {
      v = String(v == null ? '' : v).slice(0, 500);
      return /^[=+\-@]/.test(v) ? "'" + v : v;          // keep spreadsheet formulas out
    };
    const classOrItem = p.cls || (p.size ? [p.size, p.rank ? p.rank + ' belt' : ''].filter(String).join(', ') : '');

    const row = [
      new Date(), p.form, p.name, p.phone, p.email, p.age || p.who, classOrItem, p.when, p.goal, p.coach,
      p.heard, p.page, p.utm_source, p.utm_medium, p.utm_campaign, p.utm_content, p.utm_term, p.referrer
    ].map((v, i) => (i === 0 ? v : clean(v)));

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
    return json({ ok: true });
  } finally {
    lock.releaseLock();
  }
}

function doGet() {
  return json({ ok: true, message: 'CMJJ lead backup is running.' });
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
