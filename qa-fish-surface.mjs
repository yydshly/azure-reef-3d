import fs from 'node:fs';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import * as T from 'three';
import { GLTFLoader } from './dist/vendor/GLTFLoader.js';
import { addCompanionFish } from './dist/fish-population.js';
import { applyWaterLight } from './dist/water-light.js';
import { refineFish03 } from './dist/fish-surface.js';
const require = createRequire(import.meta.url);
const { loadImage } = require('@napi-rs/canvas');
globalThis.self = globalThis;
globalThis.createImageBitmap = async b => loadImage(Buffer.from(await b.arrayBuffer()));
const source = fs.readFileSync(new URL('./source-model.glb', import.meta.url));
assert.equal(createHash('sha256').update(source).digest('hex'), 'c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd');
const root = (await new Promise((yes, no) => new GLTFLoader().parse(source.buffer.slice(source.byteOffset, source.byteOffset + source.byteLength), '', yes, no))).scene;
const pattern = new T.Texture(), shaders = [], seenMaterials = new Set();
root.traverse(o => { if (o.isMesh) { o.castShadow = o.receiveShadow = true; if (!seenMaterials.has(o.material)) { seenMaterials.add(o.material); applyWaterLight(o.material, pattern, shaders); } } });
assert.throws(() => refineFish03(root, { configureMaterial: () => {} }), /after addCompanionFish/);
addCompanionFish(root);
const hash = a => createHash('sha256').update(Buffer.from(a.array.buffer, a.array.byteOffset, a.array.byteLength)).digest('hex');
const geomSig = g => ({ attrs: Object.fromEntries(Object.entries(g.attributes).map(([k, a]) => [k, { hash: hash(a), size: a.itemSize, normalized: a.normalized }])), index: g.index ? hash(g.index) : null });
const objects = []; root.traverse(o => objects.push(o));
const before = objects.map(o => ({ o, name: o.name, parent: o.parent, children: [...o.children], p: o.position.toArray(), q: o.quaternion.toArray(), s: o.scale.toArray(), cast: o.castShadow, receive: o.receiveShadow, geometry: o.geometry, sig: o.geometry && geomSig(o.geometry), material: o.material, callback: o.material?.onBeforeCompile, key: o.material?.customProgramCacheKey }));
const fish = root.getObjectByName('fish_03');
const exportFish = () => fish.children.filter(o => o.isMesh).map(o => ({ name: o.name, positions: Array.from(o.geometry.attributes.position.array), normals: Array.from(o.geometry.attributes.normal.array), colors: Array.from(o.geometry.attributes.color.array), indices: Array.from(o.geometry.index.array), finCoords: o.geometry.attributes.fishFinCoord ? Array.from(o.geometry.attributes.fishFinCoord.array) : null, position: o.position.toArray(), quaternion: o.quaternion.toArray(), scale: o.scale.toArray() }));
const baseline = exportFish();
let configured = 0;
const result = refineFish03(root, { configureMaterial: material => { configured++; applyWaterLight(material, pattern, shaders); } });
assert.equal(configured, 6);
assert.equal(refineFish03(root, { configureMaterial: () => { throw Error('must be idempotent'); } }), result);
const afterObjects = []; root.traverse(o => afterObjects.push(o)); assert.deepEqual(afterObjects, objects);
const changed = [];
for (const b of before) {
  const o = b.o;
  assert.equal(o.name, b.name); assert.equal(o.parent, b.parent); assert.deepEqual(o.children, b.children);
  assert.deepEqual(o.position.toArray(), b.p); assert.deepEqual(o.quaternion.toArray(), b.q); assert.deepEqual(o.scale.toArray(), b.s);
  assert.equal(o.castShadow, b.cast); assert.equal(o.receiveShadow, b.receive);
  if (o.geometry !== b.geometry || o.material !== b.material) {
    changed.push(o.name); assert.ok(o.name.startsWith('fish_03_') && !o.name.includes('eye'));
    assert.notEqual(o.geometry, b.geometry); assert.notEqual(o.material, b.material);
    assert.equal(o.material.roughness, b.material.roughness); assert.equal(o.material.side, b.material.side);
    assert.equal(o.material.transparent, b.material.transparent); assert.equal(o.material.opacity, b.material.opacity);
    assert.equal(o.material.depthTest, b.material.depthTest); assert.equal(o.material.depthWrite, b.material.depthWrite);
    assert.deepEqual(o.material.color.toArray(), b.material.color.toArray());
    if (o.name.endsWith('_body')) assert.deepEqual(geomSig(o.geometry), b.sig);
  } else if (o.isMesh) {
    assert.deepEqual(geomSig(o.geometry), b.sig);
    assert.equal(o.material.onBeforeCompile, b.callback); assert.equal(o.material.customProgramCacheKey, b.key);
  }
  if (b.geometry) assert.deepEqual(geomSig(b.geometry), b.sig, 'shared original resource bytes mutated');
}
assert.equal(changed.length, 6);
for (const material of result.materials) {
  const shader = { uniforms: {}, vertexShader: T.ShaderLib.standard.vertexShader, fragmentShader: T.ShaderLib.standard.fragmentShader };
  material.onBeforeCompile(shader);
  assert.equal(shader.uniforms.reefCaustics.value, pattern); assert.ok(shader.uniforms.reefTime);
  assert.ok(shader.fragmentShader.includes('reflectedLight.directDiffuse *= downTransmission'));
  assert.ok(shader.fragmentShader.includes('reflectedLight.directSpecular *= downTransmission'));
  assert.ok(shader.fragmentShader.includes('outgoingLight = outgoingLight*transmission'));
  assert.ok(!shader.fragmentShader.includes('#include <fog_fragment>'));
  assert.ok(shader.fragmentShader.indexOf('float fish') < shader.fragmentShader.indexOf('#include <lights_fragment_begin>'));
  assert.ok(material.customProgramCacheKey().includes('reefWaterLightV4|originalFishSurfaceV1'));
  assert.ok(!/[^\n\r \t]#(?:define|if|include)/.test(shader.fragmentShader));
}
assert.equal(shaders.length, 6);
function exactBounds(matrixFor) {
  const box = new T.Box3(); fish.traverse(o => { if (o.isMesh) { const p = o.geometry.attributes.position; for (let i = 0; i < p.count; i++) box.expandByPoint(new T.Vector3().fromBufferAttribute(p, i).applyMatrix4(matrixFor(o))); } }); return { min: box.min.toArray(), max: box.max.toArray() };
}
const inverse = fish.matrixWorld.clone().invert();
const localBounds = exactBounds(o => inverse.clone().multiply(o.matrixWorld)), worldBounds = exactBounds(o => o.matrixWorld);
function closeArrays(a, b, e = 1e-7) { a.forEach((v, i) => assert.ok(Math.abs(v - b[i]) <= e, `${v} != ${b[i]}`)); }
for (const key of ['min', 'max']) { closeArrays(localBounds[key], result.report.localBounds[key]); closeArrays(worldBounds[key], result.report.worldBounds[key]); }
const topology = [];
for (const { name } of result.report.fins) {
  const g = root.getObjectByName(name).geometry, p = g.attributes.position, ns = g.attributes.normal, ix = g.index.array, edges = new Map();
  let volume = 0, areaMin = Infinity;
  for (const v of [...p.array, ...ns.array]) assert.ok(Number.isFinite(v));
  for (let k = 0; k < ix.length; k += 3) {
    const ids = Array.from(ix.slice(k, k + 3)), [a, b, c] = ids.map(i => new T.Vector3().fromBufferAttribute(p, i));
    const normal = new T.Vector3().crossVectors(b.clone().sub(a), c.clone().sub(a));
    areaMin = Math.min(areaMin, normal.length() / 2); volume += a.dot(new T.Vector3().crossVectors(b, c)) / 6;
    for (let i = 0; i < 3; i++) { const u = ids[i], v = ids[(i + 1) % 3], key = [Math.min(u, v), Math.max(u, v)].join(','); const e = edges.get(key) ?? { count: 0, orientation: 0 }; e.count++; e.orientation += u < v ? 1 : -1; edges.set(key, e); }
  }
  for (const e of edges.values()) { assert.equal(e.count, 2, name + ' open/nonmanifold edge'); assert.equal(e.orientation, 0, name + ' inconsistent winding'); }
  assert.ok(areaMin > 1e-12); assert.ok(volume > 0, name + ' inward volume');
  topology.push({ name, vertices: p.count, triangles: ix.length / 3, closedManifold: true, outwardSignedVolume: volume, smallestTriangleArea: areaMin });
}
const candidate = exportFish();
const out = new URL('./evidence/fish-surface-oct7/', import.meta.url);fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(new URL('preview-input.json', out), JSON.stringify({ baseline, candidate, palette: result.report.palette }));
// Reproduce the app's existing pivot exactly once, then ensure pigment coordinates
// are unchanged. The production app still owns motion and the clock.
const tail = root.getObjectByName('fish_03_tail'), beforeCoords = hash(tail.geometry.attributes.fishFinCoord);
tail.geometry = tail.geometry.clone(); tail.geometry.translate(.49, 0, 0); tail.position.x -= .49;
assert.equal(hash(tail.geometry.attributes.fishFinCoord), beforeCoords);
const report = { sourceSHA256: createHash('sha256').update(source).digest('hex'), scope: 'Offline source/geometry/shader assembly; not a browser compile/render or biological validation', changedMeshes: changed, fishCount: objects.filter(o => /^fish_\d+$/.test(o.name)).length, originalResourcesUnchanged: true, allOtherObjectIdentitiesUnchanged: true, companion05Unchanged: true, bodyEveryAttributeAndIndexByteExact: true, transformsNamesHierarchyCountsUnchanged: true, localBoundsBefore: result.report.localBounds, localBoundsAfter: localBounds, worldBoundsBefore: result.report.worldBounds, worldBoundsAfter: worldBounds, configuredWaterMaterials: configured, waterShaderAssemblyPassed: true, tailPivotCoordinatesStable: true, ...result.report, topology };
fs.writeFileSync(new URL('source-checks.json', out), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
