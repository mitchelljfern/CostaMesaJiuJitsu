(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Google Sheet lead backup (tools/google-sheet-backup.gs). Runs alongside HighLevel. Leave the URL empty to switch off.
  var SHEET_BACKUP_URL = '';
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
