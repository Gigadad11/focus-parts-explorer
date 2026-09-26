# Cross-verification report
2026-09-26 16:57 UTC  apply=True apply-model=False

Loops: partnumbers {'parts': 94, 'confirmed': 18, 'plausible': 9, 'contradicted': 26, 'unverifiable': 41} | videos 180/180 live | links 3 ok, 85 bot-walled | geometry 0 flagged | sheet 0 findings | stores 4/5 confirmed | systems 0 errors | model-qc 30 findings | ui-qc score 7

## Errors (0)

## Warnings (40)
- weak title match pcm: 2002 FORD FOCUS 2.0L ECM REPLACEMENT
- weak title match muffler: How to Replace Flex Pipe 00-04 Ford Focus
- 2005-07 facelift video (same platform, check the part differs) seat-fr: How to remove front seats in a 2005 Ford Focus
- 2005-07 facelift video (same platform, check the part differs) pcm: PCM (Power Control Module) Replacement in 2005 Ford Focus
- 2005-07 facelift video (same platform, check the part differs) master-cyl: 2005 Ford Focus brake master cylinder
- 2005-07 facelift video (same platform, check the part differs) mid-pipe: ford focus 2005 EXHAUST REPAIR  (TIPS) ( all models ) ALL CARS
- 2005-07 facelift video (same platform, check the part differs) rear-bumper: 2005  Ford Focus Rear Bumper Change -Episode 5
- 2005-07 facelift video (same platform, check the part differs) windshield: ford focus 2007 style.old school,windshield replacement
- 2005-07 facelift video (same platform, check the part differs) exh-mani: 2005 Ford Focus Exhaust Manifold Removal- Part 1
- 2005-07 facelift video (same platform, check the part differs) cabin-filter: 2007 Ford Focus Cabin Air Filter Replacement PC5387X - Breathe Easier with PUREFLOW
- 2005-07 facelift video (same platform, check the part differs) seat-fl: How to remove front seats in a 2005 Ford Focus
- store AutoZone 1626 N Main St, Meridian, ID 83642: unverifiable
- systems: Cooling -> Ignition & Electrical interaction is not reciprocated in Ignition & Electrical
- systems: Exhaust -> Ignition & Electrical interaction is not reciprocated in Ignition & Electrical
- systems: Exhaust -> Body interaction is not reciprocated in Body
- systems: Transmission & Drive -> Ignition & Electrical interaction is not reciprocated in Ignition & Electrical
- systems: Suspension -> Transmission & Drive interaction is not reciprocated in Transmission & Drive
- systems: Brakes -> Engine interaction is not reciprocated in Engine
- systems: Steering -> Engine interaction is not reciprocated in Engine
- systems: Steering -> Interior interaction is not reciprocated in Interior
- systems: HVAC -> Engine interaction is not reciprocated in Engine
- systems: HVAC -> Ignition & Electrical interaction is not reciprocated in Ignition & Electrical
- systems: Body -> Ignition & Electrical interaction is not reciprocated in Ignition & Electrical
- systems: Lighting -> Interior interaction is not reciprocated in Interior
- model error wheel-fl: The wheel center is at y 0.98 with radius 1.3, so the tire sinks 0.32 below ground. The shell wheel profile puts the front wheel center at cy 1.439, r 1.439 (rear cy 1.393), so this part is 0.46 low and sits inside the arch. The same applies to wheel-fr, wheel-rl and wheel-rr (rear y 1.39). -> suggest {"pos": [5.62, 1.44, 2.98]}
- model error wheel-brg-f: The hub, rotor and CV axles are at y 1.24, but the wheel center is 1.44. The whole corner stack is 0.2 low and not on the axle line. The same applies to rotor-f, caliper-f/pads-f (+0.2), cv-axle-l and cv-axle-r (y 1.44), and wheel-brg-r, drum-r and shoes-r (y 1.39). -> suggest {"pos": [5.5, 1.44, 2.75]}
- model error rotor-f: size[0] is the radius (CylinderGeometry(r,r,len)), so r 0.95 means a 1.9-unit (about 46 cm) disc. A 258 mm rotor at about 0.244 m/unit is r 0.53. The rotor also nearly fills the wheel. -> suggest {"size": [0.53, 0.14]}
- model error drum-r: r 0.8 gives a drum about 39 cm across. A 203 mm drum is r 0.42. -> suggest {"size": [0.42, 0.2]}
- model error clutch: r 1.1 gives a clutch disc about 54 cm across, larger than the engine block is tall. The real disc is about 220 mm, so r 0.45. -> suggest {"size": [0.45, 0.3]}
- model error alternator: r 0.75 gives an alternator about 37 cm across (the real one is about 13 cm). It also overlaps the block, the water pump, the A/C compressor and the 2.4-wide exhaust manifold at the passenger end. -> suggest {"size": [0.28, 0.6]}
- model error ac-comp: r 0.65 gives about 32 cm across. It is also centered at x 6.4, which is inside the block (x 4.77–6.67). -> suggest {"pos": [6.95, 0.95, -1.0]}
- model error timing-belt: The box is [0.3,2.6,2.2], so it is thin in x and runs 2.2 along z, the crank axis. The belt plane should be perpendicular to the crank (x-y plane). As modeled it cuts through the block from z -2.6 to -0.4. -> suggest {"size": [2.0, 2.6, 0.3]}
- model error serp-belt: Same orientation error as timing-belt: [0.25,2.6,2.2] runs along the crank axis and goes through the block. -> suggest {"size": [2.2, 2.4, 0.25]}
- model error spark-plugs: The plug/coil row is 2.4 long in x (fore/aft), but the cylinders are in line along z on a transverse engine. -> suggest {"size": [0.5, 0.35, 2.2]}
- model error mid-pipe: At z -1.6 with r 0.3, the pipe spans z -1.9 to -1.3 and y 0.2 to 0.8, so it passes through the fuel tank (z ±1.5, y 0.5–1.4). r 0.3 is also a 15 cm pipe; the real one is about 5 cm. -> suggest {"pos": [-1.5, 0.45, -1.8]}
- ui high [visual]: On the phone the car is drawn small. At 60% explode (ui-exploded-phone) the 96 parts are packed into a band about 390x180px in the upper-middle of the screen, and the bottom ~40% is empty grid. Pinch is used for exploding and zoom is turned off (controls.enableZoom=false), so there is no way to make small parts such as sensors, filters or plugs big enough to tap. -> In resize(), when innerHeight>innerWidth, set camera distance so the car's bounding box fills about 90% of the width (dist = (carLen/2)/Math.tan(fovH/2)), and lower controls.target.y by about 1.5 so the car sits in the vertical middle. Add double-tap-to-zoom: on a double pointerup, lerp the camera toward the raycast hit point to 50% distance. Show a 'Reset view' button while zoomed.
- ui high [panel]: When a part card opens, the part itself cannot be seen. In ui-panel-phone and ui-panel-flagged-phone the card is open, the car is still at 0% explode in Full car view, and the alternator and water pump are hidden inside the body. In ui-panel-desk the body is see-through but the part is barely highlighted. select() only reveals the part when opts.reveal is set, and lookAt() stores lookTarget but the camera does not visibly frame the part. -> Always call select(m,{reveal:true}) from list, search and system chips. When a part is selected, also: fade the other parts to 0.15 opacity instead of 0.45, set emissive to 0xff8a20 with a 1Hz sine pulse in the render loop, and on the phone move controls.target to the part and the camera to 60% distance so the part appears in the top 34% of the screen above the sheet.
- ui high [first-run]: The exploded view is about 96 grey and colored blocks with no labels. A non-mechanic has to tap blindly to find out what anything is. Nothing on screen says 'this is the battery' or 'engine bay is here'. -> On pointermove (desktop) and on touchstart held 300ms (phone), raycast and show a floating label <div id=tag> at the part's screen position with p.name. Also, when explode is above 0.3, show 6–8 fixed labels ('Engine', 'Radiator', 'Battery', 'Brakes', 'Fuel tank') projected from the system centroids, styled as .chip with pointer-events:auto so tapping one runs setSystem().
- ui high [systems]: In the system detail 'How it works on this car' paragraph (ui-system-cooling phone and desk), the inline part chips keep min-height:32px, padding 6px 12px and a 3px margin. Every line with a chip becomes about 40px tall, so the prose reads as broken fragments with large gaps between lines. -> Add a scoped rule for chips inside prose: .how .chip{display:inline;min-height:0;padding:1px 7px;margin:0 1px;line-height:1.4;font-size:inherit;border-radius:6px;vertical-align:baseline}. Keep tap area with .how{line-height:1.9}, or use underlined links (color:var(--or2);text-decoration:underline dotted) instead of pills in running text.
- ui high [panel]: The alternator card shows 7 part numbers (GL-456, 1S41-…, 98AB-…, Lester, DB, WAI, Remy), all given equal weight. A layperson at the counter doesn't know which one to ask for. The flagged water pump card handles this well with 'Use one of these'; the confirmed card has no equivalent. -> Render the first confirmed OE number as a highlighted .pn.use row with the label 'Ask the counter for this one'. Put the other Ford numbers and aftermarket brands inside <details><summary>Other numbers that fit (6)</summary>…</details>.

## Agent QC notes (34)
- Model QC (+z = LH): Left/right handedness is consistent: LH/driver is +z. Every system is on the correct side and end of the car, and the intake/exhaust orientation is correct. The main problem is systematic: the renderer treats cyl size[0] as the radius, but most rotating parts were sized as if it were the diameter. That makes rotors, drums, the clutch, alternator, water pump, A/C compressor, fan, starter, pipes and hoses 2–3× too big, and it causes the pile-up at the passenger belt end. The wheel/hub stack sits 0.2–0.46 below the shell's wheel center (1.44), and both belts and the spark-plug row are rotated 90°. The mid pipe also runs through the fuel tank.
- model warn flex-pipe: r 0.25 gives a pipe about 12 cm across; the real front pipe is about 5 cm. -> suggest {"size": [0.1, 4.6]}
- model warn exh-mani: [1,1.8,2.4] covers the whole front face of the block, end to end. It swallows the alternator, O2 sensor and A/C region, and reaches x 7.4, nearly touching the fan. -> suggest {"size": [0.8, 1.6, 1.6]}
- model warn water-pump: r 0.7 gives about 34 cm across (the real one is about 10 cm), and it overlaps the alternator and the block. -> suggest {"size": [0.25, 0.3]}
- model warn ps-pump: At [5.4,3,-1.8] with r 0.5, it overlaps strut-fr (x 5.1–5.7, z -2.6 to -2.0), motor-mounts and the belts. -> suggest {"pos": [4.7, 2.5, -1.6]}
- model warn motor-mounts: At [5.7,3.2,-2.2] the 0.8 cube overlaps strut-fr and the coolant degas bottle, so three parts share the same space. -> suggest {"pos": [6.0, 3.5, -1.9]}
- model warn coolant-res: It overlaps motor-mounts (x 5.75–6.1, z -2.6 to -2.15). -> suggest {"pos": [6.9, 3.1, -2.5]}
- model warn rad-fan: r 1.1 gives a fan 2.2 across, taller than the radiator (1.6), so it sticks out above and below the core. -> suggest {"size": [0.72, 0.3]}
- model warn oil-filter: [0.45,0.9] gives a filter about 22 cm across and 22 cm long. The FL-400S is about 76 × 100 mm. -> suggest {"size": [0.16, 0.4]}
- model warn starter: r 0.55 gives about 27 cm across; the real starter is about 9 cm. -> suggest {"size": [0.2, 0.8]}
- model warn throttle-body: r 0.6 gives about 29 cm across; the real bore is about 55 mm. -> suggest {"size": [0.2, 0.35]}
- model nit rad-hoses: r 0.25 gives a hose about 12 cm across; the real hose is about 3.5 cm. -> suggest {"size": [0.08, 1.6]}
- model nit blower: r 0.7 gives about 34 cm across. -> suggest {"size": [0.35, 0.5]}
- model warn heater-core: [0.3,1.6,1.8] is about 39 × 44 cm, far too big. Its ex [0,5,0] is the same as dash, so it never separates from it when exploded. -> suggest {"size": [0.25, 0.7, 1.1]}
- model warn fuel-filter: At x -2.4, z 1.2 it is inside the fuel tank volume (x -4.1 to -1.5, z ±1.5). -> suggest {"pos": [-1.1, 0.6, 1.2]}
- model nit fuel-tank: 2.6 × 0.9 × 3.0 units is about 63 × 22 × 73 cm, roughly 100 L, which is double 13.2 gal (50 L). -> suggest {"size": [2.2, 0.75, 2.8]}
- model warn strut-fl: The strut bottom (y 1.8) at z 2.0–2.6 goes into the transaxle top (y ≤2.9, z ≤2.4). It is also inboard of the hub (z 2.75) instead of above the knuckle. The same applies to strut-fr on the passenger side. -> suggest {"pos": [5.4, 3.3, 2.55]}
- model nit caliper-f: 0.9 × 0.9 × 0.5 is about 22 cm, oversized. Once the rotor is shrunk to r 0.53 it also floats off the disc. -> suggest {"size": [0.45, 0.6, 0.35]}
- model nit maf: It sits inside the airbox volume (x 5.2–6.6). -> suggest {"pos": [5.0, 3.6, 1.5]}
- model nit taillamp-l: y 3.0 ± 0.8 is sedan height. The wagon lamps are tall units on the D-pillar. The same applies to taillamp-r. -> suggest {"pos": [-9, 3.8, 2.8]}
- UI QC score 7/10, 18 findings
- ui med [jargon]: Many terms appear without any explanation: 'DOHC Zetec' in the header, 'serpentine belt', 'degas bottle', 'transaxle', 'Motorcraft', 'OE/OEM', 'MTX-75 / 4F27E', 'VIN code 3', 'ZTW', 'reman', and 'Lester 8260'. Help has a 'Words you will see' glossary, but nothing links to it from where the words appear. -> After rendering each sheet, wrap known glossary terms in <abbr class=g data-g="term"> (style: border-bottom:1px dotted #e8a56a; cursor:help). Tapping one shows the glossary definition in the toast, or in a small popover that stays until tapped away. Change the header to '2003 Ford Focus Wagon · 2.0L engine'.
- ui med [labels]: Several toolbar labels are unclear to a layperson. 'Car' is vague when the whole app is a car. 'List' doesn't say what it lists. '👁 Full car' shows the current state rather than what tapping will do, and nothing shows that it cycles through three modes. '⋯' hides Backup and Add part with no hint. -> Rename: 'Car' → 'My car', 'List' → 'All parts', bView → 'View: Full car ▾' (or three toggle buttons: 'Outside' / 'See-through' / 'Parts only'), '⋯' → 'More'.
- ui med [nav]: On the phone the system filter is removed (#tools select{display:none}), so the only way to narrow the 3D view or the All parts list to one system is through the Systems sheet. The list sheet itself has no filter chips, and 96 items take a long scroll. -> At the top of #lbody, render a horizontal scroll row of system chips (All · Engine · Cooling · Brakes …) using .chips{flex-wrap:nowrap;overflow-x:auto}, each calling setSystem(s); renderList(). Show the active one with class .on.
- ui med [panel]: The DIY line runs difficulty, tools and a part-number warning together in one 12px grey sentence ('weekend job, jack + torque wrench · Lester 8260 for this car, not 8418 or 8406…'). The number advice gets lost, and 'Confirm belt tension and the battery first' (a diagnosis tip) is hidden in it. -> Split into three lines: '<div class=diy>Difficulty ●●●○○ weekend job · needs jack + torque wrench</div>', then '<div class=notes>Check first: …</div>' placed right after the 'When it's going' line, and move any number-specific tip into the Part numbers section above the rows. Raise .diy to 13px and #bbb.
- ui med [labels]: The trust explanation under PART NUMBERS starts lowercase and uses internal pipeline wording: 'the original number turned out to fit a different car…' and 'Use one of these (found by verification, confirm on the car)'. 'Verification' means nothing to the owner. -> Capitalize the CONF_HELP strings. Replace 'found by verification' with 'double-checked against a seller listing'. X copy: 'Our first number was for a different Focus. Use the green one below; match it to the old part before paying.'
- ui med [visual]: On desktop the car isn't moved over when a sheet opens. In ui-panel-desk, ui-list-desk and ui-systems-desk the front of the car (headlamps, bumper) sits under the 440px sheet. camera.setViewOffset is only applied when innerWidth<=700. -> In open(): if(innerWidth>700) camera.setViewOffset(innerWidth,innerHeight,sheetW/2,0,innerWidth,innerHeight) where sheetW=sheets[k].offsetWidth+12. This moves the car left into the free area.
- ui med [editor]: The Backup & fixes sheet shows three large dt/dd rows of '0' and puts a red 'Erase all my fixes' button right under 'Save a backup' even when there is nothing to erase. 'Copy backup text' is unclear. -> Replace the three counts with one line: n?`${n} fixes saved on this phone`:'No fixes yet — nothing to back up.' Hide or disable the Erase button when n===0, and move it into a <details><summary>Danger zone</summary>. Rename to 'Copy backup (to paste in a note or email)'.
- ui med [panel]: Almost every row in All parts carries a mustard 'number needs checking' badge (ui-list phone and desk). This teaches the owner to ignore the badge, and on the phone the badge wraps to its own line under long names (Timing belt kit). -> In the list, replace the text badges with a 10px colored dot plus a short word (✓ / ? / !), e.g. <span class="dot cX" title=…>check</span>. Keep the full wording in the part card. Style .item .badge{white-space:nowrap;font-size:10.5px;margin-left:4px} and float it right.
- ui low [nav]: On desktop the ⋯ button wraps onto its own second row under the tool buttons (ui-home-desk), which looks accidental. The 'All systems' dropdown and the 'Systems' button sit next to each other, doing different things with similar names. -> Set #tools{width:min(360px,46vw)} or #tools .row{flex-wrap:nowrap} so everything fits on one row. Rename the select's first option to 'Show on car: all systems' so it reads as a 3D filter rather than a second Systems page.
- ui low [first-run]: The desktop-oriented hint 'scroll wheel = explode dial · two-finger pinch on touch' appears in the phone renders at 390px (the pointer:coarse rule doesn't catch every phone or emulator). 'Explode dial' is also a term the UI doesn't use; the control is labeled 'Explode'. -> Add #hint to the max-width:700px block: @media (max-width:700px){#hint{display:none}}. Change the desktop copy to 'mouse wheel also pulls the car apart'.
- ui low [panel]: The three action buttons in the part card look inconsistent. 'Watch how-to' is a solid orange link, 'Buy nearby' is a grey <button>, and 'Prices online' is an a.snipe with orange text and different padding and height. All three should look like equal-weight siblings. -> Give all three a shared class .act{flex:1;min-height:44px;display:grid;place-items:center;border-radius:8px;font-size:13.5px}. Keep .pri for 'Watch how-to' and use the same neutral style for 'Buy nearby' and 'Prices online'. Add '↗' to the two that open another site.
- ui low [systems]: The Car sheet's 'Help finish this' callout says 'tap Edit below', but the Edit control is far below the fold on the phone (not visible in ui-vehicle-phone). -> Put the actions inside the callout itself: <div class=row><button class=pri data-act=editveh>Enter it now</button><button data-act=photo>📷 Photo the door sticker</button></div>.
- ui low [touch]: The 'copy' pills inside part-number rows are about 20px tall (padding 2px 6px, 11px text). The whole .pn row is tappable, but the pill looks like the only target and is too small. -> Remove the pill and put a trailing icon inside the full-row button: .pn::after{content:'⧉ copy';color:#e8a56a;font-size:12px}. After copying, toast 'Copied GL-456 — paste it into the store search'.

## Fixes applied (26)
- flag eng-block
- flag valve-cover
- flag timing-belt
- flag oil-pan
- flag serp-belt
- flag spark-plugs
- flag thermostat
- flag water-pump
- flag rad-hoses
- flag coolant-res
- flag throttle-body
- flag airbox
- flag maf
- flag exh-mani
- flag strut-fl
- flag strut-fr
- flag sway-f
- flag rear-blade
- flag wheel-brg-f
- flag drum-r
- flag ps-pump
- flag heater-core
- flag liftgate
- flag mirrors
- flag window-reg
- flag wheel-fl
