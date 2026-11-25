/* Costa Mesa Jiu Jitsu: online liability waiver (/waiver/).
 * Collects the form, initials and a drawn signature, then posts it to the Google Apps Script
 * (tools/google-sheet-backup.gs, "kind=waiver"). The script builds the signed PDF from the frozen
 * terms at /waiver/terms/<version>.html, saves it, and emails it to the gym and the signer.
 * The page only shows success when the script confirms it saved the waiver.
 */
(function () {
  var CFG = window.CMJJ_WAIVER || {};
  var form = document.getElementById('waiverForm');
  if (!form) return;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var started = Date.now(), MAX_MINORS = 6, sending = false;
  var errBox = $('#wError'), btn = $('#wSubmit');

  function age(v) {
    if (!v) return null;
    var p = v.split('-'), d = new Date(+p[0], +p[1] - 1, +p[2]), t = new Date();
    if (isNaN(d) || d > t) return null;
    var a = t.getFullYear() - d.getFullYear();
    if (t.getMonth() < d.getMonth() || (t.getMonth() === d.getMonth() && t.getDate() < d.getDate())) a--;
    return a;
  }
  var today = new Date();
  var todayIso = today.getFullYear() + '-' + String(today.getMonth() + 1).padStart(2, '0') + '-' + String(today.getDate()).padStart(2, '0');
  $$('input[type="date"]').forEach(function (el) { el.max = todayIso; });
  $('#wDate').textContent = 'Date: ' + today.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

  // ---------------------------------------------------------------- who is it for
  var minorsStep = $('#wMinorsStep'), minorsBox = $('#wMinors'), tpl = $('#wMinorTpl'), addBtn = $('#wAddMinor');
  function mode() { var r = $('input[name="mode"]:checked'); return r ? r.value : ''; }
  function hasMinors() { return mode() === 'minors' || mode() === 'both'; }

  function renumber() {
    $$('.w-minor', minorsBox).forEach(function (m, i) {
      var n = i + 1;
      $('.w-n', m).textContent = n;
      $$('[data-f]', m).forEach(function (el) {
        var f = el.getAttribute('data-f');
        if (el.tagName === 'INPUT') { el.name = 'minor_' + n + '_' + f; el.id = 'wM' + n + f; var l = el.closest('.field') && $('label', el.closest('.field')); if (l) l.htmlFor = el.id; }
      });
      $('.w-remove', m).hidden = $$('.w-minor', minorsBox).length < 2;
    });
    addBtn.hidden = $$('.w-minor', minorsBox).length >= MAX_MINORS;
  }
  function checkMinor(m) {
    var a = age($('[data-f="dob"]', m).value), ack = $('[data-f="ackbox"]', m), sig = $('[data-f="sig"]', m);
    $('[data-f="adult"]', m).hidden = !(a !== null && a >= 18);
    var needsAck = a !== null && a >= 7 && a <= 17;
    ack.hidden = !needsAck; sig.required = needsAck;
  }
  function addMinor() {
    if ($$('.w-minor', minorsBox).length >= MAX_MINORS) return;
    var m = tpl.content.firstElementChild.cloneNode(true);
    $('[data-f="dob"]', m).max = todayIso;
    $('[data-f="dob"]', m).addEventListener('change', function () { checkMinor(m); });
    $('.w-remove', m).addEventListener('click', function () { m.remove(); renumber(); });
    minorsBox.appendChild(m);
    renumber();
    return m;
  }
  addBtn.addEventListener('click', function () { var m = addMinor(); if (m) $('[data-f="name"]', m).focus(); });

  function applyMode() {
    var kids = hasMinors();
    minorsStep.hidden = !kids;
    $$('input, select', minorsStep).forEach(function (el) { el.disabled = !kids; });
    if (kids && !$('.w-minor', minorsBox)) addMinor();
    $('#wRelBox').hidden = !kids; $('#wRel').required = kids;
    var mi = $('.w-init[data-init="minors"]');
    if (mi) { mi.hidden = !kids; $('input', mi).required = kids; }
    $('.w-choices').classList.remove('bad');
  }
  $$('input[name="mode"]').forEach(function (r) { r.addEventListener('change', applyMode); });

  // Initials: fill the rest once the first box is typed
  var inits = $$('.w-init input');
  inits.forEach(function (el) {
    el.addEventListener('input', function () { el.value = el.value.toUpperCase().replace(/[^A-Z.\- ]/g, ''); el.classList.remove('bad'); });
  });

  // ---------------------------------------------------------------- signature pad
  var c = $('#wSig'), ctx = c.getContext('2d'), strokes = [], cur = null, cw = 0;
  function setup() {
    var r = c.getBoundingClientRect(), s = window.devicePixelRatio || 1;
    if (!r.width || Math.round(r.width) === cw) return;
    cw = Math.round(r.width);
    c.width = Math.round(r.width * s); c.height = Math.round(r.height * s);
    ctx.setTransform(s, 0, 0, s, 0, 0);
    redraw(ctx, r.width, r.height);
  }
  function redraw(g, w, h) {
    g.clearRect(0, 0, w, h);
    g.lineWidth = Math.max(2, w / 260); g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = '#0b1215';
    strokes.forEach(function (st) {
      g.beginPath();
      st.forEach(function (p, i) { var x = p[0] * w, y = p[1] * h; if (i) g.lineTo(x, y); else { g.moveTo(x, y); g.lineTo(x + 0.01, y); } });
      g.stroke();
    });
  }
  function pt(e) { var r = c.getBoundingClientRect(); return [Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)), Math.min(1, Math.max(0, (e.clientY - r.top) / r.height))]; }
  c.addEventListener('pointerdown', function (e) { e.preventDefault(); c.setPointerCapture(e.pointerId); cur = [pt(e)]; strokes.push(cur); c.classList.remove('bad'); setupAndDraw(); });
  c.addEventListener('pointermove', function (e) { if (!cur) return; cur.push(pt(e)); setupAndDraw(); });
  ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (t) { c.addEventListener(t, function () { cur = null; }); });
  function setupAndDraw() { var r = c.getBoundingClientRect(); redraw(ctx, r.width, r.height); }
  $('#wSigClear').addEventListener('click', function () { strokes = []; setupAndDraw(); });
  window.addEventListener('resize', setup);
  setup();
  if (!cw) window.addEventListener('load', setup);
  function signed() {
    var n = 0, minX = 1, maxX = 0, minY = 1, maxY = 0;
    strokes.forEach(function (st) { st.forEach(function (p) { n++; minX = Math.min(minX, p[0]); maxX = Math.max(maxX, p[0]); minY = Math.min(minY, p[1]); maxY = Math.max(maxY, p[1]); }); });
    return n >= 12 && (maxX - minX) > 0.12;
  }
  function sigPng() {
    var o = document.createElement('canvas'); o.width = 900; o.height = 270;
    var g = o.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, o.width, o.height);
    redraw(g, o.width, o.height);
    return o.toDataURL('image/png');
  }

  // ---------------------------------------------------------------- validation
  function bad(el, on) { if (el) el.classList.toggle('bad', !!on); }
  $$('input, select, textarea', form).forEach(function (el) {
    el.addEventListener('input', function () { bad(el, false); errBox.hidden = true; });
    el.addEventListener('change', function () { bad(el, false); var a = el.closest('.agree, .w-choices'); if (a) bad(a, false); });
  });
  function validate() {
    var errs = [], first = null;
    $$('.bad', form).forEach(function (el) { el.classList.remove('bad'); });
    function fail(el, msg, mark) { if (mark !== false) bad(mark || el, true); if (!first) first = el; if (msg && errs.indexOf(msg) < 0) errs.push(msg); }
    if (!mode()) fail($('input[name="mode"]'), 'Choose who this waiver is for.', $('.w-choices'));
    $$('input[required], select[required], textarea[required]', form).forEach(function (el) {
      if (el.disabled || el.type === 'radio' || el.type === 'checkbox' || el.closest('[hidden]')) return;
      var v = el.value.trim();
      if (!v) return fail(el, 'Fill in every required field.');
      if (el.type === 'email' && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) fail(el, 'Check the email address.');
      if (el.type === 'tel' && v.replace(/\D/g, '').length < 10) fail(el, 'Check the phone numbers (10 digits).');
    });
    var a = age($('#wDob').value);
    if ($('#wDob').value && (a === null || a < 18)) fail($('#wDob'), 'The person signing must be 18 or older. Students under 18 need a parent or guardian to sign.');
    if (hasMinors()) {
      $$('.w-minor', minorsBox).forEach(function (m) {
        var d = $('[data-f="dob"]', m), ma = age(d.value);
        if (d.value && (ma === null || ma >= 18)) fail(d, 'Each child listed must be under 18. Students 18 and older sign their own waiver.');
      });
    }
    if (!$('input[name="media"]:checked')) fail($('input[name="media"]'), 'Choose yes or no for photos and video.', $$('.w-choices')[1]);
    $$('.agree input', form).forEach(function (el) { if (!el.checked) fail(el, 'Check both boxes above your signature.', el.closest('.agree')); });
    if (!signed()) fail(c, 'Draw your signature in the box.', c);
    return { errs: errs, first: first };
  }

  // ---------------------------------------------------------------- submit
  function sha256(text) {
    if (!window.crypto || !crypto.subtle || !window.TextEncoder) return Promise.resolve('');
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(text)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return x.toString(16).padStart(2, '0'); }).join('');
    }).catch(function () { return ''; });
  }
  function termsText() {   // the agreement as read, without the initials boxes
    var t = $('#wTerms').cloneNode(true);
    $$('.w-init', t).forEach(function (el) { el.remove(); });
    return t.textContent.replace(/\s+/g, ' ').trim();
  }
  function showError(msg) { errBox.textContent = msg; errBox.hidden = false; }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    if (sending) return;
    errBox.hidden = true;
    var v = validate();
    if (v.errs.length) {
      showError(v.errs.join(' '));
      if (v.first) { (v.first.type === 'radio' || v.first === c ? v.first.closest('.w-step, .field') : v.first).scrollIntoView({ behavior: 'smooth', block: 'center' }); if (v.first.focus && v.first !== c) setTimeout(function () { v.first.focus({ preventScroll: true }); }, 350); }
      return;
    }
    if (!CFG.url || !window.fetch) return showError('Online signing is not available in this browser. Please call or text 949-556-1178 and we will send you a waiver.');
    sending = true; btn.disabled = true; btn.textContent = 'Saving your waiver...';
    var d = new URLSearchParams(new FormData(form));
    d.set('kind', 'waiver'); d.set('version', CFG.version || ''); d.set('host', location.hostname); d.set('page', location.pathname);
    d.set('hp', d.get('company_site') || ''); d.delete('company_site');
    d.set('ms', String(Date.now() - started));
    d.set('signature', sigPng());
    d.set('client_time', new Date().toISOString());
    try { d.set('client_tz', Intl.DateTimeFormat().resolvedOptions().timeZone || ''); } catch (er) {}
    d.set('ua', navigator.userAgent.slice(0, 300));
    if (!hasMinors()) $$('input', minorsBox).forEach(function (el) { d.delete(el.name); });
    sha256(termsText()).then(function (hash) {
      d.set('terms_hash', hash);
      var ctrl = window.AbortController ? new AbortController() : null;
      var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 45000);
      return fetch(CFG.url, { method: 'POST', body: d, signal: ctrl ? ctrl.signal : undefined })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          clearTimeout(timer);
          if (!j || !j.ok || !j.waiver) throw new Error((j && j.error) || 'not saved');
          $('#wOkName').textContent = ($('#wName').value.trim().split(' ')[0]) || 'friend';
          $('#wOkEmail').textContent = $('#wEmail').value.trim();
          $('#wOkId').textContent = j.id || '';
          form.hidden = true; $('#waiverOk').hidden = false;
          $('#waiverOk').scrollIntoView({ behavior: 'smooth', block: 'center' });
          if (window.gtag) window.gtag('event', 'waiver_signed', { waiver_for: mode() });
        });
    }).catch(function () {
      sending = false; btn.disabled = false; btn.textContent = 'Sign waiver';
      showError('Sorry, your waiver did not go through. Please check your connection and tap Sign waiver again. If it keeps happening, call or text 949-556-1178.');
    });
  }, true);
})();
