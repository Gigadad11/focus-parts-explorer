# Focus Parts Explorer
Interactive exploded-view parts catalog for one specific car, built as a single HTML file with a verification pipeline
behind it. Live demo: https://focus-parts-explorer.vercel.app

Car: 2003 Ford Focus Wagon, 2.0L DOHC Zetec (VIN 1FAFP36363W1xxxxx, serial masked). Everything in the catalog is a
best-effort assumption until the verification loops or the owner confirm it; the UI shows which state each part is in.

- `index.html` — the whole product. three.js from CDN (needs internet once; cached after).
  Default data (the part-number ASSUMPTIONS) is inline at the top of the module script.
  Corrections, added parts, photos and vehicle details save to localStorage; Data → Export JSON.
- `snipe.py` — regenerates `snipe-sheet.html` / `.csv` (every part + OE numbers + retailer links) from index.html.
- Serve locally: `python3 -m http.server 8790 --bind 0.0.0.0` from this folder.
- Public: https://focus-parts-explorer.vercel.app (Vercel project focus-parts-explorer, `vercel deploy --prod --yes` to update; noindex).

Scope for now: help with this one car. Anything beyond that (public launch, any token/claimant mechanics)
is explicitly deferred and is the last thing that would ever ship, not the first.

## 3D body
The body is procedural three.js built against two reference photos in `ref/` (2003 Focus SE wagon, Light Tundra
Metallic; Mr.choppers, Wikimedia Commons, CC BY-SA 3.0): wagon side profile extruded with wheel arches and window
openings, separate hood/fenders/doors/liftgate/bumpers/roof panels, glass, lamps, wheels, seats and dash, under
PBR paint with environment lighting and shadows. Paint color is editable in the Vehicle sheet (`paintHex`).
`renders/` holds headless screenshots. URL params for testing: `?t=0.5&cam=x,y,z&target=x,y,z&shellonly=1&xray=1`.

## The loop
`./run.sh` runs everything and deploys only if it all passes. Run it after ANY edit; never hand-deploy.
1. Deterministic loops (`loops/loop_*.py` -> `reports/*.json`): `videos` (live + relevant + right generation), `links`
   (HTTP status of every generated URL; bot-walled hosts recorded as unverifiable, never as pass), `geometry` (headless render,
   every part's world bbox checked against its system's zone and the body envelope), `sheet` (flat sheet agrees with the page
   part-for-part), `stores` (addresses/phones re-read from the chains' own pages), `systems` (the Systems sheet content is
   complete: every system described, every interaction names a real system and is reciprocated, every part has does/fails/diy/tip).
2. Agentic loops, each running its own `claude -p` through `loops/agent.py` and cached on a hash of the data it judges
   (`reports/.agent-cache/`, so unchanged inputs never cost a second run; `--fresh` forces one):
   `partnumbers` (web-checks the claimed OE/aftermarket numbers of every part whose claim changed; verdict per part with
   evidence URLs; `--all`, `--ids=a,b`, `--stale-days=N`), `modelqc` (renders x-ray top/side/front views and has an agent that
   knows the real 2000-04 Zetec Focus layout judge every part's position, size and explode direction), `uiqc` (screenshots
   every sheet at phone and desktop size via the `?open=` hook and has an agent review usability for a non-mechanic owner).
3. `loops/loop_cross.py --apply` cross-checks all reports against each other and the page, applies only the safe fixes
   (dedupe numbers, confirmed numbers -> verified + reordered first, contradicted -> flagged + wrong-fit numbers removed +
   suggestion added once, wrong-generation videos dropped), writes `CROSS-REPORT.md` and blocks the deploy on any error.
   Agent opinions (model/UI QC) are surfaced as warnings and notes, never enforced; `--apply-model` also applies the model
   QC's error-severity position suggestions.
4. `loop.py --deploy`: lint -> videos -> sheet -> syntax -> stamp (build id in `<meta name="build">`) -> render (7 frames) ->
   smoke (live bounding-box check that the car is car-shaped) -> git commit + push -> vercel deploy -> verify the public URL
   carries the build id. `BUILD-REPORT.md` has the last run.
Flags to `run.sh`: `--no-agents`, `--fresh`, `--apply-model`; everything else is passed to `loop.py` (`--skip-videos`, `--skip-render`).

## Plain-English layer
`docs/systems.json` (14 systems: what it does, how it works on this car, interactions, what usually fails, a one-line refresher)
and `docs/part-notes.json` (96 parts: does / fails / diy 1-5 / tip) are injected into `index.html` by
`loops/inject_content.py` as `SYSTEM_INFO` and `PART_NOTES`. Edit the JSON, re-inject, run the loop.
URL test hook: `?open=panel:<id> | list | veh | data | help | systems | systems:<name>`.
