# Bounded runner preparation recovery

Run37666030793 was cancelled at the22-minute job limit during the official Playwright system-dependency install. Logs stop at the runner apt mirror jammy-updates index. WebGL probe and all scene rendering were skipped; there are no shader or visual results from that run.

The same Ubuntu22.04 job now downloads pinned official Chromium separately, checks its linked libraries with ldd, and uses already-present runner libraries when complete. Only missing libraries trigger the same official dependency installer, bounded to120 seconds. Browser sandbox and graphics security flags remain unchanged. Candidate and observation protocol are byte-identical; one recovery run is requested. No mirror or network-security settings are changed.
