#!/usr/bin/env python3
"""
Visual pass 2 for warehouse-tycoon_6.html
  A. Verdict masthead on the report tab (typography of the shareable artifact)
  B. Ops channel visible on mobile, arrival cue on new lines, agents grounded
  C. Cross-aisle routing so floor traffic stops walking through racking
Presentation and movement-path only. No financial or operational value is
authored here; evIdx is surfaced, not recomputed.
"""
import io

SRC = 'warehouse-tycoon_6.html'
OUT = 'warehouse-tycoon_7.html'
s = io.open(SRC, encoding='utf-8').read()
orig = len(s)
applied = []

def sub(name, anchor, new):
    global s
    n = s.count(anchor)
    assert n == 1, f'[{name}] anchor matched {n} times, expected 1'
    s = s.replace(anchor, new)
    applied.append(name)

# ═══ A. VERDICT MASTHEAD ════════════════════════════════════════════════════

# A1 — surface the evidence index that the verdict already turns on
sub('A1 expose evIdx',
"""  const flips = comp.slice().sort((a,b)=>a.v*a.w-b.v*b.w).slice(0,3).map(c=>flipText(c));
  return {score, verdict, comp, flips, override, pj, rr, marginY};""",
"""  const flips = comp.slice().sort((a,b)=>a.v*a.w-b.v*b.w).slice(0,3).map(c=>flipText(c));
  /* evIdx is already what holds a GO at CONDITIONAL. Returning it lets the
     masthead print the floor test next to the score instead of leaving the
     reader to infer why a 74 did not clear. Same value, no second call. */
  return {score, verdict, comp, flips, override, pj, rr, marginY, evIdx};""")

# A2 — masthead styles
sub('A2 masthead css',
"""  .report-doc{background:#FFFFFF;border:1px solid #D4DCE7}""",
"""  .report-doc{background:#FFFFFF;border:1px solid #D4DCE7}
  /* The verdict block is the one thing that leaves this app as an image, so it
     is set as a document masthead rather than a dashboard tile: serif call,
     tabular figures, and the holding reason stated instead of buried. */
  .vsh{border:1px solid #D4DCE7;background:#FBFBF7;padding:18px 20px;
       font-family:Georgia,"Iowan Old Style","Palatino Linotype",Palatino,serif}
  .vsh-top{display:flex;gap:22px;align-items:flex-start;flex-wrap:wrap}
  .vsh-eyebrow{font:700 10px ui-monospace,Menlo,monospace;letter-spacing:.1em;
       text-transform:uppercase;color:#5D6C81}
  .vsh-call{font-size:44px;line-height:1.02;letter-spacing:-.02em;margin:3px 0 7px;font-weight:400}
  .vsh-ok{color:#1D4B3C} .vsh-amber{color:#8A6410} .vsh-warn{color:#8C2E22}
  .vsh-sub{font-size:13.5px;line-height:1.6;max-width:58ch;color:#2A3648;margin:0}
  .vsh-figs{display:flex;gap:24px;flex:none;border-left:1px solid #D4DCE7;padding-left:20px}
  .vsh-fig{text-align:right;min-width:82px}
  .vsh-n{font:400 30px/1 ui-monospace,Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}
  .vsh-k{font:700 9.5px ui-monospace,Menlo,monospace;letter-spacing:.08em;
       text-transform:uppercase;color:#5D6C81;margin-top:5px}
  .vsh-bar{height:3px;background:#E3E6DE;margin-top:7px}
  .vsh-bar i{display:block;height:3px}
  .vsh-hold{font-size:12.5px;line-height:1.6;margin:14px 0 0;padding:10px 12px;
       background:#FBEFD9;border-left:3px solid #8A6410;color:#4A3A12}
  @media (max-width:820px){
    .vsh{padding:15px 15px} .vsh-call{font-size:31px}
    .vsh-figs{border-left:none;border-top:1px solid #D4DCE7;padding:13px 0 0;width:100%}
    .vsh-fig{text-align:left;flex:1} }
  @media print{ .vsh{background:#fff;border-color:#bbb} .vsh-hold{background:#fff} }""")

# A3 — replace the header tile with the masthead
sub('A3 masthead markup',
"""    <div class="flex items-center gap-5 card p-4">
      <div class="text-center flex-none"><div class="num font-bold text-4xl ${vc}">${cs.score}</div><div class="lbl">confidence / 100</div></div>
      <div class="flex-1"><div class="font-bold text-lg ${vc}">${cs.verdict}${cs.override?' — '+esc(cs.override):''}</div>
        <div class="text-[12px] text-mut mt-1">Weighted: ${cs.comp.map(c=>`${c.k} ${(c.w*100)}%`).join(' · ')}</div></div></div>""",
"""    ${verdictMasthead(cs)}""")

sub('A4b masthead function',
"""function flipText(c){""",
"""/* The shareable artifact. Reads top-down: what the call is, what carried it,
   what dragged, and — if the call is being held below GO — why, in a sentence
   a reader can act on. Every number here is read off cs; none is derived. */
function verdictMasthead(cs){
  const tone = cs.verdict==='GO'?'ok' : cs.verdict==='CONDITIONAL'?'amber' : 'warn';
  const hue  = tone==='ok'?'#1D4B3C' : tone==='amber'?'#8A6410' : '#8C2E22';
  const ranked = cs.comp.slice().sort((a,b)=>(b.v*b.w)-(a.v*a.w));
  const best = ranked[0], worst = ranked[ranked.length-1];
  const ev = Math.round((cs.evIdx!=null?cs.evIdx:0)*100);
  const evTone = ev>=Math.round(EV_GO_FLOOR*100) ? '#1D4B3C' : '#8A6410';
  const sub = `Carried by <b>${esc(best.k.toLowerCase())}</b>; held back by `
    + `<b>${esc(worst.k.toLowerCase())}</b>. `
    + (cs.verdict==='GO'
        ? 'The case clears both the scoring threshold and the evidence floor.'
        : cs.verdict==='CONDITIONAL'
          ? 'Committable only against the conditions listed below.'
          : 'Not recommended for capital at the current configuration.');
  return `
  <div class="vsh">
    <div class="vsh-top">
      <div class="flex-1 min-w-0">
        <div class="vsh-eyebrow">Recommendation to the investment committee</div>
        <h2 class="vsh-call vsh-${tone}">${cs.verdict}</h2>
        <p class="vsh-sub">${sub}</p>
      </div>
      <div class="vsh-figs">
        <div class="vsh-fig"><div class="vsh-n" style="color:${hue}">${cs.score}</div>
          <div class="vsh-k">Score / 100</div>
          <div class="vsh-bar"><i style="width:${clamp(cs.score,0,100)}%;background:${hue}"></i></div></div>
        <div class="vsh-fig"><div class="vsh-n" style="color:${evTone}">${ev}%</div>
          <div class="vsh-k">Measured · floor ${Math.round(EV_GO_FLOOR*100)}%</div>
          <div class="vsh-bar"><i style="width:${clamp(ev,0,100)}%;background:${evTone}"></i></div></div>
      </div>
    </div>
    ${cs.override?`<p class="vsh-hold">${esc(cs.override)}</p>`:''}
  </div>`;
}
function flipText(c){""")

# ═══ B. OPS CHANNEL ═════════════════════════════════════════════════════════

# B1 — the dock was desktop-only, which is exactly where it gets demoed
sub('B1 dock on mobile',
"""      <div id="merDock" class="card p-2 text-[10.5px] space-y-0.5 no-print hidden sm:block">""",
"""      <div id="merDock" class="card p-2 text-[10.5px] space-y-0.5 no-print">""")

sub('B2 dock mobile css',
"""  #merDock{position:absolute;left:12px;bottom:12px;width:min(430px,58vw);max-height:132px;overflow:hidden}""",
"""  #merDock{position:absolute;left:12px;bottom:12px;width:min(430px,58vw);max-height:132px;overflow:hidden}
  /* Phone: the channel spans the foot of the stage instead of a 58vw sliver
     that could hold three words. Fewer lines, full width, still out of the way. */
  @media (max-width:640px){
    #merDock{left:8px;right:8px;bottom:8px;width:auto;max-height:70px;padding:6px 8px}
    #merDock .lbl{margin-bottom:2px} }
  /* New lines have been arriving silently. A short wash on change is enough to
     pull the eye without animating the whole dock. */
  @keyframes merArrive{ from{background:rgba(179,116,0,.20)} to{background:transparent} }
  .mer-arrive{animation:merArrive .9s ease-out}""")

# B3 — flash the dock row when its content actually changes
sub('B3 dock arrival cue',
"""      n.textContent=(m.kind==='human'?'YOU':m.name)+': '+m.text;
      n.style.color=m.kind==='human'?'#1C2634':m.color;
      n.className='truncate';""",
"""      const next=(m.kind==='human'?'YOU':m.name)+': '+m.text;
      const changed = n.textContent!==next;
      n.textContent=next;
      n.style.color=m.kind==='human'?'#1C2634':m.color;
      n.className='truncate';
      /* Re-trigger the animation by forcing a reflow; without it a row that
         changes twice in a row only ever flashes once. */
      if(changed && n.textContent){ void n.offsetWidth; n.classList.add('mer-arrive'); }""")

# B4 — agents stand on the floor like everything else after pass 1
sub('B4 agent contact shadow',
"""    const x=isoX(ac.x,ac.y), y=isoY(ac.x,ac.y);
    const c=ac.a.color;
    // body — taller than a worker, coloured coat""",
"""    const x=isoX(ac.x,ac.y), y=isoY(ac.x,ac.y);
    const c=ac.a.color;
    contactShadow(ctx,ac.x,ac.y,3.8,1.9,0.62);
    // body — taller than a worker, coloured coat""")

# ═══ C. CROSS-AISLE ROUTING ═════════════════════════════════════════════════

sub('C1 aisle geometry helpers',
"""function zoneAnchor(id){""",
"""/* Floor traffic used to interpolate straight from anchor to anchor, which
   walks pickers and forklifts clean through solid racking — the single loudest
   tell that this was a diagram and not a building. Rack runs extend along x and
   are 1.2 deep in y, so the open lanes are the bands between rows, and the only
   legal way across the racking is a cross-aisle at the ends or the middle.
   Cached per layout; spawnWorld changes W and the cache drops. */
let _aisleCache=null;
function aisleBands(){
  const key=(WORLD.W||0)+'x'+(WORLD.H||0)+':'+(WORLD.rackBlocks||[]).length;
  if(_aisleCache && _aisleCache.key===key) return _aisleCache.bands;
  const bands=[];
  for(const r of (WORLD.rackBlocks||[]))
    for(let row=0;row<(r.rows||3);row++){ const y=r.gy+row*4; bands.push([y-0.25,y+1.45]); }
  _aisleCache={key,bands};
  return bands;
}
function crossLanes(){
  const W=WORLD.W||34;
  return W>26 ? [1.0, W/2, W-1.0] : [1.0, W-1.0];
}
/* True only when a rack row lies wholly between the two heights, so an agent
   already standing at a pick face is never told to detour away from it. */
function crossesRack(y0,y1){
  const lo=Math.min(y0,y1), hi=Math.max(y0,y1);
  for(const b of aisleBands()) if(b[0]>lo+0.4 && b[1]<hi-0.4) return true;
  return false;
}
function zoneAnchor(id){""")

sub('C2 route through cross-aisles',
"""  const wp=a.wps[a.wi]; const dx=wp.x-a.x, dy=wp.y-a.y, d=Math.hypot(dx,dy);
  const sp=a.speed*dt*(SIM.paused?0:1);
  if(d<0.15){ a.wi=(a.wi+1)%a.wps.length; if(a.wi===0 && a.dept){ a.wps=DEPT_ROUTES[a.dept](); a.fatigue=Math.min(1,a.fatigue+.02);} if(a.kind){ a.wps=[zoneAnchor('staging'),rackAnchor(),zoneAnchor(a.kind==='agv'?'charge':'dispatch')]; a.carrying=!a.carrying; } }
  else { a.x+=dx/d*sp; a.y+=dy/d*sp; }""",
"""  const wp=a.wps[a.wi];
  const sp=a.speed*dt*(SIM.paused?0:1);
  /* Aim point: the waypoint itself when the way is clear, otherwise the leg of
     a cross-aisle detour — square up to the nearest cross-aisle, cross, then
     run the lane. Arrival is still judged against the true waypoint, so a leg
     can never be mistaken for reaching the destination. */
  let tx=wp.x, ty=wp.y, leg=false;
  if(crossesRack(a.y,wp.y)){
    const lanes=crossLanes();
    let lane=lanes[0];
    for(const L of lanes) if(Math.abs(L-a.x)<Math.abs(lane-a.x)) lane=L;
    if(Math.abs(a.x-lane)>0.5){ tx=lane; ty=a.y; }   // square up along the lane
    else { tx=a.x; ty=wp.y; }                         // then cross
    leg=true;
  }
  const tdx=wp.x-a.x, tdy=wp.y-a.y, td=Math.hypot(tdx,tdy);
  if(!leg && td<0.15){ a.wi=(a.wi+1)%a.wps.length; if(a.wi===0 && a.dept){ a.wps=DEPT_ROUTES[a.dept](); a.fatigue=Math.min(1,a.fatigue+.02);} if(a.kind){ a.wps=[zoneAnchor('staging'),rackAnchor(),zoneAnchor(a.kind==='agv'?'charge':'dispatch')]; a.carrying=!a.carrying; } }
  else { const dx=tx-a.x, dy=ty-a.y, d=Math.hypot(dx,dy);
    if(d>0.0001){ const ux=dx/d, uy=dy/d; a.x+=ux*sp; a.y+=uy*sp; a.hdx=ux; a.hdy=uy; } }""")

# C3 — heading readable on the forklifts
sub('C3 vehicle heading',
"""  if(v.carrying&&!v.charging) cube(ctx,v.x+.1,v.y+.05,0.5,0.4,0.9, '#BF8B5E', shade('#BF8B5E',.5), shade('#BF8B5E',.65));""",
"""  if(v.carrying&&!v.charging) cube(ctx,v.x+.1,v.y+.05,0.5,0.4,0.9, '#BF8B5E', shade('#BF8B5E',.5), shade('#BF8B5E',.65));
  /* Fork end, so a unit reads as facing its direction of travel rather than
     sliding sideways down an aisle. Heading comes from the movement step. */
  if(v.hdx!==undefined){
    const nx=v.x+.4+v.hdx*.62, ny=v.y+.3+v.hdy*.62;
    ctx.fillStyle=shade(c,1.2-nite*.3);
    ctx.beginPath(); ctx.arc(isoX(nx,ny), isoY(nx,ny)-TILE*.42, 1.9, 0, 7); ctx.fill(); }""")

io.open(OUT,'w',encoding='utf-8').write(s)
print('patched:', len(applied), 'sections')
for a in applied: print('  ok  ', a)
print(f'{orig} -> {len(s)} chars  ->  {OUT}')
