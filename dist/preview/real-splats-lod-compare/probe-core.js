export const PRESETS = Object.freeze({
  overview: { label: '概览 · 源平面上方', position: [0, 8, 8], target: [0, 0, 0] },
  side: { label: '侧面 · 低角度', position: [7.1, 1.2, 0], target: [0, -0.2, 0] },
  back: { label: '背面 · 低角度', position: [0, 1.0, -7.8], target: [0, -0.2, 0] },
  low: { label: '贴近 · 低角度', position: [-4.9, 0.65, 5.0], target: [0, -0.2, 0] },
});
export const ALLOWED_LODS = Object.freeze([4,3]);
export function validLod(lod){return ALLOWED_LODS.includes(lod);}
export function cadence(samples,now,windowMs=5000){const recent=samples.filter(t=>t>=now-windowMs);return recent.length>1?{samples:recent.length,spanMs:now-recent[0],hz:(recent.length-1)*1000/Math.max(1,now-recent[0])}:null;}
export function mapPoint([x,y,z],[cx,cy,cz]) { return [x-cx,z-cz,-(y-cy)]; }
export function movement(keys, speed, delta, yaw, pitch) {
  let forward=Number(keys.has('KeyW')||keys.has('ArrowUp'))-Number(keys.has('KeyS')||keys.has('ArrowDown'));
  let right=Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft'));
  let up=Number(keys.has('KeyE'))-Number(keys.has('KeyQ'));
  const norm=Math.hypot(forward,right,up)||1, step=speed*Math.min(Math.max(delta,0),0.05)/norm;
  return [(-Math.sin(yaw)*Math.cos(pitch)*forward+Math.cos(yaw)*right)*step,
    (Math.sin(pitch)*forward+up)*step,(-Math.cos(yaw)*Math.cos(pitch)*forward-Math.sin(yaw)*right)*step];
}
export function outsideReference(point, origin, bounds) {
  const x=point[0]+origin[0], y=origin[1]-point[2];
  return x<bounds.min_x||x>bounds.max_x||y<bounds.min_y||y>bounds.max_y;
}
export function shaHex(buffer) { return Array.from(new Uint8Array(buffer),v=>v.toString(16).padStart(2,'0')).join(''); }
