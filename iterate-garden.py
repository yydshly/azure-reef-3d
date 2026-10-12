from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
page=root/'dist/preview/reef-garden-v1'
archive=root/'dist/preview/reef-garden-v1-first'
assert not archive.exists()
shutil.copytree(page,archive)
world=page/'world.js';s=world.read_text(encoding='utf-8')
def replace(old,new):
 global s
 assert s.count(old)==1,old
 s=s.replace(old,new)
replace('[-19,-218,14,11,15]','[-36,-226,13,8,13]')
replace('[-15,-190,11.4,6]','[-3,-189,9.4,4.2]')
replace('const reefItems=[],gardens=[];', '''// Smaller asymmetric outcrops punctuate the sand banks without adding gateways.
 formations.push([-7,14,3.1,1.5,3.6],[8,1,3.8,1.8,3.1],[7,-14,2.6,1.4,3.8],[-9,-39,3.7,2.1,4.8],[10,-52,2.8,1.6,3.5],[24,-77,3.4,2.5,4.8],[3,-89,3.1,1.8,3.6],[-10,-119,4.2,2.7,4.4],[-30,-139,3.5,2.2,4.5],[-6,-171,3.2,2.1,4.3],[-9,-209,3.8,2,4.5],[-10,-229,6,3.2,7],[12,-236,13,9,16]);
 const reefItems=[],gardens=[];''')
replace('for(let j=0;j<12;j++){const angle=', 'for(let j=0;j<(rx<5?6:12);j++){const angle=')
replace('// Two distinctive doorways and a grove of giant umbrella corals establish the journey.', '''// Fan coral grows as a curved radial crown, distinct from the round plate gardens.
 function seaFan(){const pieces=[];const tube=(points,r)=>pieces.push(new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),7,r,5,false));tube([[0,0,0],[0,.6,0],[.04,1.2,.06]],.075);
  for(let i=0;i<11;i++){const a=-1.12+i*.224,x=Math.sin(a)*1.8,y=.5+Math.cos(a)*2.3;const tip=[x,y,.18+Math.abs(x)*.12];tube([[0,.65,0],[x*.45,1.35,.07],tip],.038);for(let k=0;k<3;k++)tube([[x*.66,.85+(y-.85)*.66,.13],[x*.85+(k-1)*.1,y-.2,.20],[x+(k-1)*.22,y+.13-Math.abs(k-1)*.13,.23]],.022)}
  const g=mergeGeometries(pieces,false);pieces.forEach(p=>p.dispose());return g;
 }
 const fanSites=[[-8,9,1.3,.6],[8,-11,1.05,-.5],[23,-73,1.4,-.9],[6,-94,1.1,.6],[-13,-113,1.2,-.4],[-33,-144,1.2,.5],[-5,-178,1.5,-.8],[-29,-210,1.3,.7],[0,-231,1.5,-.6]];
 const fanItems=fanSites.map(([x,z,s,a],i)=>({p:[x,floorHeight(x,z),z],s:[s,s,s],a,c:i%3===0?palette.peach:i%3===1?palette.rose:palette.lilac}));batch('Curved_Sea_Fan_Groves',seaFan(),mat('#ffffff'),fanItems);
 // Keep the original two landmarks; no additional arches are introduced.''')
replace('[-12,4,-208]],fish=[];','[-12,4,-208],[4,8,-82],[-8,9,-121],[-24,8,-179],[3,8,-230]],fish=[];')
replace('for(let i=0;i<24;i++){const a=rand()*6.28,r=rand()*4,s=.55+rand()*.35;', 'for(let i=0;i<(j>=9?18:24);i++){const a=rand()*6.28,r=rand()*(j>=9?6:4),s=(j>=9?.8:.55)+rand()*.35;')
replace('formations:formations.length,giantCorals:', 'formations:formations.length,seaFans:fanItems.length,giantCorals:')
world.write_text(s,encoding='utf-8',newline='\n')
html=page/'index.html';s=html.read_text(encoding='utf-8')
replace('<span class="edition">原创风格化海域 · 01</span></header>', '''<div class="header-tools"><span class="edition">原创风格化海域 · 01.1</span><button id="previous" aria-expanded="false" aria-controls="previousMenu">之前的探索 <span aria-hidden="true">↗</span></button></div></header><section id="previousMenu" class="previous-menu" hidden role="dialog" aria-labelledby="previousTitle"><div class="menu-heading"><h2 id="previousTitle">之前的探索</h2><button id="closePrevious" aria-label="关闭之前的探索菜单">×</button></div><a id="oldWorld" href="../world/" target="_blank" rel="noopener noreferrer"><strong>原版海底探索 ↗</strong><span>保留之前的探索场景，在新窗口打开</span></a><a id="realProbe" href="../real-splats-probe/" target="_blank" rel="noopener noreferrer"><strong>真实扫描试验 ↗</strong><span>独立试验，尚非完整海底体验</span></a><a id="firstGarden" href="../reef-garden-v1-first/" target="_blank" rel="noopener noreferrer"><strong>海庭首版对照 ↗</strong><span>查看本轮改进前的海庭</span></a><p>这些入口各自独立，原有场景与扫描模型尚未融合进海庭。</p></section>''')
html.write_text(s,encoding='utf-8',newline='\n')
app=page/'app.js';s=app.read_text(encoding='utf-8')
replace(" const supported=['KeyW'", """ const menu=$('#previousMenu'),menuButton=$('#previous');
 function closePrevious(restoreFocus=false){menu.hidden=true;menuButton.setAttribute('aria-expanded','false');if(restoreFocus)menuButton.focus({preventScroll:true})}
 menuButton.onclick=()=>{if(!menu.hidden){closePrevious();return}nav.stop();menu.hidden=false;menuButton.setAttribute('aria-expanded','true');$('#closePrevious').focus({preventScroll:true})};$('#closePrevious').onclick=()=>closePrevious(true);
 document.addEventListener('pointerdown',e=>{if(!menu.hidden&&!menu.contains(e.target)&&!menuButton.contains(e.target))closePrevious()});document.addEventListener('keydown',e=>{if(e.code==='Escape'&&!menu.hidden){e.preventDefault();closePrevious(true)}});menu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>closePrevious()));
 const supported=['KeyW'""")
app.write_text(s,encoding='utf-8',newline='\n')
css=page/'style.css';s=css.read_text(encoding='utf-8')
s+='''\n.header-tools{display:flex;align-items:center;gap:18px}#previous{border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--ink);padding:9px 12px;font-size:11px}#previous span{margin-left:12px}.previous-menu{position:absolute;z-index:7;right:34px;top:76px;width:330px;padding:15px;background:#173f49f5;border:1px solid var(--line);border-radius:14px;box-shadow:0 12px 40px #092b3b66;backdrop-filter:blur(12px)}.previous-menu[hidden]{display:none}.menu-heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:5px}.menu-heading h2{font-size:14px;font-weight:500;margin:0;color:var(--gold)}#closePrevious{border:0;background:transparent;color:var(--ink);font-size:23px;width:34px;height:34px;border-radius:7px}.previous-menu a{display:block;padding:13px 5px;border-top:1px solid var(--line);text-decoration:none;color:var(--ink)}.previous-menu strong{display:block;font-size:12px;font-weight:500}.previous-menu a span{display:block;margin-top:6px;font-size:10px;color:var(--muted);line-height:1.5}.previous-menu p{margin:6px 5px 0;font-size:10px;color:var(--muted);line-height:1.7}.previous-menu a:hover,#closePrevious:hover{background:#91b5a212}.previous-menu a:focus-visible,#previous:focus-visible,#closePrevious:focus-visible{outline:2px solid var(--gold);outline-offset:2px}@media(max-width:680px){.header-tools{gap:0}#previous{font-size:10px;padding:7px 9px}#previous span{margin-left:7px}.previous-menu{right:12px;top:54px;width:min(330px,calc(100vw - 24px));padding:12px}.previous-menu a{padding:11px 5px}}\n'''
css.write_text(s,encoding='utf-8',newline='\n')
print('First version frozen; scoped 01.1 scene and previous exploration menu implemented.')
