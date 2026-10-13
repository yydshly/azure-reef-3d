import * as THREE from 'three';

// Original, bounded surface study. No photographs or external texture assets.
// Call AFTER addCompanionFish and BEFORE the app registers/pivots moving fins.
// configureMaterial must reapply the accepted scene lighting to each new material.
const applied = new WeakMap();
const FIN_NAMES = ['dorsal', 'ventral', 'pectoral_-1', 'pectoral_1', 'tail'];
const EPS = 2e-7;

function boundsOf(fish, matrixFor) {
  const box = new THREE.Box3();
  fish.traverse(o => {
    if (!o.isMesh) return;
    const p = o.geometry.getAttribute('position'), m = matrixFor(o);
    for (let i = 0; i < p.count; i++) box.expandByPoint(new THREE.Vector3().fromBufferAttribute(p, i).applyMatrix4(m));
  });
  return box;
}

// Fit only the source's existing light/dark pigment ramps. No species-specific
// pattern is introduced: the inherited x*34 + height*3 phase remains unchanged.
function pigmentPalette(geometry) {
  const p = geometry.getAttribute('position'), c = geometry.getAttribute('color');
  const groups = [[], []];
  for (let i = 0; i < p.count; i++) {
    const y = p.getY(i) / .32, z = p.getZ(i) / .15;
    const h = y / Math.max(Math.hypot(y, z), 1e-8);
    groups[Math.sin(p.getX(i) * 34 + p.getY(i) * 3) > .56 ? 1 : 0].push([h, c.getX(i), c.getY(i), c.getZ(i)]);
  }
  return groups.map(rows => {
    const n = rows.length, sx = rows.reduce((a, r) => a + r[0], 0), sxx = rows.reduce((a, r) => a + r[0] ** 2, 0);
    const intercept = [], slope = [];
    for (let k = 1; k <= 3; k++) {
      const sy = rows.reduce((a, r) => a + r[k], 0), sxy = rows.reduce((a, r) => a + r[0] * r[k], 0);
      const b = (n * sxy - sx * sy) / (n * sxx - sx * sx);
      slope.push(b); intercept.push((sy - b * sx) / n);
    }
    return { center: intercept, slope };
  });
}

function addSurfaceShader(material, role, palette) {
  const previous = material.onBeforeCompile, previousKey = material.customProgramCacheKey;
  material.onBeforeCompile = function (shader, renderer) {
    previous.call(this, shader, renderer);
    if (role === 'body') {
      ['Light', 'Dark'].forEach((label, i) => {
        shader.uniforms['fish' + label] = { value: new THREE.Vector3(...palette[i].center) };
        shader.uniforms['fish' + label + 'Slope'] = { value: new THREE.Vector3(...palette[i].slope) };
      });
      shader.vertexShader = 'varying vec3 vFishSurface;\n' + shader.vertexShader;
      shader.vertexShader = shader.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\nvFishSurface = position;');
      shader.fragmentShader = `varying vec3 vFishSurface;
uniform vec3 fishLight, fishLightSlope, fishDark, fishDarkSlope;
` + shader.fragmentShader;
      shader.fragmentShader = shader.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
vec2 fishSection = vFishSurface.yz / vec2(.32, .15);
float fishHeight = fishSection.x / max(length(fishSection), .00001);
float fishBand = sin(vFishSurface.x * 34.0 + vFishSurface.y * 3.0);
float fishAA = max(.12, fwidth(fishBand) * .65);
float fishPigment = smoothstep(.56 - fishAA, .56 + fishAA, fishBand);
vec3 fishPale = fishLight + fishLightSlope * fishHeight;
vec3 fishDeep = fishDark + fishDarkSlope * fishHeight;
diffuseColor.rgb *= mix(fishPale, fishDeep, fishPigment);
`);
    } else {
      shader.vertexShader = 'attribute vec2 fishFinCoord;\nvarying vec2 vFishFinCoord;\n' + shader.vertexShader;
      shader.vertexShader = shader.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\nvFishFinCoord = fishFinCoord;');
      shader.fragmentShader = 'varying vec2 vFishFinCoord;\n' + shader.fragmentShader;
      shader.fragmentShader = shader.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
// Broad, low-contrast fan rays. Coordinates survive the later tail pivot.
float fishRayPhase = atan(vFishFinCoord.y, max(vFishFinCoord.x, .00001)) * 30.0;
float fishRayWave = .5 + .5 * cos(fishRayPhase);
float fishRayAA = max(.09, fwidth(fishRayPhase) * .3);
float fishRay = smoothstep(.80 - fishRayAA, .80 + fishRayAA, fishRayWave);
float fishRayFade = smoothstep(.04, .25, length(vFishFinCoord));
diffuseColor.rgb *= mix(.94, 1.035, fishRay * fishRayFade);
`);
    }
  };
  material.customProgramCacheKey = () => previousKey.call(material) + '|originalFishSurfaceV1:' + role;
  material.needsUpdate = true;
}

function thinFin(mesh, fishInverse, localBounds, worldBounds) {
  const source = mesh.geometry, attr = source.getAttribute('position'), n = attr.count / 2;
  if (!Number.isInteger(n) || (n !== 3 && n !== 4)) throw Error('Unexpected paired fin prism: ' + mesh.name);
  const original = Array.from({ length: attr.count }, (_, i) => new THREE.Vector3().fromBufferAttribute(attr, i));
  const middle = [], halves = [], localMatrix = fishInverse.clone().multiply(mesh.matrixWorld);
  for (let i = 0; i < n; i++) {
    if (Math.abs(original[i].x - original[i + n].x) > EPS || Math.abs(original[i].y - original[i + n].y) > EPS) throw Error('Unrecognized fin layer ordering');
    middle.push(original[i].clone().add(original[i + n]).multiplyScalar(.5));
    halves.push((original[i].z - original[i + n].z) * .5);
  }
  const maxReach = Math.max(...middle.map(v => v.distanceTo(middle[0])));
  const forward = middle[1].clone().sub(middle[0]).normalize();
  const side = middle[n - 1].clone().sub(middle[0]);
  side.addScaledVector(forward, -side.dot(forward)).normalize();
  const held = new Set();
  // Retain a tip only where thinning would move an actual whole-fish support
  // point. Unchanged x/y bounds do not force unnecessarily thick fin edges.
  for (let i = 0; i < original.length; i++) {
    const proposal = original[i].clone(); proposal.z = middle[i % n].z;
    for (const [matrix, box] of [[localMatrix, localBounds], [mesh.matrixWorld, worldBounds]]) {
      const a = original[i].clone().applyMatrix4(matrix), b = proposal.clone().applyMatrix4(matrix);
      for (const axis of ['x', 'y', 'z']) {
        if (Math.abs(a[axis] - b[axis]) > EPS && (Math.abs(a[axis] - box.min[axis]) < EPS || Math.abs(a[axis] - box.max[axis]) < EPS)) held.add(i);
      }
    }
  }
  const subdivisions = 8, positions = [], colors = [], coords = [], indices = [], cache = new Map();
  const color = source.getAttribute('color');
  function vertex(weights, layer) {
    const key = layer + ':' + weights.map(w => Math.round(w * subdivisions)).join(',');
    if (cache.has(key)) return cache.get(key);
    const center = new THREE.Vector3(); let half = 0, preservedWeight = 0;
    for (let i = 0; i < n; i++) {
      center.addScaledVector(middle[i], weights[i]); half += halves[i] * weights[i];
      if (held.has(i + (layer < 0 ? n : 0))) preservedWeight = Math.max(preservedWeight, weights[i]);
    }
    const distance = center.distanceTo(middle[0]) / maxReach;
    const ordinary = THREE.MathUtils.lerp(.34, .12, Math.min(distance, 1));
    // A short smooth collar reaches exactly the retained original support tip.
    const collar = THREE.MathUtils.smoothstep(preservedWeight, .74, 1);
    const factor = THREE.MathUtils.lerp(ordinary, 1, collar);
    const point = center.clone(); point.z += layer * half * factor;
    const index = positions.length / 3; positions.push(...point.toArray());
    colors.push(color.getX(0), color.getY(0), color.getZ(0));
    const relative = center.clone().sub(middle[0]); coords.push(relative.dot(forward) / maxReach, relative.dot(side) / maxReach);
    cache.set(key, index); return index;
  }
  function bary(ids, i, j) {
    const weights = new Array(n).fill(0); weights[ids[0]] = 1 - (i + j) / subdivisions; weights[ids[1]] = i / subdivisions; weights[ids[2]] = j / subdivisions; return weights;
  }
  const triangles = THREE.ShapeUtils.triangulateShape(middle.map(v => new THREE.Vector2(v.x, v.y)), []);
  for (const face of triangles) for (const layer of [1, -1]) {
    for (let i = 0; i < subdivisions; i++) for (let j = 0; j < subdivisions - i; j++) {
      const a = vertex(bary(face, i, j), layer), b = vertex(bary(face, i + 1, j), layer), c = vertex(bary(face, i, j + 1), layer);
      indices.push(...(layer > 0 ? [a, b, c] : [a, c, b]));
      if (i + j < subdivisions - 1) {
        const d = vertex(bary(face, i + 1, j + 1), layer);
        indices.push(...(layer > 0 ? [b, d, c] : [b, c, d]));
      }
    }
  }
  // Explicit closed rim, sharing welded cap-boundary vertices.
  const signedArea = middle.reduce((a, p, i) => { const q = middle[(i + 1) % n]; return a + p.x * q.y - p.y * q.x; }, 0);
  for (let i = 0; i < n; i++) for (let k = 0; k < subdivisions; k++) {
    const weights = t => { const w = new Array(n).fill(0); w[i] = 1 - t; w[(i + 1) % n] = t; return w; };
    const wa = weights(k / subdivisions), wb = weights((k + 1) / subdivisions);
    const a = vertex(wa, 1), b = vertex(wb, 1), c = vertex(wb, -1), d = vertex(wa, -1);
    indices.push(...(signedArea > 0 ? [a, d, b, b, d, c] : [a, b, d, b, c, d]));
  }
  const geometry = new THREE.BufferGeometry();
  geometry.name = source.name;
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geometry.setAttribute('fishFinCoord', new THREE.Float32BufferAttribute(coords, 2));
  geometry.setIndex(indices); geometry.computeVertexNormals(); geometry.computeBoundingBox(); geometry.computeBoundingSphere();
  return { geometry, held: [...held], originalVertices: attr.count, vertices: positions.length / 3, triangles: indices.length / 3 };
}

export function refineFish03(root, { configureMaterial } = {}) {
  const fish = root.getObjectByName('fish_03');
  if (!fish || !root.getObjectByName('fish_05')) throw Error('refineFish03 must run after addCompanionFish(root)');
  if (applied.has(fish)) return applied.get(fish);
  if (typeof configureMaterial !== 'function') throw Error('Provide configureMaterial to retain the accepted water-light shader');
  const body = fish.getObjectByName('fish_03_body');
  const fins = FIN_NAMES.map(name => fish.getObjectByName('fish_03_' + name));
  if (!body?.isMesh || fins.some(o => !o?.isMesh)) throw Error('Unexpected fish_03 hierarchy');
  const tail = fish.getObjectByName('fish_03_tail');
  if (Math.abs(tail.position.x) > EPS || tail.geometry.getAttribute('position').getX(0) > -.48) throw Error('Run refinement before the existing tail pivot is applied');
  root.updateMatrixWorld(true);
  const inverse = fish.matrixWorld.clone().invert();
  const localBounds = boundsOf(fish, o => inverse.clone().multiply(o.matrixWorld));
  const worldBounds = boundsOf(fish, o => o.matrixWorld);
  const palette = pigmentPalette(body.geometry), prepared = [];
  // Prepare resources first. Shared source/companion resources are never mutated.
  for (const mesh of [body, ...fins]) {
    if (Array.isArray(mesh.material) || !mesh.material.isMeshStandardMaterial) throw Error('Expected one standard material per fish mesh');
    const material = mesh.material.clone();
    const role = mesh === body ? 'body' : 'fin';
    if (role === 'body') material.vertexColors = false;
    configureMaterial(material, mesh);
    addSurfaceShader(material, role, palette);
    const result = role === 'body' ? { geometry: mesh.geometry.clone() } : thinFin(mesh, inverse, localBounds, worldBounds);
    prepared.push({ mesh, material, ...result });
  }
  for (const item of prepared) { item.mesh.geometry = item.geometry; item.mesh.material = item.material; }
  const result = {
    fish, materials: prepared.map(p => p.material),
    report: { target: fish.name, palette, fins: prepared.slice(1).map(({ mesh, held, originalVertices, vertices, triangles }) => ({ name: mesh.name, held, originalVertices, vertices, triangles })), localBounds: { min: localBounds.min.toArray(), max: localBounds.max.toArray() }, worldBounds: { min: worldBounds.min.toArray(), max: worldBounds.max.toArray() } },
  };
  applied.set(fish, result);
  return result;
}
