import bpy,sys,argparse,json
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(args.input.resolve()))
bpy.context.scene['asset_provenance']='Exact final GLB reimport. Original authored materials and maps; no offline caustic shader, lights, or atmosphere. Linked staghorn mesh instances preserved.'
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(args.output.resolve()))
images=[{'name':im.name,'packed':bool(im.packed_file)}for im in bpy.data.images if im.type=='IMAGE']
proof={'images':images,'all_images_packed':all(i['packed']for i in images),'objects':len(bpy.data.objects),'meshes':len(bpy.data.meshes),'lights':sum(o.type=='LIGHT'for o in bpy.data.objects),'cameras':sum(o.type=='CAMERA'for o in bpy.data.objects)}
args.output.with_suffix('.proof.json').write_text(json.dumps(proof,indent=2));print(proof)
