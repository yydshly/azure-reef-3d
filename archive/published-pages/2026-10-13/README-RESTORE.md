# Complete Azure Reef Pages byte archive

Source: published code 5a9c61c64b4734e38d09e6fc6c80d708a5152d16, Pages run 38385076150.
Original ZIP: 2,904,694,811 bytes, SHA256 2812632b4fb83d41fa39e1b9afb73c46157eda4d80f31ec18d8b63f395aeec1f.
Site inventory: 2,969 files, 4,139,910,115 bytes. This is the full current site, including all old previews and assets.

Download all three .zip.part001/.part002/.part003 assets, pages-archive.json, site-files.json, and restore-pages-archive.py into one new folder. The source-code ZIP generated automatically by GitHub for the tag is not the full Pages backup.

With existing Python 3.10+ (standard library only), run:

    python restore-pages-archive.py --manifest pages-archive.json --expected-manifest-sha256 87f15f64e8c1bdf41e14308e1ad0668fc75d5007689afabd842aba05d734b679 --output recovered-pages.zip --site-dir recovered-site --receipt recovery-receipt.json

Outputs must not already exist. The script verifies each part, concatenates the exact original ZIP, checks its original hash, safely extracts artifact.tar, and verifies every file against site-files.json. It does not deploy, modify an existing site, contact the expired artifact endpoint, or need GitHub credentials.

SHA256SUMS contains hashes of all payload, manifest and restore-script assets. Part order is fixed in pages-archive.json; do not change it. The attached asset bytes are permanent Release assets subject to normal repository ownership and deletion, with no Actions artifact expiry. Keep the manifest and hashes to detect any accidental alteration.
