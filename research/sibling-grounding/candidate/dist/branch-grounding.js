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

// Independent contact calculation for the retained sibling with unequal local Z scale.
export const SIBLING_GROUNDING=Object.freeze({node:'Depth_Staghorn_Linked_01_1',originalY:0.5899999737739563,downshift:0.10224513179842109});
export function seatSiblingColony(root){
 const o=root.getObjectByName(SIBLING_GROUNDING.node);if(!o?.isMesh||o.geometry.index?.count!==66504)throw Error('Sibling grounding source changed; repeat contact audit');
 root.updateMatrixWorld(true);const m=o.parent.matrixWorld.elements;
 if(m.some((v,i)=>Math.abs(v-([0,5,10,15].includes(i)?1:0))>1e-8))throw Error('Sibling grounding requires unchanged scene-parent transform');
 const y=SIBLING_GROUNDING.originalY-SIBLING_GROUNDING.downshift;
 if(Math.abs(o.position.y-y)<1e-10)return o;
 if(Math.abs(o.position.y-SIBLING_GROUNDING.originalY)>1e-8)throw Error('Unexpected sibling starting height');
 o.position.y=y;root.updateMatrixWorld(true);return o;
}
