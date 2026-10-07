import * as THREE from 'three';

// One illustrative flexible fan, not a calibrated flow or biological simulation.
// Frozen source2372e912: a rigid lower band clears its attached limestone support.
export const SEA_FAN_CURRENT = Object.freeze({
  node: 'Inhabited_Middle_Attached_reticulate_fan_form',
  fixedThroughY: 1.84,
  tipY: 2.6220932006835938,
  maxDisplacement: .04,
  periodSeconds: 8
});
const applied = new WeakMap();

export function seaFanAmplitude(visibleSeconds) {
  if (!Number.isFinite(visibleSeconds)) throw Error('Sea fan needs finite visible elapsed seconds');
  return SEA_FAN_CURRENT.maxDisplacement * Math.sin(visibleSeconds * (2 * Math.PI / SEA_FAN_CURRENT.periodSeconds));
}

// Kept alongside GLSL for geometry verification; never called per vertex at runtime.
export function seaFanWeight(y) {
  const h = THREE.MathUtils.clamp((y - SEA_FAN_CURRENT.fixedThroughY) / (SEA_FAN_CURRENT.tipY - SEA_FAN_CURRENT.fixedThroughY), 0, 1);
  return h * h * (3 - 2 * h);
}
export function seaFanSlope(y) {
  const span = SEA_FAN_CURRENT.tipY - SEA_FAN_CURRENT.fixedThroughY;
  const h = THREE.MathUtils.clamp((y - SEA_FAN_CURRENT.fixedThroughY) / span, 0, 1);
  return 6 * h * (1 - h) / span;
}

const declarations = `
uniform float reefFanAmplitude;
float reefFanHeight(float y) {
  return clamp((y - ${SEA_FAN_CURRENT.fixedThroughY}) / ${SEA_FAN_CURRENT.tipY - SEA_FAN_CURRENT.fixedThroughY}, 0.0, 1.0);
}
float reefFanWeight(float y) {
  float h = reefFanHeight(y);
  return h * h * (3.0 - 2.0 * h);
}
float reefFanSlope(float y) {
  float h = reefFanHeight(y);
  return 6.0 * h * (1.0 - h) / ${SEA_FAN_CURRENT.tipY - SEA_FAN_CURRENT.fixedThroughY};
}
`;
const positionPatch = '#include <begin_vertex>\ntransformed.z += reefFanAmplitude * reefFanWeight(position.y);';
const normalPatch = `#include <beginnormal_vertex>
// F(x,y,z)=(x,y,z+a*w(y)); J^-T keeps lighting aligned with the bent surface.
float reefFanShear = reefFanAmplitude * reefFanSlope(position.y);
objectNormal.y -= reefFanShear * objectNormal.z;
#ifdef USE_TANGENT
  objectTangent.z += reefFanShear * objectTangent.y;
#endif
`;
function addBend(material, amplitude, withNormals) {
  const previous = material.onBeforeCompile, previousKey = material.customProgramCacheKey();
  material.onBeforeCompile = function (shader, renderer) {
    previous.call(this, shader, renderer);
    if (!shader.vertexShader.includes('#include <begin_vertex>')) throw Error('Sea fan position insertion point missing');
    if (withNormals && !shader.vertexShader.includes('#include <beginnormal_vertex>')) throw Error('Sea fan normal insertion point missing');
    shader.uniforms.reefFanAmplitude = amplitude;
    shader.vertexShader = declarations + shader.vertexShader.replace('#include <begin_vertex>', positionPatch);
    if (withNormals) shader.vertexShader = shader.vertexShader.replace('#include <beginnormal_vertex>', normalPatch);
  };
  material.customProgramCacheKey = () => previousKey + '_seaFanCurrentR1_' + (withNormals ? 'surface' : 'depth');
}

export function installSeaFanCurrent(root, { configureMaterial } = {}) {
  const matches = [];
  root.traverse(o => { if (o.name === SEA_FAN_CURRENT.node) matches.push(o); });
  if (matches.length !== 1 || !matches[0].isMesh) throw Error('Expected one exact Middle sea fan');
  const mesh = matches[0];
  if (applied.has(mesh)) return applied.get(mesh);
  if (typeof configureMaterial !== 'function') throw Error('Reapply accepted water/substrate material composition');
  if (!mesh.material.isMeshStandardMaterial || mesh.isSkinnedMesh || mesh.morphTargetInfluences || mesh.material.displacementMap) throw Error('Sea fan source is no longer the certified rigid standard mesh');
  root.updateMatrixWorld(true);
  const scale = new THREE.Vector3();mesh.getWorldScale(scale);
  if (scale.distanceTo(new THREE.Vector3(1, 1, 1)) > 1e-8) throw Error('Sea fan scene-unit displacement needs unchanged unit scale');
  const source = mesh.geometry;source.computeBoundingBox();
  if (source.attributes.position.count !== 50583 || source.index?.count !== 227778 || Math.abs(source.boundingBox.max.y - SEA_FAN_CURRENT.tipY) > 1e-8) throw Error('Sea fan source changed; repeat its motion-envelope audit');

  // Separate bounds, shared immutable buffers: no vertex/index copies or new triangles.
  const geometry = new THREE.BufferGeometry();
  for (const [name, attribute] of Object.entries(source.attributes)) geometry.setAttribute(name, attribute);
  geometry.setIndex(source.index);
  geometry.groups = source.groups.map(group => ({ ...group }));
  geometry.setDrawRange(source.drawRange.start, source.drawRange.count);
  geometry.boundingBox = source.boundingBox.clone();
  geometry.boundingBox.min.z -= SEA_FAN_CURRENT.maxDisplacement;
  geometry.boundingBox.max.z += SEA_FAN_CURRENT.maxDisplacement;
  geometry.boundingSphere = geometry.boundingBox.getBoundingSphere(new THREE.Sphere());
  mesh.geometry = geometry;
  const material = mesh.material.clone();
  configureMaterial(material, mesh);
  const amplitude = { value: 0 };
  addBend(material, amplitude, true);
  mesh.material = material;
  // Default packing matches this vendored Three renderer's own depth material.
  mesh.customDepthMaterial = new THREE.MeshDepthMaterial();
  mesh.customDistanceMaterial = new THREE.MeshDistanceMaterial();
  addBend(mesh.customDepthMaterial, amplitude, false);
  addBend(mesh.customDistanceMaterial, amplitude, false);
  const controller = Object.freeze({
    node: mesh.name,
    update(visibleSeconds) { amplitude.value = seaFanAmplitude(visibleSeconds); },
    getState() { return { node: mesh.name, amplitude: amplitude.value, maxDisplacement: SEA_FAN_CURRENT.maxDisplacement, fixedThroughLocalY: SEA_FAN_CURRENT.fixedThroughY, periodSeconds: SEA_FAN_CURRENT.periodSeconds }; }
  });
  applied.set(mesh, controller);
  return controller;
}
