# Single-thicket morphology experiment

## Reference and scope

The inspected reference is NOAA's staghorn coral photograph and species profile: https://www.fisheries.noaa.gov/species/staghorn-coral . It supports comparison of continuous axes, unequal lateral shoots and pale growing tips. It is not a survey of the synthetic scene or proof of its colony density.

Published baseline model SHA-256: deac6a8e6d2173fc649023b763264f3b195fc5c084bf5a2c58c3ca76c4abcb0e.
Target: Coral_Staghorn_Thicket_01. All lighting, palette, camera and surrounding scene are held fixed for morphology comparisons. The offline fixture has light/fog/PBR but no projected caustics.

## Proven defect

The original tube generator shrinks every final ring to 38% of its radius, including nonterminal segments. A parent end becomes 0.304 of its initial radius, while its next segment starts at 0.77, a 2.53-fold radius discontinuity. This is a generator artifact, not a feature inferred from NOAA.

## Rejected experiments

V1 joined 12 continuous axes into one connected mesh. It removed visible pinches but made the crown sparse and exposed spoke-like low arms. Owner and independent image review rejected it.

V2 added staggered side shoots and repaired substrate attachment. Geometry and guide/route checks passed, but fixed close and neutral views still showed a comb-like branching rhythm and a conspicuous connected basal structure. It was also rejected as a replacement. Neither candidate was deployed or propagated.

The scope assumption was corrected: the baseline object is a multi-stem thicket, not a verified single biological colony. Requiring the entire object to be one connected component imposed an unsupported growth structure. More shoot-count tuning is not the next step.

## Revised finite test

Preserve the original axes, terminal endpoints, density, independent basal networks, placement and material. Repair only actual nonterminal parent-child transitions. Do not weld incidental crossings or separate basal networks. Accept only if representative joints visibly improve in matched detail/front/back views while the original crown silhouette and substrate contact remain essentially unchanged. This would establish a specific geometry correction, not completion of the overall realism goal.
