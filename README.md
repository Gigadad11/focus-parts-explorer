# Focus Parts Explorer
Single-file interactive exploded-view parts catalog for one specific car:
2003 Ford Focus Wagon, 2.0L DOHC Zetec, VIN 1FAFP36363W175417 (Torgen's brother's car).

- `index.html` — the whole product. three.js from CDN (needs internet once; cached after).
  Default data (the part-number ASSUMPTIONS) is inline at the top of the module script.
  Corrections, added parts, photos and vehicle details save to localStorage; Data → Export JSON.
- `snipe.py` — regenerates `snipe-sheet.html` / `.csv` (every part + OE numbers + retailer links) from index.html.
- Serve: `python3 -m http.server 8790 --bind 0.0.0.0` from this folder.

Scope for now: help with this one car. Anything beyond that (public launch, any token/claimant mechanics)
is explicitly deferred and is the last thing that would ever ship, not the first.
