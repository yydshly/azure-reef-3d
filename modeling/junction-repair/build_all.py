"""Apply the reviewed narrow continuation repair to exact-replayed original thickets only."""
import bpy,bmesh,sys,argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('recipe',type=Path);p.add_argument('out',type=Path);cfg=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sys.path.insert(0,str(Path(__file__).parent));from replay_thickets import replay,correct
proof=json.loads((cfg.out/'all-replay-proof.json').read_text());assert proof['all22_exact']and proof['source_sha256']==hashlib.sha256(cfg.source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(cfg.source));targets=[];reports=[];branchgraphs={}
for m in replay(cfg.recipe):
 graph=[dict(t)for t in m.tubes];report=correct(m);branchgraphs[m.name]={'height_scale':m.height_scale,'source_graph':graph,'continuation_repairs':report['joints']};mat=bpy.data.objects[m.name].data.materials[0];me=bpy.data.meshes.new(m.name+'_junctions');me.from_pydata(m.v,[],m.f);me.update();ob=bpy.data.objects.new(m.name+'_junctions',me);bpy.context.collection.objects.link(ob);me.materials.append(mat)
 ca=me.color_attributes.new(name='ReefColor',type='FLOAT_COLOR',domain='POINT')
 for d,c in zip(ca.data,m.c):d.color=c
 me.color_attributes.active_color=ca
 bm=bmesh.new();bm.from_mesh(me);loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=bm.faces);report['boundary_edges']=sum(e.is_boundary for e in bm.edges);report['nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges);assert report['boundary_edges']==report['nonmanifold_edges']==0;bm.to_mesh(me);bm.free()
 for f in me.polygons:f.use_smooth=True
 uv=me.uv_layers.new(name='SurfaceUV');me.update()
 for poly in me.polygons:
  axis=max(range(3),key=lambda i:abs(poly.normal[i]));dims=[(1,2),(0,2),(0,1)][axis];sign=1 if poly.normal[axis]>=0 else -1
  for li in poly.loop_indices:
   c=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(c[dims[0]]*2.4*sign,c[dims[1]]*2.4)
 report['intrinsic_vertices']=len(me.vertices);report['bbox_exactly_unchanged']=report['bbox_before']==report['bbox_after'];report['final_polygons']=len(me.polygons);targets.append((ob,m.name));reports.append(report);print('MESH_READY',m.name,report['joints_corrected'],report['bbox_exactly_unchanged'],flush=True)
keep={o for o,_ in targets}
for ob in list(bpy.data.objects):
 if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
for ob,name in targets:ob.name=name;ob.data.name=name;ob.select_set(True)
bpy.context.view_layer.objects.active=targets[0][0]
bpy.ops.export_scene.gltf(filepath=str(cfg.out/'replacement-thickets.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT');bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(cfg.out/'thickets-editable.blend'))
report={'source_sha256':proof['source_sha256'],'mesh_count':len(reports),'joints_repaired':sum(m['joints_corrected']for m in reports),'triangles':sum(m['triangles']for m in reports),'all_original_axes_tips_bases_colors_retained':all(m['all_terminal_tips_and_basal_roots_unchanged']for m in reports),'all_envelopes_exactly_unchanged':all(m['bbox_exactly_unchanged']for m in reports),'all_native_boundary_nonmanifold_zero':all(m['boundary_edges']==m['nonmanifold_edges']==0 for m in reports),'meshes':reports,'scope':'Apply the same reviewed source-graph nonterminal radius restoration and continuation bridge only. No new growth forms, global unions, incidental crossing welds, base shifts or color changes.'};(cfg.out/'all-branch-graphs.json').write_text(json.dumps(branchgraphs,indent=2));(cfg.out/'all-geometry-proof.json').write_text(json.dumps(report,indent=2));print('ALL_DONE',report['joints_repaired'],report['triangles'])
