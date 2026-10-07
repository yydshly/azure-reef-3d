# Cost separation diagnosis, not a product candidate

Actual run37600639623 passes four sequential diagnostic states at fixed departure/reduced motion with unchanged scene assets. Each state has3 RAF warmup then two approximate15-second observation intervals with no intermediate screenshots. Actual intervals are recorded rather than replaced by requested wait durations.

Default1120×700 with shadows:.270787/.271701 RAF/s; no-shadow at the same pixels:.322879/.323125; half pixel ratio560×350 with shadows:.395606/.395768; restored default:.269792/.271022. Default draw work128 calls/2,053,361 triangles; no-shadow77 calls/1,083,477 triangles; half pixels retain the default draw work. These are renderer counters, not unique model triangles.

The approximately19% no-shadow and46% quarter-pixel relative rate increases indicate useful cost centers in this software setting. Every interval has only5–6 callbacks; all conditions remain extremely slow. The restored-default drift is small in this run, but neither device performance nor a lower-quality shipping setting is accepted. All screenshots are explicitly marked diagnostic. No production changes result from this experiment.

Owner pixel review confirms neither diagnostic setting is a shipping candidate: half resolution visibly blurs details, while disabling shadows weakens ground contact and cavity layers. Multiple costs are implicated; this does not isolate geometry as the sole bottleneck. No additional condition scan follows this run.
