# Unpublished basin proof — visual goal failed

This independent candidate is not an accepted product milestone. It must not replace an existing public entry.

Run `python -m http.server 8000 --bind 127.0.0.1 --directory dist` from the repository and open `http://127.0.0.1:8000/preview/reef-basin-proof/`. Click **开始连续证明段** to advance, turn 180°, swim sideways, look around 360°, and swim back to the start through the same world at a 61° field of view. The final recorded movement took about 38.5 seconds, within a roughly 42-second recording including loading. The existing navigation controller moves and resolves the route; there is no position reset during the proof.

The implementation replaces separate exhibit islands with closed curved reef volumes around an open basin, reuses the existing local normal/roughness maps, and animates individual fish headings/tails and manta wings. After the first actual render, one correction buried the reef skirts, broke up the section and crown, and repositioned the same colony budget onto the slopes. No further visual corrections were made.

Actual screenshots and both uncut recordings are in `evidence/basin-proof`. The correction reduced the floating appearance, but broad elongated platforms and scattered props remain; one turn exposes mostly bare sand, and depth layers do not persist through the whole motion. All three visual gates remain failed. Do not interpret the technical PASS as visual acceptance.

Technical verification is limited to this Windows machine's sandboxed Edge/Intel UHD at 1280×820: scene construction, source hashes, normal-FOV movement and return, load/render errors, and recorded frame gaps. It does not accept manual controls, physical mobile, exact ledge collision, other GPUs, the six-station tour, or online publication. No previous source, tag, workflow, or public site was changed.
