// Shared helpers for the Casa Alberto reels.
// Every reel exposes window.DURATION (seconds), window.renderFrame(t) and
// optionally window.SFX / window.MUSIC, which render.mjs reads when exporting.

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const E = {
  linear: t => t,
  inCubic: t => t * t * t,
  outCubic: t => 1 - Math.pow(1 - t, 3),
  inOutCubic: t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  outExpo: t => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  inExpo: t => (t === 0 ? 0 : Math.pow(2, 10 * t - 10)),
  outBack: t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  outElastic: t => (t === 0 || t === 1 ? t : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * (2 * Math.PI) / 3) + 1),
};
// Eased progress of an animation that starts at `start` and lasts `dur` seconds.
const prog = (t, start, dur, ease = E.outCubic) => ease(clamp((t - start) / dur));
// Visibility envelope: fades in over `fin` after `a`, fades out over `fout` before `b`.
const env = (t, a, b, fin = .35, fout = .3) => Math.min(prog(t, a, fin), 1 - prog(t, b - fout, fout, E.inCubic));
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];

function style(el, { x = 0, y = 0, s = 1, sx, sy, r = 0, o, blur, extra = '', center = false } = {}) {
  const base = center ? 'translate(-50%,-50%) ' : '';
  el.style.transform = `${base}translate(${x}px,${y}px) rotate(${r}deg) scale(${sx ?? s},${sy ?? s}) ${extra}`;
  if (o !== undefined) el.style.opacity = o;
  if (blur !== undefined) el.style.filter = blur > 0.05 ? `blur(${blur}px)` : 'none';
}

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Deterministic camera shake that decays from `start` over `dur` seconds.
function shake(t, start, dur, amp) {
  const k = clamp((t - start) / dur);
  if (k <= 0 || k >= 1) return { x: 0, y: 0, r: 0 };
  const a = amp * Math.pow(1 - k, 2);
  return { x: Math.sin(t * 91) * a, y: Math.cos(t * 77) * a, r: Math.sin(t * 53) * a * .04 };
}

// Vector recreation of the "De tapa en tapa · Casa Alberto" logo.
const LOGO_SVG = `
<svg viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;overflow:visible">
  <defs>
    <path id="logoArc" d="M 112 292 A 188 188 0 0 1 488 292"/>
  </defs>
  <circle cx="300" cy="280" r="238" fill="#931237"/>
  <circle cx="300" cy="280" r="228" fill="none" stroke="#fff" stroke-width="6"/>
  <circle cx="300" cy="280" r="150" fill="none" stroke="#fff" stroke-width="7"/>
  <text font-family="Inter" font-weight="800" font-size="54" fill="#fff" letter-spacing="1">
    <textPath href="#logoArc" startOffset="50%" text-anchor="middle">DE TAPA EN TAPA</textPath>
  </text>
  <path d="M 115 330 A 190 190 0 0 0 150 400" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="12 10" stroke-linecap="round"/>
  <path d="M 485 330 A 190 190 0 0 1 450 400" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="12 10" stroke-linecap="round"/>
  <g fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
    <!-- tap tower -->
    <path d="M 300 262 L 300 190"/>
    <path d="M 252 190 L 348 190"/>
    <path d="M 262 190 L 262 218 M 300 190 L 300 210 M 338 190 L 338 218"/>
    <path d="M 254 176 l 8 -40 l 8 40 z M 292 172 l 8 -40 l 8 40 z M 330 176 l 8 -40 l 8 40 z" fill="#fff"/>
    <path d="M 255 218 h 14 v 10 h -6 M 331 218 h 14 v 10 h -6"/>
    <!-- barrel -->
    <path d="M 248 262 Q 238 318 248 374 L 352 374 Q 362 318 352 262 Z"/>
    <path d="M 244 284 L 356 284 M 241 352 L 359 352"/>
    <path d="M 274 262 Q 268 318 274 374 M 300 262 L 300 374 M 326 262 Q 332 318 326 374"/>
  </g>
  <!-- ribbon -->
  <g stroke="#fff" stroke-width="6" stroke-linejoin="round">
    <path d="M 96 452 L 40 452 L 64 492 L 40 532 L 132 532 L 132 500 Z" fill="#931237"/>
    <path d="M 504 452 L 560 452 L 536 492 L 560 532 L 468 532 L 468 500 Z" fill="#931237"/>
    <path d="M 96 500 L 132 532 L 132 500 Z M 504 500 L 468 532 L 468 500 Z" fill="#5c0a22"/>
    <rect x="96" y="420" width="408" height="84" rx="4" fill="#931237"/>
  </g>
  <text x="300" y="481" font-family="Inter" font-weight="800" font-size="56" fill="#fff" text-anchor="middle" letter-spacing="1">CASA ALBERTO</text>
</svg>`;

// End card shared by every reel: <div id="end" data-headline="..."></div>
function mountEndCard() {
  const end = $('#end');
  if (!end) return;
  end.innerHTML = `
    <div id="rays"></div>
    <div id="endtop" class="anton"></div>
    <div id="endlogo" class="logo"></div>
    <div id="addr" class="bebas">C/ Muro 27 · Tudela</div>
    <div id="phone">📞 948 82 19 12</div>
    <div id="tags" class="bebas">Paletilla · Costillares · Cachopos</div>`;
  $('#endtop').textContent = end.dataset.headline || '';
  const rnd = mulberry32(7);
  for (let i = 0; i < 26; i++) {
    const s = document.createElement('div'); s.className = 'spark';
    Object.assign(s.dataset, { x: 80 + rnd() * 920, y: 200 + rnd() * 1500, p: rnd() * 6, k: .5 + rnd() });
    end.appendChild(s);
  }
}

function renderEnd(t, start) {
  const end = $('#end');
  const endIn = prog(t, start - .1, .45);
  end.style.opacity = endIn;
  end.style.display = endIn > 0 ? 'block' : 'none';
  if (endIn <= 0) return;
  $('#rays').style.transform = `rotate(${t * 12}deg)`;
  const lg = prog(t, start, .9, E.outBack);
  style($('#endlogo'), { center: true, s: .2 + .8 * lg + .015 * Math.sin(t * 3), r: (1 - lg) * -200, o: clamp(lg * 2) });
  const top = prog(t, start + .6, .5, E.outBack);
  style($('#endtop'), { y: (1 - top) * -80, o: top });
  const ad = prog(t, start + .9, .5, E.outBack);
  style($('#addr'), { y: (1 - ad) * 80, o: clamp(ad * 2) });
  const ph = prog(t, start + 1.15, .5, E.outBack);
  $('#phone').style.opacity = clamp(ph * 2);
  $('#phone').style.transform = `translateX(-50%) scale(${.5 + .5 * ph + (t > start + 2 ? .03 * Math.sin((t - start) * 6) : 0)})`;
  const tg = prog(t, start + 1.5, .5);
  style($('#tags'), { o: tg, y: (1 - tg) * 30 });
  $$('.spark').forEach(s => {
    const k = +s.dataset.k, p = +s.dataset.p;
    const y = +s.dataset.y - (t - start) * 90 * k;
    s.style.transform = `translate(${+s.dataset.x + Math.sin(t * k * 2 + p) * 30}px, ${y}px) scale(${.5 + .5 * Math.sin(t * 4 * k + p)})`;
    s.style.opacity = endIn * (.4 + .6 * Math.abs(Math.sin(t * 2 * k + p)));
  });
}

function mountLogos() { $$('.logo').forEach(el => { el.innerHTML = LOGO_SVG; }); }

// Overlays shared by every reel.
function mountOverlays() {
  const stage = $('#stage');
  for (const id of ['vignette', 'grain', 'flash']) {
    const d = document.createElement('div'); d.id = id; stage.appendChild(d);
  }
}
function overlays(t, flashes = []) {
  const g = $('#grain');
  const f = Math.floor(t * 24);
  g.style.transform = `translate(${(f * 37) % 120 - 60}px, ${(f * 53) % 120 - 60}px)`;
  let fl = 0;
  for (const [ft, dur = .25, peak = .85] of flashes) fl = Math.max(fl, peak * (1 - clamp((t - ft) / dur)) * (t >= ft ? 1 : 0));
  $('#flash').style.opacity = fl;
}

window.addEventListener('DOMContentLoaded', () => { mountEndCard(); mountLogos(); mountOverlays(); });
