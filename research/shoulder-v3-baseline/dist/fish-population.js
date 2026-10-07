// Two small companions reuse the original generic meshes and materials.
// They are illustrative groups, not identified species or measured reef density.
export function addCompanionFish(root){
 for(const [from,name,scale] of [['fish_03','fish_05',.93],['fish_04','fish_06',.88]]){
  if(root.getObjectByName(name))continue;
  const source=root.getObjectByName(from);if(!source)throw Error('Missing generic fish '+from);
  const fish=source.clone(true);fish.name=name;fish.scale.multiplyScalar(scale);
  fish.traverse(o=>{if(o!==fish)o.name=o.name.replace(from,name)});root.add(fish);
 }
}
