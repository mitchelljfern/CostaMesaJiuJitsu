/* Costa Mesa Jiu Jitsu: lead form spam check (every page).
 *
 * How a form submission flows:
 *   1. This script catches the click/submit first, before HighLevel's tracker can see it.
 *   2. It checks the form is filled in, gets an invisible Cloudflare Turnstile token (no puzzle),
 *      and sends everything to the Google Apps Script (tools/google-sheet-backup.gs).
 *   3. The Apps Script verifies the token, scores the lead and saves it:
 *        real lead -> "Leads" tab, and this script releases the submission so HighLevel captures it
 *        spam      -> "Spam" tab only; HighLevel never sees it and the bot just gets a thank-you screen
 *   If the check itself fails to answer (timeout, Google down), the lead goes through so nothing real is lost.
 *
 * Settings: TURNSTILE_SITEKEY (public key from Cloudflare) and SHEET_URL (Apps Script web app URL).
 */
(function () {
  var TURNSTILE_SITEKEY = '';
  var SHEET_URL = 'https://script.google.com/macros/s/AKfycbyZ0EI_Cq5wvFBlQ_vXDkqYB94jN8FJrmQJZ3XB3CKEXAgRZ8D8JnHimtU3FHQbKXPN/exec';
  var HP = 'company_site';                 // hidden spam-trap field; people never see or fill it
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  var started = Date.now(), touched = false, ts = { loading: null, ids: {} };

  window.CMJJ_GATE = true;

  ['pointerdown', 'keydown', 'touchstart'].forEach(function (t) {
    window.addEventListener(t, function () { touched = true; }, { capture: true, passive: true });
  });

  function isLead(f) { return f && f.tagName === 'FORM' && f.hasAttribute('data-lead'); }
  function label(f) {
    var l = f.getAttribute('data-lead') || 'form';
    if (location.pathname.indexOf('/kids-jiu-jitsu') === 0 && /free/.test(l)) l = 'kids free class';
    return l.charAt(0).toUpperCase() + l.slice(1);
  }
  function adTags() {
    var q = new URLSearchParams(location.search), o = {};
    if (UTM_KEYS.some(function (k) { return q.get(k); })) {
      UTM_KEYS.forEach(function (k) { o[k] = q.get(k) || ''; });
      try { sessionStorage.setItem('cmjj-utm', JSON.stringify(o)); } catch (e) {}
      return o;
    }
    try { return JSON.parse(sessionStorage.getItem('cmjj-utm') || '{}'); } catch (e) { return {}; }
  }
  adTags();

  // Add the hidden spam-trap field to every lead form
  function addTrap(f) {
    if (f.querySelector('[name="' + HP + '"]')) return;
    var w = document.createElement('div');
    w.setAttribute('aria-hidden', 'true');
    w.style.cssText = 'position:absolute!important;left:-9999px!important;width:1px;height:1px;overflow:hidden';
    w.innerHTML = '<label>Company website<input type="text" name="' + HP + '" tabindex="-1" autocomplete="off"></label>';
    f.appendChild(w);
  }

  // Cloudflare Turnstile (invisible): loads the first time someone starts on a form
  function loadTurnstile(cb) {
    if (!TURNSTILE_SITEKEY) return cb && cb();
    if (window.turnstile) return cb && cb();
    if (!ts.loading) {
      ts.loading = [];
      window.cmjjTsReady = function () { var q = ts.loading; ts.loading = 'done'; q.forEach(function (fn) { fn(); }); };
      var s = document.createElement('script');
      s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=cmjjTsReady';
      s.async = true; s.defer = true;
      document.head.appendChild(s);
    }
    if (cb && ts.loading !== 'done') ts.loading.push(cb);
  }
  function widget(f) {
    if (!TURNSTILE_SITEKEY || !window.turnstile) return null;
    var id = f.id || 'f';
    if (ts.ids[id] == null) {
      var box = document.createElement('div');
      box.className = 'cf-turnstile-box';
      f.appendChild(box);
      try { ts.ids[id] = window.turnstile.render(box, { sitekey: TURNSTILE_SITEKEY, size: 'flexible', appearance: 'interaction-only', 'refresh-expired': 'auto', action: 'lead' }); }
      catch (e) { ts.ids[id] = false; }
    }
    return ts.ids[id] === false ? null : ts.ids[id];
  }
  function getToken(f, done) {
    if (!TURNSTILE_SITEKEY) return done('');
    var t0 = Date.now();
    loadTurnstile(function () {
      var id = widget(f);
      (function poll() {
        var tok = '';
        try { tok = id != null ? window.turnstile.getResponse(id) || '' : ''; } catch (e) {}
        if (tok || Date.now() - t0 > 6000) return done(tok);
        setTimeout(poll, 150);
      })();
    });
  }
  function resetToken(f) {
    var id = ts.ids[f.id || 'f'];
    if (id != null && id !== false && window.turnstile) { try { window.turnstile.reset(id); } catch (e) {} }
  }

  function invalid(f) {
    var bad = Array.prototype.filter.call(f.querySelectorAll('[required]'), function (el) {
      return !el.value || (el.type === 'email' && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(el.value));
    });
    bad.forEach(function (el) { el.style.borderColor = '#f0544f'; });
    if (bad.length) bad[0].focus();
    return bad.length > 0;
  }

  function busy(f, on) {
    var b = f.querySelector('button[type="submit"], input[type="submit"]');
    if (!b) return;
    if (on) { b.disabled = true; b.setAttribute('aria-busy', 'true'); b.dataset.txt = b.innerHTML; b.textContent = 'Sending...'; }
    else { b.disabled = false; b.removeAttribute('aria-busy'); if (b.dataset.txt) b.innerHTML = b.dataset.txt; }
  }

  // Release a checked submission: HighLevel captures it and the page shows its confirmation
  function release(f) {
    var trap = f.querySelector('[name="' + HP + '"]');
    var holder = trap && trap.closest('div');
    if (holder) holder.remove();              // keep the trap field out of HighLevel
    var ev = new Event('submit', { bubbles: true, cancelable: true });
    ev.__gated = true;
    f.dispatchEvent(ev);
    if (window.gtag) window.gtag('event', 'generate_lead', { form_name: label(f) });
    addTrap(f);
  }
  // Spam: thank-you screen only, nothing sent to HighLevel
  function quietThanks(f) {
    var ok = document.getElementById(f.getAttribute('data-ok') || '');
    f.hidden = true;
    if (ok) { ok.querySelectorAll('[data-ok-name]').forEach(function (s) { s.textContent = 'friend'; }); ok.hidden = false; }
  }

  function check(f) {
    if (f.__sending) return;
    if (invalid(f)) return;
    f.__sending = true; busy(f, true);
    getToken(f, function (token) {
      var d = new URLSearchParams(new FormData(f)), t = adTags(), settled = false;
      d.set('form', label(f)); d.set('page', location.pathname); d.set('referrer', document.referrer || '');
      Object.keys(t).forEach(function (k) { d.set(k, t[k]); });
      d.set('hp', d.get(HP) || ''); d.delete(HP);
      d.set('ms', String(Date.now() - started)); d.set('touched', touched ? '1' : '0');
      d.set('cf_token', token); d.set('host', location.hostname);
      function finish(spam) {
        if (settled) return; settled = true;
        f.__sending = false; busy(f, false); resetToken(f);
        if (spam) quietThanks(f); else release(f);
      }
      if (!SHEET_URL || !window.fetch) return finish(false);
      var timer = setTimeout(function () { finish(false); }, 9000);   // no answer: let it through
      fetch(SHEET_URL, { method: 'POST', body: d })
        .then(function (r) { return r.json(); })
        .then(function (j) { clearTimeout(timer); finish(!!(j && j.spam)); })
        .catch(function () { clearTimeout(timer); finish(false); });
    });
  }

  // Stop HighLevel's tracker from seeing a submit-button click before the check runs.
  // The click still submits the form normally, which the listener below catches.
  window.addEventListener('click', function (e) {
    var b = e.target && e.target.closest && e.target.closest('button[type="submit"], input[type="submit"]');
    if (b && isLead(b.form)) e.stopImmediatePropagation();
  }, true);

  window.addEventListener('submit', function (e) {
    var f = e.target;
    if (!isLead(f) || e.__gated) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    check(f);
  }, true);

  function init() {
    document.querySelectorAll('form[data-lead]').forEach(function (f) {
      addTrap(f);
      f.addEventListener('focusin', function () { loadTurnstile(function () { widget(f); }); }, { once: true });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
