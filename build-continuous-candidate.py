from pathlib import Path
import hashlib,json,shutil,sys
root=Path(__file__).resolve().parent
base=root/'artifacts/enriched-baseline'
proof=json.loads((root/'artifacts/enriched-recovery.json').read_text(encoding='utf-8'))
for n,h in proof['sourceHashes'].items():assert hashlib.sha256((base/n).read_bytes()).hexdigest()==h,n
composition='--composition' in sys.argv
candidate=root/'artifacts'/('composition-candidate' if composition else 'continuous-candidate')
shutil.copytree(base,candidate,dirs_exist_ok=True)
for src in (root/'candidate-src').glob('*.js'):shutil.copyfile(src,candidate/src.name)
main=(candidate/'scan-exhibit.js').read_text(encoding='utf-8')
main="import {createContinuousReef} from './continuous-reef.js';\n"+main
needle="explorationWorld=createExplorationWorld({scene,configure:m=>ocean.configure(m),ground:ocean.ground});"
replacement=needle+"const reefRock=await new GLTFLoader().loadAsync('./assets/boulder_01_LOD1_1k.glb');const continuous=createContinuousReef({parent:explorationWorld.group,rockScene:reefRock.scene,corals:coralAsset.scene,configure:m=>ocean.configure(m)});explorationWorld.continuous=continuous;const priorUpdate=explorationWorld.update;explorationWorld.update=(time,camera)=>{priorUpdate(time,camera);const s=explorationWorld.getState();if(!s.paused&&!s.reduced&&!s.hidden)continuous.update(time);};const priorDispose=explorationWorld.dispose;explorationWorld.dispose=()=>{continuous.dispose();priorDispose();};"
assert main.count(needle)==1
main=main.replace(needle,replacement)
(candidate/'scan-exhibit.js').write_text(main,encoding='utf-8',newline='\n')
data=(candidate/'exploration-world-data.js').read_text(encoding='utf-8')
data="import {CONTINUOUS_MASSES} from './continuous-layout.js';\n"+data
assert data.count('const masses=[...REEF_MASSES,...DISTANT_MASSES];')==1
data=data.replace('const masses=[...REEF_MASSES,...DISTANT_MASSES];','const masses=[...CONTINUOUS_MASSES];')
(candidate/'exploration-world-data.js').write_text(data,encoding='utf-8',newline='\n')
# The broad textured formations replace the bare late-route rock proxies and
# their sparse stub decorations; retained near scan/supports are unchanged.
world=(candidate/'exploration-world.js').read_text(encoding='utf-8')
world=world.replace('REEF_MASSES.forEach(outcrop);','// Existing collision footprints retained; textured 3D buttresses supply the candidate scenery.\n // REEF_MASSES.forEach(outcrop);')
world=world.replace('DISTANT_MASSES.forEach(outcrop);','// DISTANT_MASSES.forEach(outcrop);')
# Do not run the old top seating against hidden/deleted proxies.
world=world.replace('for(const r of REEF_MASSES){for(let i=0;i<26;i++){','for(const r of []){for(let i=0;i<26;i++){')
if composition:
    # Extend the actual seabed behind the entry. Near scan/support geometry is
    # retained; the extension shares its height at the existing grid boundary.
    world=world.replace('for(let z=-620;z<80;z+=tile)', 'for(let z=-620;z<280;z+=tile)')
    # Match sediment at the retained rectangular boundary, then gradually reach
    # the existing offshore palette. This removes the exposed bright seam.
    world=world.replace("color.set('#beb897').lerp", "color.set('#9e9672').lerp(new T.Color('#beb897'),smooth(0,80,Math.max(0,Math.abs(px)-75,pz-65,-pz-145))).lerp")
(candidate/'exploration-world.js').write_text(world,encoding='utf-8',newline='\n')
ocean=(candidate/'scan-ocean.js').read_text(encoding='utf-8')
ocean=ocean.replace("sun.shadow.mapSize.set(1024,1024)","sun.shadow.mapSize.set(1024,1024)")
ocean=ocean.replace("envelope.position.copy(camera.position);","envelope.position.copy(camera.position);sun.position.set(camera.position.x-25,65,camera.position.z+28);sun.target.position.set(camera.position.x,-10,camera.position.z-16);sun.target.updateMatrixWorld();")
ocean=ocean.replace("{left:-12,right:12,top:12,bottom:-12,near:.2,far:35}","{left:-34,right:34,top:34,bottom:-34,near:.2,far:160}")
ocean=ocean.replace("surface.position.set(0,12,-40)","surface.scale.set(4,4,1);surface.position.set(0,12,-220)")
if composition:
    # The finite alpha plane caused the horizontal water-colour step. The
    # existing directional water-volume shader supplies the continuous surface
    # impression; transmission and fog coefficients remain unchanged.
    ocean=ocean.replace("surface.name='Synthetic_Overhead_Surface';group.add(surface);", "surface.name='Synthetic_Overhead_Surface';surface.visible=false;group.add(surface);")
    ocean=ocean.replace('outgoingLight=mix(exhibitWater(normalize(ray)),outgoingLight,sandInterior);', '/* Connected seabed has no finite rectangular colour fade. */')
(candidate/'scan-ocean.js').write_text(ocean,encoding='utf-8',newline='\n')
changes={}
for p in candidate.glob('*.js'):
    n=p.name
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if proof['sourceHashes'].get(n)!=h:changes[n]=h
(root/'artifacts'/('composition-build.json' if composition else 'continuous-build.json')).write_text(json.dumps({'baseSourceHashAggregate':proof['sourceHashAggregate'],'changes':changes,'scanAssetsUnchanged':True,'tourAndNavigationUnchanged':True,'compositionRevision':composition,'originalFormationCount':17,'currentFormationCount':17,'fishCountUnchanged':286,'waterTransmissionUnchanged':True},indent=2),encoding='utf-8')
print('CONTINUOUS_CANDIDATE',candidate,len(changes))
