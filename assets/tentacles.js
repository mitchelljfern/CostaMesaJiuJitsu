/* Costa Mesa Jiu Jitsu: octopus tentacles that weave down the page edges.
 *
 * Each tentacle is drawn from a smooth centerline (a curve through a few anchor points that
 * ends in a curled tip). It tapers from base to tip and copies the logo's style: cyan body,
 * dark outline with a glowing rim, highlight and shadow streaks, and sand sucker rings.
 *
 * On wide screens the tentacles live in the side margins and slip behind cards and photo
 * bands. On phones, small tentacle tips peek in from the edges in the gaps between sections,
 * never over text. They draw in as you scroll (all at once if the visitor prefers less motion).
 *
 * window.CMJJTentacle.svg(opts) also builds a stand-alone tentacle (used on /brand-kit).
 */
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  var seq = 0;
  var C = { body: '#0fc3d8', rim: '#68faff', ink: '#03161b', deep: '#013243', glow: '#9ffcff', sand: '#f9d1a8' };

  // ---------- geometry ----------
  function catmull(pts, steps) {
    var out = [];
    for (var i = 0; i < pts.length - 1; i++) {
      var p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
      for (var t = 0; t < 1; t += 1 / steps) {
        var t2 = t * t, t3 = t2 * t;
        out.push([
          0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
          0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
        ]);
      }
    }
    out.push(pts[pts.length - 1]);
    return out;
  }
  function curl(line, r0, turns, dir) {
    var a = line[line.length - 2], b = line[line.length - 1];
    var th = Math.atan2(b[1] - a[1], b[0] - a[0]), x = b[0], y = b[1], turned = 0, max = turns * Math.PI * 2, ds = Math.max(1.2, r0 / 14);
    while (turned < max) {
      var k = turned / max, r = r0 * (1 - 0.78 * k);
      var dth = ds / r; th += dth * dir; turned += dth;
      x += Math.cos(th) * ds; y += Math.sin(th) * ds;
      line.push([x, y]);
    }
    return line;
  }
  function resample(line, step) {
    var out = [line[0]], S = [0], acc = 0, carry = 0;
    for (var i = 1; i < line.length; i++) {
      var p = line[i - 1], q = line[i], d = Math.hypot(q[0] - p[0], q[1] - p[1]);
      while (carry + d >= step) {
        var t = (step - carry) / d; p = [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t];
        d = Math.hypot(q[0] - p[0], q[1] - p[1]); carry = 0; acc += step; out.push(p); S.push(acc);
      }
      carry += d;
    }
    return { pts: out, S: S, L: acc };
  }
  function normals(pts) {
    return pts.map(function (p, i) {
      var a = pts[Math.max(0, i - 2)], b = pts[Math.min(pts.length - 1, i + 2)];
      var dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1;
      return [-dy / l, dx / l];
    });
  }
  function f(n) { return Math.round(n * 10) / 10; }
  // closed outline of a strip that follows the centerline: offset (fraction of width) and width fraction
  function strip(R, N, W, off, frac, from, to) {
    var a = [], b = [], i0 = Math.floor(from * (R.pts.length - 1)), i1 = Math.floor(to * (R.pts.length - 1));
    for (var i = i0; i <= i1; i++) {
      var p = R.pts[i], n = N[i], w = W[i], c = off * w, h = frac * w / 2;
      a.push(f(p[0] + n[0] * (c + h)) + ' ' + f(p[1] + n[1] * (c + h)));
      b.push(f(p[0] + n[0] * (c - h)) + ' ' + f(p[1] + n[1] * (c - h)));
    }
    return 'M' + a.join('L') + 'L' + b.reverse().join('L') + 'Z';
  }

  // ---------- one tentacle as SVG markup ----------
  // opts: points [[x,y]...], w (base width), curl {r, turns, dir}, side (+1/-1 = which edge the suckers sit on), id
  function build(o) {
    var line = catmull(o.points, 28);
    if (o.curl) curl(line, o.curl.r, o.curl.turns, o.curl.dir);
    var R = resample(line, Math.max(2, o.w / 14)), N = normals(R.pts), side = o.side || 1;
    var W = R.S.map(function (s) { var u = s / R.L; return o.w * Math.pow(1 - u, 1.05) + Math.max(1.4, o.w * 0.035); });
    var body = strip(R, N, W, 0, 1, 0, 1);
    var center = 'M' + R.pts.map(function (p) { return f(p[0]) + ' ' + f(p[1]); }).join('L');
    var rimW = Math.max(2, o.w * 0.11), inkW = Math.max(1.4, o.w * 0.06);
    var g = '';
    g += '<path d="' + body + '" fill="none" stroke="' + C.rim + '" stroke-width="' + f(rimW + inkW) + '" stroke-linejoin="round" opacity="0.85"/>';
    g += '<path d="' + body + '" fill="' + C.body + '" stroke="' + C.ink + '" stroke-width="' + f(inkW) + '" stroke-linejoin="round"/>';
    // soft shading, kept inside the body outline
    var uid = 't' + (++seq), soft = Math.max(0.6, o.w * 0.07);
    g += '<clipPath id="' + uid + 'c"><path d="' + body + '"/></clipPath><filter id="' + uid + 'f" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="' + f(soft) + '"/></filter>';
    g += '<g clip-path="url(#' + uid + 'c)"><g filter="url(#' + uid + 'f)">';
    g += '<path d="' + strip(R, N, W, -0.34 * side, 0.42, 0, 1) + '" fill="' + C.deep + '" opacity="0.7"/>';
    g += '<path d="' + strip(R, N, W, 0.18 * side, 0.22, 0, 0.98) + '" fill="' + C.glow + '" opacity="0.75"/>';
    g += '</g><path d="' + strip(R, N, W, -0.04 * side, 0.035, 0.02, 0.88) + '" fill="' + C.ink + '" opacity="0.22"/></g>';
    // suckers along one edge, from a quarter of the way to near the tip
    var su = '', s = R.L * (o.peek ? 0.3 : 0.34), ringStroke = Math.max(0.8, o.w * 0.025);
    while (s < R.L * 0.965) {
      var i = Math.min(R.pts.length - 1, Math.round(s / R.L * (R.pts.length - 1))), w = W[i], p = R.pts[i], n = N[i];
      var r = Math.max(1.5, w * 0.22), off = -side * w * 0.38;
      su += '<circle cx="' + f(p[0] + n[0] * off) + '" cy="' + f(p[1] + n[1] * off) + '" r="' + f(r) + '" fill="' + C.sand + '" stroke="' + C.ink + '" stroke-width="' + f(ringStroke) + '"/>';
      if (r > 2) su += '<circle cx="' + f(p[0] + n[0] * off) + '" cy="' + f(p[1] + n[1] * off) + '" r="' + f(r * 0.42) + '" fill="' + C.deep + '"/>';
      s += Math.max(r * 2.95, 4.5);
    }
    g += su;
    return { g: g, center: center, L: R.L, w: o.w };
  }

  // stand-alone SVG string (brand kit)
  function svg(o) {
    var t = build(o), vb = o.viewBox || '0 0 400 600';
    return '<svg xmlns="' + NS + '" viewBox="' + vb + '" role="img" aria-label="Octopus tentacle">' + t.g + '</svg>';
  }
  window.CMJJTentacle = { build: build, svg: svg };

  // ---------- page layer ----------
  var main = document.querySelector('main'), layer, items = [], best = [], raf = 0;
  if (!main || !document.querySelector('[data-tentacles]')) return;
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function box(sel) {
    var el = document.querySelector(sel); if (!el) return null;
    var r = el.getBoundingClientRect(), m = main.getBoundingClientRect();
    return { top: r.top - m.top, bottom: r.bottom - m.top, mid: (r.top + r.bottom) / 2 - m.top };
  }
  function plan(vw) {
    var wrap = document.querySelector('#programs .wrap'); if (!wrap) return [];
    var cs = getComputedStyle(wrap), left = wrap.getBoundingClientRect().left + parseFloat(cs.paddingLeft);
    var gut = left, list = [];
    var P = box('#programs'), B = box('#beginners'), S = box('#schedule'), PR = box('#pricing'), FC = box('#free-class'),
        K = box('#kids'), CO = box('#coaches'), PV = box('#privates'), IG = box('#instagram'), SH = box('#shop'), FQ = box('#faq'), CT = box('#contact');
    if (gut >= 72) {
      // wide screens: long tentacles in the side margins
      var w = Math.max(26, Math.min(62, gut * 0.4)), R = function (k) { return vw - gut * k; }, L = function (k) { return gut * k; };
      if (P && B) list.push({ side: -1, w: w, points: [[vw + w, P.top - 160], [R(0.3), P.top + 60], [R(0.62), P.mid - 40], [R(0.4), P.bottom - 120], [R(0.66), B.top + 40], [R(0.5), B.mid]], curl: { r: w * 1.05, turns: 1.15, dir: 1 } });
      if (S && PR) list.push({ side: 1, w: w, points: [[-w, S.top - 40], [L(0.32), S.top + 140], [L(0.6), S.mid], [L(0.36), S.bottom - 40], [L(0.62), PR.top + 120], [L(0.48), PR.mid + 30]], curl: { r: w * 1.05, turns: 1.2, dir: -1 } });
      if (FC && K && CO) list.push({ side: -1, w: w * 0.9, points: [[vw + w, K.top - 30], [R(0.58), K.top + 80], [R(0.36), K.mid], [R(0.62), K.bottom - 30], [R(0.46), CO.top + 90], [R(0.56), CO.mid + 40]], curl: { r: w * 0.95, turns: 1.1, dir: 1 } });
      if (IG && SH) list.push({ side: 1, w: w * 0.85, points: [[-w, IG.top + 30], [L(0.36), IG.mid], [L(0.62), IG.bottom - 20], [L(0.38), SH.top + 120], [L(0.56), SH.mid]], curl: { r: w * 0.9, turns: 1.15, dir: -1 } });
      if (FQ && CT) list.push({ side: -1, w: w * 0.8, points: [[vw + w, CT.top - 20], [R(0.6), CT.top + 90], [R(0.4), CT.mid], [R(0.55), CT.bottom - 60]], curl: { r: w * 0.85, turns: 1.2, dir: 1 } });
    } else {
      // phones and tablets: small tips peeking in from the edge, centered in the gap above a section
      var pw = vw < 480 ? 15 : 19;
      function peek(at, fromRight, dip) {
        if (!at) return;
        var y = at.top + (dip || 0), x0 = fromRight ? vw + 24 : -24, k = fromRight ? -1 : 1;
        list.push({ side: fromRight ? -1 : 1, w: pw, points: [[x0, y - 26], [x0 + k * 40, y - 6], [x0 + k * 70, y - 12]], curl: { r: pw * 0.95, turns: 1.15, dir: fromRight ? -1 : 1 }, peek: true });
      }
      peek(S, true); peek(FC, false, -30); peek(CO, true); peek(SH, false); peek(CT, true, 30);
    }
    return list;
  }

  function render() {
    var vw = document.documentElement.clientWidth, h = main.scrollHeight;
    if (!layer) {
      layer = document.createElementNS(NS, 'svg');
      layer.setAttribute('class', 'tentacles'); layer.setAttribute('aria-hidden', 'true'); layer.setAttribute('focusable', 'false');
      main.insertBefore(layer, main.firstChild);
    }
    layer.setAttribute('viewBox', '0 0 ' + vw + ' ' + h);
    layer.setAttribute('width', vw); layer.setAttribute('height', h);
    var defs = '', body = '', key = vw + 'x' + h;
    items = plan(vw).map(function (o, i) {
      var t = build(o), id = 'tm' + i;
      defs += '<mask id="' + id + '" maskUnits="userSpaceOnUse" x="-200" y="-200" width="' + (vw + 400) + '" height="' + (h + 400) + '"><path d="' + t.center + '" fill="none" stroke="#fff" stroke-width="' + Math.round(o.w * 2.6 + 16) + '" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="' + Math.ceil(t.L + 2) + '" stroke-dashoffset="' + Math.ceil(t.L + 2) + '"/></mask>';
      body += '<g class="tentacle" mask="url(#' + id + ')">' + t.g + '</g>';
      var ys = o.points.map(function (p) { return p[1]; });
      return { L: t.L, y0: Math.min.apply(null, ys), y1: Math.max.apply(null, ys) + o.w * 2 };
    });
    layer.innerHTML = '<defs>' + defs + '</defs>' + body;
    if (layer.__key !== key) best = [];
    layer.__key = key;
    items.forEach(function (it, i) { it.mask = layer.querySelectorAll('mask path')[i]; });
    draw();
  }

  function draw() {
    raf = 0;
    var mtop = main.getBoundingClientRect().top + window.scrollY, edge = window.scrollY + window.innerHeight * 0.9 - mtop;
    items.forEach(function (it, i) {
      var p = still ? 1 : Math.max(0, Math.min(1, (edge - it.y0) / Math.max(200, (it.y1 - it.y0) * 0.9)));
      if (p < (best[i] || 0)) p = best[i];          // drawn once; doesn't retract when scrolling back up
      best[i] = p;
      it.mask.setAttribute('stroke-dashoffset', String(Math.ceil((it.L + 2) * (1 - p))));
    });
  }
  function onScroll() { if (!raf) raf = requestAnimationFrame(draw); }

  var t = 0;
  function soon() { clearTimeout(t); t = setTimeout(render, 160); }
  if ('ResizeObserver' in window) new ResizeObserver(soon).observe(main); else window.addEventListener('resize', soon);
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('load', soon);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(soon);
  render();
})();
