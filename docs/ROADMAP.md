# Roadmap (draft 2026-09-26)

## Phase 0 — one car, done right (now)
- Blueprint-traced body (`loops/trace_blueprint.py`), part library (`LIB` in index.html), verification loops, public demo.
- Owner layer: phone scan (Polycam/Luma/Scaniverse GLB) or six photos + door-jamb label -> paint, wheels, trim.
- Remaining accuracy work: front/top blueprint views (paid vector), CC-BY Mk1 mesh for the front clip/interior, GrabCAD part meshes.

## Phase 1 — "new car in a day" pipeline
- VIN -> vPIC -> generation/body/engine; fetch blueprint + CC mesh + Commons photos + spec dimensions; trace; fit; place ACES-typed part library; run loops.
- Data moat: per-callout OEM numbers + aftermarket interchange with a source per row (nothing open covers this; see automotive-data-landscape.md).
- Contribute upstream: OBDb/Ford-Focus gen-1 signalset, OBDex refinements, Awesome-Automotive listing.

## Phase 2 — community and funding (gated)
- Points first, no token: contributions (verified part numbers, photos, scans, video links) earn points in a public ledger. Points are records, not promises.
- Money in: Drips / Juicebox donations + GitHub Sponsors; grants (Optimism RetroPGF-style, Gitcoin rounds) for open automotive data.
- Real capital, if needed: Reg CF (up to $5M) through a registered portal, or a Reg D 506(c) round. Both are compliant for a US person in Idaho.

## Token: parked, with the reasons
- Robinhood Stock Tokens are tokenised debt securities NOT offered to US persons (issuer's own terms). A US person seeding a Stock-Token-paired pool (Long, Pons stock pairs) is off the table. F/AZO/ORLY Stock Tokens were not even confirmed to exist.
- A transfer-tax token only works on Uniswap v2; v3 breaks, v4 does it with hooks (swap fee -> LP), which every Robinhood Chain launcher already offers. "Tax" in the token contract is a sniper/honeypot red flag.
- Low float + high FDV is the exact pattern named in the LIBRA / M3M3 / MELANIA class actions.
- SEC memecoin statement (Feb 2025) excludes tokens whose proceeds fund development; the March 2026 SEC/CFTC interpretation treats contributor rewards for work as "consideration" (Howey applies). Reg Crypto Assets (proposed Aug 2026) is not law; CLARITY Act failed cloture 2026-09-15.
- Revisit only if: a paying demand side exists (shops/parts sellers paying for the data), a lawyer signs off on the distribution mechanics, and the token is a usage/reward instrument with vesting, not a fundraise. Precedents that survived: Protocol Guild, Optimism RetroPGF, Drips, DIMO, Hivemapper.
Full research: docs/token-launch-research.md
