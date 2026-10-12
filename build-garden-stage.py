from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;page=root/'dist/preview/reef-garden-v1';frozen=root/'dist/preview/reef-garden-v11'
assert not frozen.exists();shutil.copytree(page,frozen)
world=page/'world.js';s=world.read_text(encoding='utf-8')
def rep(old,new):
 global s
 assert s.count(old)==1,old
 s=s.replace(old,new)
rep("export const SPAWN=", "export const STAGE_VERSION='01.2-stage';\nexport const STATION_HABITATS=['shell-portal','rose-plate-garden','sea-feather-bay','blue-canyon','umbrella-grove','gold-fan-lookout'];\nexport const SPAWN=")
rep(" const palette={", " const zone=z=>z>0?0:z>-46?1:z>-90?2:z>-130?3:z>-176?4:5;\n const coralColors=[['#d9bc8c','#b6cab1'],['#d997a0','#e1b79a'],['#76ae9b','#b0cdb0'],['#93abc3','#92b7b7'],['#bc97c0','#caa3b9'],['#e1c28f','#cbd7ae']];\n const palette={")
for a,b in [('[-33,59,15,6,17]','[-26,56,11,4.5,12]'),('[22,70,16,7,16]','[23,53,10,6,12]'),('[-55,-14,19,8,20]','[-48,6,16,6,17]'),('[66,-54,19,11,24]','[50,-44,18,9,19]'),('[-64,-105,22,12,26]','[-52,-101,18,13,20]'),('[55,-154,24,13,26]','[48,-152,17,10,19]'),('[-62,-208,24,12,25]','[-55,-214,17,10,21]'),('[60,27,22,7,21]','[54,33,16,6,17]'),('[-4,104,22,11,20]','[-8,91,17,7,16]'),('[40,107,18,14,24]','[44,95,16,10,19]'),('[-34,-250,20,13,20]','[-30,-247,13,11,16]'),('[20,-255,24,14,22]','[15,-251,18,8,19]')]:rep(a,b)
rep('const reefItems=[],gardens=[];', 'const reefItems=Array.from({length:6},()=>[]),gardens=[];')
rep('reefItems.push({p:[x,base,z],s:[rx,h,rz],a:k*.74});', 'reefItems[zone(z)].push({p:[x,base,z],s:[rx,h,rz],a:k*.74});')
rep("batch('Layered_Reef_Gardens',reefG,reefM,reefItems,true);", '''// Six deformations of the same volumetric shelf, with unchanged formation count.
 const reefTops=['#abc3a8','#bcb1a1','#90b7a1','#6e9ea8','#aba6bc','#a9c0ae'];
 const reefSides=['#527c81','#796f7b','#3e7d7b','#426377','#666c89','#527c86'];
 for(let v=0;v<6;v++){const g=reefG.clone(),p=g.attributes.position,c=g.attributes.color;
  for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),a=Math.atan2(z,x);let fx=1,fz=1,ox=0,oz=0;
   if(v===0){fx=1+.12*Math.cos(a*2);oz=.10*y*y}
   if(v===1){fx=1+.19*Math.sin(a*3+.4);fz=.88+.12*Math.cos(a*2);ox=.17*y}
   if(v===2){fx=1+.20*Math.sin(a*2);fz=1+.12*Math.cos(a*3);oz=-.15*y*y}
   if(v===3){fx=.87+.20*Math.cos(a*2);fz=1+.16*Math.sin(a*3);ox=.26*y*y}
   if(v===4){fx=1+.15*Math.cos(a*4);fz=1+.11*Math.sin(a*3);ox=-.12*y}
   if(v===5){fx=1+.23*Math.sin(a*2+.7);fz=.90+.15*Math.cos(a*3);oz=.22*y*y}
   p.setXYZ(i,x*fx+ox,y,z*fz+oz);col.set(y>.85?reefTops[v]:reefSides[v]).multiplyScalar(y>.85?1:((Math.floor(y*8)%2)?.90:1.06));c.setXYZ(i,col.r,col.g,col.b)
  }g.computeVertexNormals();batch('Habitat_Reef_'+STATION_HABITATS[v],g,reefM,reefItems[v],true)
 }reefG.dispose();
 ''')
rep("s:[p.scale,p.scale*1.4,p.scale],a:rand()*6.28,c:[palette.peach,palette.lilac,palette.mint][p.index%3]", "s:[p.scale*(zone(p.z)===3?.65:1),p.scale*(zone(p.z)===3?2.1:zone(p.z)===2?.7:1.4),p.scale*(zone(p.z)===3?.65:1)],a:rand()*6.28,c:coralColors[zone(p.z)][p.index%2]")
rep('s:[p.scale*(1.25-j*.15),p.scale,p.scale*(1.25-j*.15)],a:rand()*6.28,c:[palette.rose,palette.peach,palette.lilac][p.index%3]', 's:[p.scale*(1.25-j*.15)*(zone(p.z)===1?1.25:.9),p.scale*(zone(p.z)===1?1.6:.7),p.scale*(1.25-j*.15)],a:rand()*6.28,c:coralColors[zone(p.z)][(p.index+j)%2]')
rep('c:p.index%2?palette.mint:palette.gold', 'c:coralColors[zone(p.z)][p.index%2]')
rep('const fanSites=[[-8,9,1.3,.6],[8,-11,1.05,-.5],[23,-73,1.4,-.9],[6,-94,1.1,.6],[-13,-113,1.2,-.4],[-33,-144,1.2,.5],[-5,-178,1.5,-.8],[-29,-210,1.3,.7],[0,-231,1.5,-.6]];', '''const fanSites=[[13,42,1.5,.7],[-19,-27,1.6,-.5],[29,-38,1.4,.4],[-26,-97,1.2,.5],[-33,-144,1.2,.5],[-8,-169,1.1,-.5],[-32,-192,1.9,-.8],[1,-183,2.1,.5],[-34,-224,1.7,-.6]];
 const bankHeight=(x,z)=>{const r=formations.find(([a,b,rx,,rz])=>Math.hypot((x-a)/rx,(z-b)/rz)<.56);return r?floorHeight(r[0],r[1])+r[3]*.71:floorHeight(x,z)};''')
rep('p:[x,floorHeight(x,z),z],s:[s,s,s],a,c:i%3===0?palette.peach:i%3===1?palette.rose:palette.lilac', 'p:[x,bankHeight(x,z),z],s:[s,s,s*.65],a,c:coralColors[zone(z)][i%2]')
rep('const giants=[[-13,-92,7.8,4.8],[21,-88,6.2,3.8],[-22,-137,10.8,6.4],[-8,-151,12,6.8],[-34,-164,8.8,5.3],[-3,-189,9.4,4.2],[-36,-178,6.9,3.7],[19,-169,9.8,5.3],[-49,-102,9,5.5],[44,-135,10,6],[-6,76,11.6,7.2],[29,102,13.2,6.5],[-25,-239,13,7.5],[20,-229,10,6.5]];', 'const giants=[[-31,-130,8.4,4.5],[20,-140,7.2,3.8],[-22,-137,10.8,6.4],[-8,-151,12,6.8],[-34,-164,8.8,5.3],[8,-174,8.2,4.2],[-38,-156,7.2,3.7],[19,-169,9.8,5.3],[-47,-145,8.5,4.9],[38,-159,9,5.3]];')
rep("}batch('Sea_Feather_Meadows',leafG,leafM,plants);", '''}
 // Redistribute the existing plant budget: the bay becomes a true meadow,
 // while entrance return banks and the final fan overlook keep low vegetation.
 plants.splice(512);for(let i=0;i<plants.length;i++){const item=plants[i];if(i<200||i>=200&&i<260){let x,z,found=false;for(let attempt=0;attempt<50;attempt++){x=i<200?-12+rand()*49:-34+rand()*68;z=i<200?-92+rand()*43:35+rand()*46;if(laneDistance(x,z)>=4&&!obstacles.some(o=>Math.hypot((x-o.x)/o.rx,(z-o.z)/o.rz)<1.05)){found=true;break}}if(found)item.p=[x,floorHeight(x,z),z]}
  const v=zone(item.p[2]),k=item.s[0];item.s=v===2?[k*.85,k*3.2,k*.85]:[k,k*(v===0?.85:.65),k];item.c=v===2?(i%3?'#72ac95':'#b8c78d'):v===3?'#7b9fad':v===5?'#b5bc91':palette.grass;
 }batch('Sea_Feather_Meadows',leafG,leafM,plants);''')
rep('const schoolCentres=[[-6,4,6],[12,5,-34],[17,4,-63],[-12,5,-90],[5,5,-114],[-26,5,-137],[-15,7,-174],[20,4,48],[-12,4,-208],[4,8,-82],[-8,9,-121],[-24,8,-179],[3,8,-230]]', 'const schoolCentres=[[-6,4,6],[12,5,-34],[22,5,-63],[-17,6,-87],[5,6,-114],[-26,5,-137],[-15,7,-174],[14,5,48],[-12,5,-212],[4,8,-82],[-8,9,-121],[-24,8,-185],[3,8,-230]]')
rep("s:[s,s,s],a:0,c:i%4?'#b2cfbc':'#d9bc86',j,phase:", "s:[s,s*(zone(p[2])===1?.7:zone(p[2])===5?1.4:1),s],a:0,c:zone(p[2])===1?'#e3bd93':zone(p[2])===3?'#a7cbd5':zone(p[2])===4?'#d1b6c6':zone(p[2])===5?'#e1ca8f':'#b2cfbc',j,phase:")
rep("const stats={artLanguage:", "const stats={version:STAGE_VERSION,habitats:STATION_HABITATS,reefVariants:6,coralInstances:branchItems.length+cupItems.length+bulbItems.length,artLanguage:")
world.write_text(s,encoding='utf-8',newline='\n')
html=page/'index.html';s=html.read_text(encoding='utf-8');rep('原创风格化海域 · 01.1','海庭阶段版 · 01.2');rep('<title>海庭 · Azure Reef Garden</title>','<title>海庭 01.2 · 阶段演示版</title>');html.write_text(s,encoding='utf-8',newline='\n')
print('Existing habitat budget redistributed; six reef silhouettes; 01.1 frozen.')
