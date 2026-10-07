// One interpreted colony placement repair; original branch and substrate meshes stay unchanged.
export const BRANCH_GROUNDING=Object.freeze({node:'Corridor_Distant_Linked_03',originalY:-0.20698136165738104,downshift:0.12711730762552115});
export function seatBranchColony(root){
 const o=root.getObjectByName(BRANCH_GROUNDING.node);if(!o?.isMesh||o.geometry.index?.count!==66504)throw Error('Grounding source changed; repeat contact audit');
 root.updateMatrixWorld(true);const m=o.parent.matrixWorld.elements;
 if(m.some((v,i)=>Math.abs(v-([0,5,10,15].includes(i)?1:0))>1e-8))throw Error('Grounding requires unchanged scene-parent transform');
 const y=BRANCH_GROUNDING.originalY-BRANCH_GROUNDING.downshift;
 if(Math.abs(o.position.y-y)<1e-10)return o;
 if(Math.abs(o.position.y-BRANCH_GROUNDING.originalY)>1e-8)throw Error('Unexpected colony starting height');
 o.position.y=y;root.updateMatrixWorld(true);return o;
}
