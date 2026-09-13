/* Verification for visual pass 2. Boots the file under jsdom with a recording
   context, then exercises the masthead, the ops dock and the routing. */
import { JSDOM } from 'jsdom';
import fs from 'node:fs';

const file = process.argv[2];
let fails = 0, passes = 0;
const check = (n, c, x='') => { if (c) { passes++; console.log('  PASS  ' + n); }
  else { fails++; console.log('  FAIL  ' + n + (x ? '  — ' + x : '')); } };

const calls = { styles: [] };
const makeCtx = () => { const noop = () => {};
  const ctx = new Proxy({}, { get(t, k) {
    if (k === 'fill') return () => calls.styles.push(ctx.fillStyle);
    if (k === 'measureText') return () => ({ width: 10 });
    if (k === 'createLinearGradient' || k === 'createRadialGradient') return () => ({ addColorStop: noop });
    if (k === 'getImageData') return () => ({ data: new Uint8ClampedArray(4) });
    if (k === 'canvas') return { width: 800, height: 600 };
    return (k in t) ? t[k] : noop;
  }, set(t, k, v) { t[k] = v; return true; } });
  return ctx; };

const dom = new JSDOM(fs.readFileSync(file, 'utf8'), {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://local.test/',
  beforeParse(win) {
    win.HTMLCanvasElement.prototype.getContext = makeCtx;
    win.HTMLCanvasElement.prototype.getBoundingClientRect = () => ({ width: 800, height: 600, top: 0, left: 0, right: 800, bottom: 600 });
    win.matchMedia = () => ({ matches: false, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {} });
    win.requestAnimationFrame = () => 0; win.cancelAnimationFrame = () => {};
    win.fetch = () => Promise.reject(new Error('offline'));
    win.scrollTo = () => {}; win.tailwind = { config: {} };
  }
});
const w = dom.window;
await new Promise(r => setTimeout(r, 700));
const ev = src => w.eval(src);

// ── A. verdict masthead ─────────────────────────────────────────────────────
check('verdictMasthead defined', typeof w.verdictMasthead === 'function');
check('scoring exposes evIdx', ev('typeof confidenceScore==="function" ? (confidenceScore().evIdx!=null) : false'));

if (typeof w.verdictMasthead === 'function') {
  const cs = ev('confidenceScore()');
  const html = w.verdictMasthead(cs);
  check('masthead prints the call', html.includes(cs.verdict), cs.verdict);
  check('masthead prints the score', html.includes('>' + cs.score + '<'), String(cs.score));
  check('masthead prints the evidence floor',
    /Measured · floor \d+%/.test(html));
  check('masthead tone matches the call',
    html.includes('vsh-' + (cs.verdict === 'GO' ? 'ok' : cs.verdict === 'CONDITIONAL' ? 'amber' : 'warn')));

  // a held verdict must state the reason, not bury it
  const held = Object.assign({}, cs, { verdict: 'CONDITIONAL', override: 'Held for testing.' });
  check('held verdict prints the holding reason',
    w.verdictMasthead(held).includes('vsh-hold') && w.verdictMasthead(held).includes('Held for testing.'));
  check('clean verdict prints no holding block',
    !w.verdictMasthead(Object.assign({}, cs, { override: null })).includes('vsh-hold'));

  // it must survive being rendered into the report tab
  let threw = null;
  try { ev('setTab("rep")'); } catch (e) { threw = e; }
  const rep = w.document.getElementById('stage-rep');
  check('report tab renders with the masthead', threw === null && rep && rep.innerHTML.includes('vsh-call'),
    threw ? threw.message : '');
}

// ── B. ops channel ──────────────────────────────────────────────────────────
const dock = w.document.getElementById('merDock');
check('ops dock exists', !!dock);
check('ops dock is not hidden on phones', dock && !/\bhidden\b/.test(dock.className), dock ? dock.className : '');
check('arrival animation is defined', w.document.documentElement.innerHTML.includes('@keyframes merArrive'));

// ── C. cross-aisle routing ──────────────────────────────────────────────────
ev('if(!WORLD.rackBlocks || !WORLD.rackBlocks.length) spawnWorld();');
const bands = ev('aisleBands()');
const lanes = ev('crossLanes()');
check('rack bands derived from the layout', Array.isArray(bands) && bands.length > 0, `bands=${bands.length}`);
check('cross-aisles derived from the width', Array.isArray(lanes) && lanes.length >= 2, `lanes=${JSON.stringify(lanes)}`);
check('a run across the racking is detected',
  ev('crossesRack(-2, (WORLD.H||22)+2)') === true);
check('a move inside one aisle is not a crossing',
  ev('(function(){var b=aisleBands()[0]; return crossesRack(b[1]+0.3, b[1]+0.6);})()') === false);

// walk an agent from the far north of the shed to the dock face and watch it
const trace = ev(`(function(){
  var a={x:(WORLD.W||34)/2, y:-1.5, wps:[{x:(WORLD.W||34)/2, y:(WORLD.H||22)+1}], wi:0, speed:0.06, fatigue:0};
  var pts=[];
  for(var i=0;i<4000;i++){ moveAgent(a,1); pts.push([a.x,a.y,a.hdx,a.hdy]); }
  return {pts:pts, lanes:crossLanes(), bands:aisleBands()};
})()`);

const inBand = (y, bands) => bands.some(b => y > b[0] && y < b[1]);
const nearLane = (x, lanes) => Math.min(...lanes.map(L => Math.abs(L - x)));
const violations = trace.pts.filter(p => inBand(p[1], trace.bands) && nearLane(p[0], trace.lanes) > 0.75);
check('agent never stands inside racking away from a cross-aisle',
  violations.length === 0, `violations=${violations.length} of ${trace.pts.length}`);
check('agent actually traversed the building',
  trace.pts[trace.pts.length - 1][1] > (ev('WORLD.H||22') - 2),
  `end y=${trace.pts[trace.pts.length - 1][1].toFixed(2)}`);
check('heading recorded during travel',
  trace.pts.some(p => typeof p[2] === 'number' && (Math.abs(p[2]) > 0.1 || Math.abs(p[3]) > 0.1)));

// ── regression: the world still renders across a full day ───────────────────
let threw = null;
try { for (let hr = 0; hr < 24; hr++) { ev(`SIM.t=${hr * 3600}`); w.renderWorld(); } }
catch (e) { threw = e; }
check('renderWorld still runs 24 frames', threw === null, threw ? threw.message : '');
check('pass-1 lighting still painting',
  calls.styles.some(s => typeof s === 'string' && (s.startsWith('rgba(255,241,208') || s.startsWith('rgba(14,24,38'))));
check('pass-1 contact shadows still painting',
  calls.styles.some(s => s === 'rgba(28,38,52,.20)'));

console.log(`\n${passes} passed, ${fails} failed`);
process.exit(fails ? 1 : 0);
