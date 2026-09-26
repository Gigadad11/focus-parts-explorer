# Focus Parts Explorer
Single-file interactive exploded-view parts catalog for one specific car:
2003 Ford Focus Wagon, 2.0L DOHC Zetec, VIN 1FAFP36363W175417 (Torgen's brother's car).

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
`./run.sh` = `python3 loop.py --deploy`. Stages: lint → videos (oEmbed re-check, dead links removed + logged to
dead-videos.log) → sheet → syntax → stamp (build id in `<meta name="build">`) → render (7 headless frames) →
smoke (live bounding-box check that the car is car-shaped) → git commit → deploy → verify the public URL carries
the build id. Deploy and commit are skipped if any earlier stage fails. `BUILD-REPORT.md` has the last run.
Flags: `--skip-videos`, `--skip-render`; omit `--deploy` to verify only.

## Verification loops (run before every deploy)
`run.sh` now runs, in order: `loops/loop_videos.py` (live + relevant + right generation), `loop_links.py`
(HTTP status of every generated URL; bot-walled hosts recorded as unverifiable, never as pass), `loop_geometry.py`
(headless render, every part's world bbox checked against its system's zone and the body envelope), `loop_sheet.py`
(flat sheet must agree with the page part-for-part), `loop_stores.py` (store addresses/phones re-read from the chains'
own location pages). `reports/partnumbers.json` comes from an agent pass that web-checks every claimed part number.
Then `loops/loop_cross.py --apply` checks all reports against each other and the page, applies only safe fixes
(confirmed numbers → verified + reordered first; contradicted → flagged X; wrong-vehicle videos dropped), writes
CROSS-REPORT.md, and blocks the deploy on any error. Only then does `loop.py --deploy` run.
