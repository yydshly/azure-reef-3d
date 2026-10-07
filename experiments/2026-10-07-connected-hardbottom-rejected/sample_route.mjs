// Read the actual route module without writing into its checkout.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const [rootArg, output] = process.argv.slice(2);
if (!rootArg || !output) throw new Error('Usage: node sample_route.mjs REPOSITORY OUTPUT_JSON');
const root = path.resolve(rootArg), routeFile = path.join(root, 'dist/passage.js');
const source = fs.readFileSync(routeFile, 'utf8');
const importText = "from 'three'";
if (!source.includes(importText)) throw new Error('Unexpected route import; inspect before using this sampler');
const vendorUrl = pathToFileURL(path.join(root, 'dist/vendor/three.module.js')).href;
const instrumented = source.replace(importText, `from '${vendorUrl}'`) + '\nexport const qaPath = path;';
const module = await import('data:text/javascript;base64,' + Buffer.from(instrumented).toString('base64'));
const samples = Array.from({length:4001}, (_,i) => module.qaPath.getPoint(i/4000).toArray());
let maxMidpointChordDeviation = 0;
for (let i=0; i<4000; i++) {
  const p = module.qaPath.getPoint((i+.5)/4000).toArray();
  const d = Math.hypot(...p.map((v,k) => v-(samples[i][k]+samples[i+1][k])/2));
  maxMidpointChordDeviation = Math.max(maxMidpointChordDeviation,d);
}
const report = {
  curve:'Actual dist/passage.js THREE.CatmullRomCurve3 centripetal getPoint',
  source_sha256:crypto.createHash('sha256').update(source).digest('hex'),
  waypoints:module.qaPath.points.map(p=>p.toArray()),
  samples, stops:module.PASSAGE_STOPS,
  maximum_sampled_midpoint_chord_deviation_m:maxMidpointChordDeviation,
  note:'Uses the actual runtime spline. Temporary in-memory export only; no runtime source edits. Midpoint deviation is an empirical check, not an analytic curve bound.'
};
fs.writeFileSync(output,JSON.stringify(report,null,2));
console.log(JSON.stringify({samples:samples.length,source_sha256:report.source_sha256,maxMidpointChordDeviation}));
