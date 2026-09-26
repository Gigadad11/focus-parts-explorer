# Automotive open-data landscape for the Focus Parts Explorer

Research date: 2026-09-25. Scope: open-source GitHub projects (plus the government/standards sources they sit on) that a per-vehicle exploded-view parts explorer could consume, fork, or contribute to. Target vehicle: 2003 Ford Focus wagon (ZTW), 2.0L Zetec, North American Mk1 (C170).

Method: 34 distinct web searches, then every candidate repo was checked against the GitHub REST API on 2026-09-25 for stars / forks / last push / language / licence. Where a number below is not from the API it is marked "activity unknown". Three live probes were run against the real endpoints (vPIC decode, NHTSA recalls, NHTSA complaints) for this exact car; results are quoted where relevant.

Verdict key: **USE** = consume its data/API as-is. **FORK** = good base, needs extension. **CONTRIBUTE** = active project where our Focus data or scrapers would be a welcome PR. **SKIP** = dead, wrong scope, or unusable licence.

---

## Summary: top 5 picks and why

| # | Pick | Why |
|---|------|-----|
| 1 | **NHTSA vPIC** (API + monthly SQL backup) via **cardog-ai/corgi** (333 stars, pushed 2026-04, ISC, offline SQLite ~20 MB) | The only authoritative, public-domain VIN -> year/make/model/body/engine source. Live probe on a 2003 Focus VIN pattern returned Make/Model/Year, BodyClass=Wagon, 2.0 L, 4 cyl, 130 hp, plant Wixom. Caveat: Series/Trim/EngineModel/Drive/Transmission came back empty, so vPIC alone will not distinguish ZTW from SE for a 2003 car. |
| 2 | **NHTSA recalls + complaints API** (api.nhtsa.gov) + **ODI flat files** for TSBs | Free, no key. Live probe: 7 recalls and 1,017 complaints for 2003 Focus. Wrap with **DealerShelf/NHTSA** (Python, MIT, pushed 2025-10) or call directly. TSB summaries only exist as the ODI `FLAT_TSBS.zip` flat file. |
| 3 | **foerbsnavi/OBDex** (CC0 data, MIT tooling, 9,533 generic codes, pushed 2026-08) + **Wal33D/dtc-database** (MIT, 28k codes incl. Ford P1xxx, pushed 2026-02) | Together they cover generic and Ford-specific DTCs with causes/symptoms. Both are drop-in JSON/SQLite. |
| 4 | **rsp2k/rockauto-api** (Python, MIT, 18 stars, pushed 2025-09) | The only open, structured client for a retailer that carries every part category for this car with live price and fitment. Uses RockAuto's internal JSON endpoints rather than HTML scraping. ToS-sensitive; use for on-demand lookup with rate limiting, never bulk. |
| 5 | **autopartsource/sandpim** (PHP/MySQL, MIT, pushed 2026-09-24) + **aceslint** VCdb schema | The only open implementation of the ACES/PIES data model (fitment, part types, positions, digital assets). Its schema is the right skeleton for our part/fitment tables even though the Auto Care VCdb/PCdb reference data itself is subscription-only. |

**What does not exist as open data** (we must build or scrape ourselves): OEM Ford part numbers per callout, exploded-view diagrams, aftermarket interchange (Motorcraft <-> Lester/Dorman/Gates/Moog), Hollander numbers, factory torque specs, and labor times. See "Recommended plan".

---

## VIN & vehicle tables

### NHTSA vPIC (the source itself)
- **URL:** https://vpic.nhtsa.dot.gov/api/ and https://vpic.nhtsa.dot.gov/Downloads/
- **Indexes:** WMI, VIN pattern decoding, makes, models by make/year, plant codes, equipment; ~140 decoded variables.
- **Data source / licence:** US DOT, public data, no key, no stated rate limit ("automated traffic rate control"). Monthly standalone backups `vPICList_lite_2026_09.bak.zip` (MS SQL), `.custom.zip`, `.plain.zip` (PostgreSQL) — Sept 2026 files were listed on the Downloads page at research time.
- **Endpoints of interest:** `DecodeVinValues/{vin}?format=json`, `DecodeVinValuesBatch` (POST, up to 1000 VINs), `GetModelsForMakeYear/make/ford/modelyear/2003`, `GetVehicleVariableList`.
- **Live probe (2003 Focus wagon VIN pattern `1FAFP363x3W...`):** Make=FORD, Model=Focus, ModelYear=2003, BodyClass=Wagon, DisplacementL=2.0, EngineCylinders=4, EngineHP=130, PlantCity=WIXOM; **Series, Trim, EngineModel, DriveType, TransmissionStyle all blank.** Position 8 (engine code 3 = 2.0 Zetec DOHC) is decoded to displacement/hp but not to the Zetec name.
- **Verdict:** USE (foundation). Expect thin trim/engine detail for pre-2010 vehicles.

### cardog-ai/corgi
- **URL:** https://github.com/cardog-ai/corgi
- **Indexes:** offline VIN decode + validation from a trimmed vPIC SQLite (~20 MB gz / 40 MB); returns make, model, year, series, body, drive, fuel, doors, engine, WMI, plant, check digit.
- **Licence:** ISC code; data derived from vPIC (public). DB regenerated monthly, served from `https://corgi.cardog.io/`.
- **Activity:** 333 stars, 33 forks, pushed 2026-04-25, TypeScript. Runs in Node, browser (CDN-loaded DB), Cloudflare Workers/D1.
- **Verdict:** USE. Best fit for a static/Vercel front end that must decode without hitting NHTSA on every request.

### samsullivandelgobbo/vPIC-dl
- **URL:** https://github.com/samsullivandelgobbo/vPIC-dl
- **Indexes:** pipeline that downloads the vPIC MS SQL backup, restores it, migrates to Postgres/SQLite, compresses (63 MB -> 12 MB xz).
- **Licence:** none declared. **Activity:** 25 stars, pushed 2026-03-31, Shell.
- **Verdict:** USE (build step) if we want the full vPIC tables (e.g. all Ford Focus models/years) rather than corgi's decode subset.

### heyjoeway/docker-vpic
- **URL:** https://github.com/heyjoeway/docker-vpic — one-command MS SQL container hosting the `.bak`. 0 stars, pushed 2026-09-19, no licence.
- **Verdict:** SKIP unless we need the stored procedures verbatim; vPIC-dl's SQLite is lighter.

### ShaggyTech/nhtsa-api-wrapper
- **URL:** https://github.com/ShaggyTech/nhtsa-api-wrapper — typed JS/TS client for every vPIC endpoint, works in browser and Node. MIT. 41 stars, pushed 2026-02-24.
- **Verdict:** USE for online decode + `GetModelsForMakeYear` calls from the web app.

### davidpeckham/vpic-api
- **URL:** https://github.com/davidpeckham/vpic-api — Python vPIC client with typed results. MIT. 10 stars, pushed 2024-01-30.
- **Verdict:** USE (Python side of a build script), but it is stale; the API surface has not changed, so it still works.

### Wal33D/nhtsa-vin-decoder
- **URL:** https://github.com/Wal33D/nhtsa-vin-decoder — vPIC wrapper with offline WMI fallback, Java-first with Python port. MIT. 22 stars, pushed 2025-10-23.
- **Verdict:** SKIP (redundant with corgi + ShaggyTech).

### ssrpw2/NHTSA-VIN-Decoder, arex388/Arex388.NhtsaVpic, cran/vindecodr
- SQL-Server stored-proc tweak (9 stars, 2024), C# client (1 star, 2022), R wrapper. **Verdict:** SKIP (wrong stack or stale).

### gor3a/vehicle-makes-models
- **URL:** https://github.com/gor3a/vehicle-makes-models
- **Indexes:** make group -> make -> model -> generation -> engine, 164 makes, 2,621 models, 7,169 generations, 30,390 engines; fields include cylinders, displacement, hp, torque, drivetrain, 0-100, dimensions, curb weight. JSON/CSV/SQLite, weekly releases.
- **Licence:** ODbL (data), MIT (tooling). Source is a crawl of a spec site (not named in README; treat as secondary data).
- **Activity:** 13 stars, pushed 2026-09-25 (same day), TypeScript.
- **Verdict:** USE for the year/make/model/engine picker and generation boundaries; ODbL share-alike applies to derived databases.

### plowman/open-vehicle-db
- **URL:** https://github.com/plowman/open-vehicle-db
- **Indexes:** 70 makes, 1,678 models, 9,960 styles (e.g. "PRIUS V 5DR HATCHBACK"), years 1981-2027, four CSVs joined on slugs, Python dataclass client, changelog-driven updates.
- **Licence:** none declared in API metadata; data provenance not stated in README (styles look derived from a US insurer/DMV-style list). **Activity:** 82 stars, pushed 2026-07-25.
- **Verdict:** USE with caution (no licence file) for US body-style strings like "FOCUS ZTW WAGON"; ask the maintainer to add a licence.

### vehiclesdb/vehiclesdb
- **URL:** https://github.com/vehiclesdb/vehiclesdb
- **Indexes:** 14,886 models / 918 makes / 6 kinds reconciled from official registers of 14 countries; popularity and availability per country; JSON/CSV/parquet/SQLite on jsDelivr; Ruby gem with MCP server.
- **Licence:** CC-BY 4.0. **Activity:** 13 stars, pushed 2026-09-12, DOI on Zenodo.
- **Verdict:** USE (light) for canonical make/model naming; no engines or trims.

### abhionlyone/us-car-models-data
- **URL:** https://github.com/abhionlyone/us-car-models-data — 15k US models 1992-2026, basic fields only. 528 stars, pushed 2025-11-21. README: free version frozen, specs moved to a paid subscription; licence "NOASSERTION".
- **Verdict:** SKIP (frozen, unclear licence; gor3a/plowman cover it).

### n8barr/automotive-model-year-data, arthurkao/vehicle-make-model-data
- 565 stars / 156 stars but last pushed 2017 / 2015; 7,268 model-years / 19,722 models. MIT (arthurkao), none (n8barr).
- **Verdict:** SKIP (dead; superseded).

### ilyasozkurt/automobile-models-and-specs
- **URL:** https://github.com/ilyasozkurt/automobile-models-and-specs — Laravel scraper + dump, 124 brands / 7,207 models / ~30k engine options with specs. 269 stars, pushed 2026-04-04, PHP, no licence, scraped from an unnamed spec site.
- **Verdict:** SKIP for redistribution (no licence, scraped); gor3a is the licensed equivalent.

### vbalagovic/cars-dataset
- 35k variants, 370 brands, 1898-2026, 27 stars, pushed 2026-07-08, no licence. **Verdict:** SKIP for the same reason.

### david025445/ankusi-wheel-fitment-data
- **URL:** https://github.com/david025445/ankusi-wheel-fitment-data (search also surfaced `ankusi-wheel-fitment-dataset`, which 404'd on the API on 2026-09-25)
- **Indexes:** bolt pattern (PCD), centre bore, lug count, OE wheel size/offset, aftermarket flush/max size, source URL; 6,436-9,688 variants depending on release, 1940-2027. CSV/JSON, mirrored on HF/Kaggle/figshare.
- **Licence:** CC BY 4.0 per README (GitHub API reports no SPDX licence file). **Activity:** 0 stars, 0 forks, pushed 2026-09-22, release v2026.09; effectively a one-person dataset.
- **Verdict:** USE for the wheel/hub section of the explorer.

### EPA fueleconomy.gov `vehicles.csv`
- **URL:** https://www.fueleconomy.gov/feg/download.shtml — 1984-present, ~48k rows, engine displacement/cylinders/transmission/drive/fuel per EPA ID. Public domain.
- Wrappers **hadley/fueleconomy** (R, 2020) and **ryankirkman/fueleconomy** (Go, 2015) are stale; use the CSV directly.
- **Verdict:** USE (direct CSV). It is the cleanest free source for "2003 Focus wagon: 2.0L, 4 cyl, 5-spd manual / 4-spd auto, FWD".

---

## Part numbers & interchange

### The honest finding
No open-source repository on GitHub indexes OEM part numbers per vehicle, Ford callout diagrams, or aftermarket interchange (Motorcraft/Lester/Dorman/Gates/Moog). Every hit for "interchange", "cross reference", "Hollander", or "Ford part number" was a commercial site (Hollander/Solera, Car-Part.com, 7zap, catalogs-parts.com, PartSouq, Apify actors) or a forum article on the Ford prefix/basic/suffix scheme (e.g. therangerstation.com, blueovaltrucks.com). The Ford numbering rules themselves are public knowledge and can be encoded in a small decoder, but no repo already does it.

### rsp2k/rockauto-api
- **URL:** https://github.com/rsp2k/rockauto-api
- **Indexes:** make -> year -> model -> engine browsing (295 makes, 68+ years), 21 categories / 5,314 part types / 570+ manufacturers, part search by keyword or number, price and availability, order tracking, tools catalog. Pydantic models over RockAuto's internal JSON endpoints; has header spoofing and session handling.
- **Licence:** MIT. **Activity:** 18 stars, 3 forks, pushed 2025-09-28, Python (httpx + bs4).
- **Verdict:** FORK. Good base for an on-demand "what does RockAuto stock for this callout" lookup that also yields brand part numbers (Motorcraft, Dorman, Gates, Moog) as a de-facto interchange. Respect ToS: cache aggressively, no bulk crawl.

### autopartsource/sandpim
- **URL:** https://github.com/autopartsource/sandpim
- **Indexes:** a PIM for aftermarket parts: MMY fitment, part attributes, digital assets, pricing, competitor interchange; imports/exports ACES and PIES XML (XSDs for several versions included). LAMP, no framework, Docker demo.
- **Licence:** MIT. **Activity:** 25 stars, pushed 2026-09-24; used in production by AutoPartSource for brakes/filters/exhaust.
- **Verdict:** CONTRIBUTE / FORK (schema). Do not adopt the PHP app, but copy its fitment + interchange table design; a PR adding a VCdb-free "custom vehicle" mode would be welcome given their stated goal of low barriers for casual contributors.

### autopartsource/aceslint and ACESinspector
- **URLs:** https://github.com/autopartsource/aceslint (C, MIT, 19 stars, pushed 2017) and https://github.com/autopartsource/ACESinspector (C#, MIT, 15 stars, pushed 2026-03-31)
- **Indexes:** ACES XML validators; aceslint ships `VCDB_schema.sql` and `load_VCDB_tables.sql`, i.e. the table layout of the Auto Care vehicle configuration DB.
- **Verdict:** USE (schema reference only). We cannot get VCdb data without a subscription, but mirroring its BaseVehicle/Engine/Transmission/BodyStyle IDs keeps us ACES-compatible later.

### TecDoc-derived repos
- **stanislav-web/tecdoc-client** (Node, MIT, 5 stars, pushed 2017), **ronhartman/tecdoc-autoparts-catalog** (Symfony 7, 39 stars, pushed 2026-06, no licence), **AlidaSoble/tecdoc-car-parts** (0 stars, 2025).
- All require a paid TecDoc/RapidAPI key; TecDoc is EU-centric and weak on NA Ford.
- **Verdict:** SKIP.

### chung-chris-zz/car_part_scraper, kalyanoliveira/car-parts-scrap, mbtomlinson/Rock-Auto-Price-Scrape
- Car-Part.com salvage scraper (6 stars, 2021), generic ETL (0 stars, 2023), Selenium price scraper (0 stars, 2016).
- **Verdict:** SKIP (dead). Car-Part.com is the one place Hollander interchange leaks into public HTML, so a fresh, polite scraper of it is a candidate for "what we would build".

### 2smok3d/focus-st
- **URL:** https://github.com/2smok3d/focus-st — a personal Focus ST (2017) parts and mods tracker, Python, 0 stars, pushed 2026-08-28, no licence.
- **Verdict:** SKIP for data (Mk3 ST), but worth a look at its part-record shape.

### ajay-bhojani/Awesome-Automotive
- **URL:** https://github.com/ajay-bhojani/Awesome-Automotive — curated list (54 stars, pushed 2026-09-21); the ANKUSI wheel dataset was added via PR.
- **Verdict:** CONTRIBUTE (add the Focus explorer once public).

---

## Diagrams & procedures

### iamtheyammer/fetch-ford-service-manuals
- **URL:** https://github.com/iamtheyammer/fetch-ford-service-manuals
- **Indexes:** downloads the full Ford Workshop Manual (HTML + PDF) and all wiring diagrams from Ford PTS (Motorcraft Service) for a VIN; separate flows for pre-2003 and 2003+; tested 1995-2024.
- **Data source / licence:** requires a paid PTS subscription (README: "the 72-hour subscription is fine"); code GPL-3.0; the downloaded manual is Ford copyright (personal use only).
- **Activity:** 110 stars, 27 forks, pushed 2024-08-04, TypeScript; 16 open issues; author warns it needs continuous maintenance as PTS changes.
- **Verdict:** USE (one-time). One 72-hour PTS pass yields the authoritative 2003 Focus workshop manual with torque specs, removal/installation procedures, and wiring for local extraction. That extracted text cannot be republished, but our own tables of torque values and step summaries can.

### Open Labor Project (openlaborproject.com)
- **URL:** https://openlaborproject.com/ and /developers (site returned HTTP 403 to automated fetch; details below are from search snippets)
- **Indexes:** 700k+ labor times, torque specs, fluid specs, DTCs, battery specs, NHTSA recalls; 92 makes / 35,796 configurations; Ford pages exist.
- **Data source / licence:** "community-sourced"; web pages free with no signup; REST API Hobbyist tier 50 req/day with attribution, paid from $49/mo. **No GitHub repository or open data licence found** despite the name; activity unknown.
- **Verdict:** USE (Hobbyist tier) as a sanity cross-check for torque and labor values; not a redistributable dataset.

### kase1111-hash/Mechanic-Scope
- **URL:** https://github.com/kase1111-hash/Mechanic-Scope — AR overlay of a 3D engine model with sequenced repair steps; Toyota-centric, procedures self-described as unverified drafts. C#, MIT, 1 star, pushed 2026-09-25.
- **Verdict:** SKIP for now; conceptually adjacent (3D-model-driven parts identification), watch it.

### dsmlr/Car-Parts-Segmentation, yashjain-99/car_parts_detection, Roboflow car-parts sets
- Exterior body-panel segmentation (bumper, hood, doors) for damage estimation. 110 stars, 2022.
- **Verdict:** SKIP (wrong scope: not exploded views, not mechanical parts).

### BUTTERGANG/3D-CAR-MANUAL
- Empty repo with an issue proposing "interactive exploded view and parts catalog"; 0 stars. **Verdict:** SKIP.

### Exploded-view diagram sources
- No open dataset exists. Ford's own diagrams are served by dealer sites (parts.ford.com, Levittown, oempartsonline) and by 7zap / catalogs-parts.com / PartSouq, all commercial and all Ford-copyright images. No open GitHub scraper for them was found (searches for partsouq/7zap/parts.ford.com scrapers returned only the sites themselves).
- **Conclusion:** the diagrams in this project must remain our own renders (the existing `renders/` pipeline), with callout numbers mapped to Ford basic part numbers we curate by hand.

---

## Codes / recalls / TSBs

### foerbsnavi/OBDex
- **URL:** https://github.com/foerbsnavi/OBDex
- **Indexes:** 9,533 generic P0/P2/P3/U0/U3/B0/C0 codes, each with EN+DE title/description, components, causes with likelihood, symptoms, repair difficulty/cost/hours, MIL/emissions/limp flags, cross-references, ~17k source links; plus live-data PIDs. `all.json`, `generic.json`.
- **Licence:** CC0 data, MIT tooling. Manufacturer-specific codes deliberately excluded.
- **Activity:** 3 stars, pushed 2026-08-22, JavaScript; schema-validated PRs, one code per PR.
- **Verdict:** USE (embed `generic.json`), CONTRIBUTE if we find Focus-specific symptom evidence for generic codes.

### Wal33D/dtc-database
- **URL:** https://github.com/Wal33D/dtc-database
- **Indexes:** 28,220 codes: 9,415 generic + 18,805 manufacturer-specific for 33 brands incl. Ford (`get_dtc("P1690","FORD")`); SQLite ~3.1 MB plus 37 source text files; Python/Java/Android/TS wrappers.
- **Licence:** MIT. **Activity:** 47 stars, 15 forks, pushed 2026-02-16.
- **Verdict:** USE for Ford P1xxx codes (the 2003 Focus's EEC-V throws many of these). Descriptions are one-liners, so pair with OBDex for the generic layer.

### OBDb (the OBD database) and OBDb/Ford-Focus
- **URLs:** https://github.com/OBDb (746 repos), https://github.com/OBDb/Ford-Focus, https://github.com/OBDb/.schemas, https://obdb.community
- **Indexes:** per-vehicle signalsets (PIDs, scalings, ECU addresses) in JSON. Ford-Focus has one `signalsets/v3/default.json` with 120 commands and a `generations.yaml` that documents Gen 1 (C170, 1998-2007, incl. the NA 2.0 Zetec).
- **Licence:** CC-BY-SA 4.0. **Activity:** pushed 2026-09-26 (daily), 3 stars on the Focus repo, active PRs from the maintainer.
- **Caveat:** the default signalset uses UDS service 0x22 on CAN header 0x720; a 2003 NA Focus speaks J1850 PWM with EEC-V, so those signals will not answer on this car. There is no `2000-2007.json` override.
- **Verdict:** CONTRIBUTE. Adding a Gen-1 override (Mode 01 PIDs actually supported by the 2003 EEC-V, plus the ECU list) is exactly the kind of PR the README invites, and it makes our car's OBD page correct.

### DealerShelf/NHTSA (formerly ReedGraff/NHTSA)
- **URL:** https://github.com/DealerShelf/NHTSA (ReedGraff URL now redirects)
- **Indexes:** async Python SDK for recalls (by vehicle / campaign), complaints (by vehicle / ODI number), investigations, safety ratings, vPIC, including static-file downloads.
- **Licence:** MIT. **Activity:** 7 stars, pushed 2025-10-13.
- **Verdict:** USE for the build-time fetch.

### NHTSA recalls / complaints API (direct)
- `https://api.nhtsa.gov/recalls/recallsByVehicle?make=ford&model=focus&modelYear=2003` -> **7 recalls** on 2026-09-25 (05V030000 door latch, 06E056000 fuel system, four exterior-lighting equipment recalls, 12E007000 equipment).
- `https://api.nhtsa.gov/complaints/complaintsByVehicle?...` -> **1,017 complaints**.
- No key, no published rate limit. **Verdict:** USE.

### NHTSA ODI flat files (TSBs)
- **URLs:** https://www-odi.nhtsa.dot.gov/downloads/flatfiles.cfm (page did not render via curl; links are JS-loaded), catalogued at https://catalog.data.gov/dataset/nhtsas-office-of-defects-investigation-odi-technical-service-bulletins-system-tsbs-downloa and https://data.transportation.gov/Automobiles/NHTSA-s-Office-of-Defects-Investigation-ODI-Techni/hczg-qbhf
- **Indexes:** `FLAT_TSBS.zip` (TSB summaries by year/make/model/component, ~33 MB), `FLAT_RCL.zip`, `FLAT_CMPL.zip` (the CMPL zip answered HTTP 200 at `static.nhtsa.gov/odi/ffdd/cmpl/`; my guessed TSB/RCL paths 404'd, so take the link from the ODI page). Search snippets put FLAT_TSBS last-modified at 2022-07-29; the data.gov metadata says 2018. Treat TSB coverage as historical only.
- **Licence:** US government public data. **Verdict:** USE (one-time import, filter FORD / FOCUS / 2003).

### Wal33D/nhtsa-recall-lookup, codeforamerica/recalls-python, statwonk/openNHTSA, slkjain/autobot
- Redundant recall wrapper (0 stars, 2025), usa.gov recalls wrapper (2011), R wrapper (2015), chatbot (2021). **Verdict:** SKIP.

### todrobbins/dtcdb, lennykean/OBDII.DTC, aalih34554-ai/obd2-database
- 2013 PID list (34 stars), .NET generic-code list (2023), 0-star JSON dump (2026-09, no licence). **Verdict:** SKIP (superseded by OBDex + Wal33D).

### tbohne/obd_ontology
- OWL/KG for DTC knowledge (15 stars, MIT, 2025). **Verdict:** SKIP for the app; a reference if we ever model "code -> suspect component -> part callout" formally.

---

## Pricing / availability

### rsp2k/rockauto-api
- See "Part numbers & interchange". The single open retailer client found. **Verdict:** FORK.

### eBay Browse API (official) with parts compatibility
- **URL:** https://developer.ebay.com/api-docs/user-guides/static/trading-user-guide/compatible-parts-api-support.html
- Free developer key; Browse API supports `compatibility_filter` by year/make/model/trim/engine and returns live prices. Not a GitHub project, but the only official, ToS-clean fitment+price source. **Verdict:** USE.

### AutoZone / O'Reilly / NAPA / Advance
- Only commercial Apify actors and a profile repo (`api-evangelist/advance-auto-parts`, 0 stars, a doc-only "API surface profile" of Advance's private APIs). AdvanceAutoParts' official GitHub org has one unrelated repo. No open clients found.
- **Verdict:** SKIP (nothing to fork); if store-pickup pricing matters, it is a from-scratch scraper with ToS exposure.

### Car-Part.com (salvage yards, Hollander)
- Only the dead `chung-chris-zz/car_part_scraper` (2021). **Verdict:** rebuild if used-part pricing is wanted.

---

## Standards (ACES/PIES, vPIC)

### Auto Care Association ACES / PIES / VCdb / PCdb / PAdb / Qdb
- **URLs:** https://www.autocare.org/aces, https://www.autocare.org/data-standards
- ACES = fitment XML (part -> BaseVehicle/Engine/etc. IDs), PIES = product attributes/assets/pricing XML. Both depend on reference databases (VCdb for vehicles, PCdb for part types/positions, PAdb for attributes, Qdb qualifiers). The site states these are **subscription-based**; no free, hobbyist, or open tier is mentioned and no pricing is published. There is no open mirror of VCdb on GitHub (and redistributing it would violate the subscription).
- Open implementations found: **sandpim** (import/export + PIM), **ACESinspector** (validator), **aceslint** (validator + VCdb DDL). XSD schemas for ACES 3.x/4.x and PIES 6.x/7.x are bundled inside sandpim.
- **Implication:** adopt the ACES vocabulary (BaseVehicle, SubModel, EngineBase, Position, PartType, Qualifier) and the PIES item/attribute/asset shape in our own schema, keyed to our own IDs, so that a later VCdb subscription is a join, not a rewrite.

### NHTSA vPIC
- Public, documented, bulk-downloadable monthly, no licence restrictions found on the API page. See the vehicle-tables section for the 2003 Focus decode limits.

### Ontologies (edmcouncil/auto, COVESA/akm, highmobility/auto-api)
- AUTO (OWL, MIT, 23 stars, 2024) extends schema.org/auto; AKM (MPL-2.0, signals) and Auto API (MIT, telematics) are about vehicle-generated data, not parts. **Verdict:** SKIP; optionally reuse schema.org `Vehicle` / `Car` terms in page JSON-LD for SEO.

---

## Recommended plan

### Use now (data or API, as-is)
1. **vPIC**: `DecodeVinValues` at request time (ShaggyTech wrapper) and/or corgi's offline SQLite for the static site; pull `GetModelsForMakeYear` for Ford 2000-2007 into a JSON.
2. **EPA vehicles.csv**: the 2003 Focus wagon engine/transmission/drive rows.
3. **gor3a/vehicle-makes-models** (ODbL) for generation boundaries and engine labels in the picker; **vehiclesdb** for canonical names.
4. **OBDex `generic.json` (CC0) + Wal33D `dtc_codes.db` (MIT, Ford P1xxx)** for the codes page.
5. **NHTSA recalls + complaints API** at build time via DealerShelf/NHTSA; **ODI FLAT_TSBS** imported once and filtered.
6. **ANKUSI wheel fitment** (CC BY) for hub/wheel specs.
7. **Open Labor Project** Hobbyist tier for spot-checking torque/labor values (attribution required; do not mirror).
8. **fetch-ford-service-manuals** with one 72-hour PTS subscription to get the authoritative workshop manual locally; extract torque tables and step outlines into our own words.

### Fork
- **rsp2k/rockauto-api**: add a per-callout lookup ("Zetec alternator" -> RockAuto listings) returning brand + part number + price; cache to a JSON snapshot per part group; add polite rate limiting. This is our de-facto aftermarket interchange source.
- **sandpim's schema** (not the app): lift the fitment/interchange/asset tables into our SQLite/JSON model.

### Contribute
- **OBDb/Ford-Focus**: a `2000-2007.json` (Gen-1 NA) signalset override plus ECU list, verified on the actual car with an ELM327.
- **OBDex**: Focus-observed symptom/cause refinements for generic codes (one PR per code, sources required).
- **plowman/open-vehicle-db**: request a licence file; contribute any missing Focus styles.
- **Awesome-Automotive**: list the explorer once public.

### Does not exist as open data -> we build it
- **OEM part-number index per callout** for the 2003 Focus (Ford prefix/basic/suffix, e.g. `3S4Z-10346-AA`): hand-curated from the workshop manual and dealer diagrams, stored in ACES-style tables with position/qualifier fields. Ship it under an open licence in this repo; it becomes the first open Ford Mk1 parts index.
- **Aftermarket interchange table** (Motorcraft <-> Lester/Dorman/Gates/Moog/etc.): seeded from the RockAuto lookups and brand catalogs, curated by hand, with a `source` column per row.
- **Exploded views**: continue rendering our own (the `renders/` pipeline); map callout numbers to the index above. No open diagram set exists and OEM images are copyrighted.
- **Ford part-number decoder**: a small pure function implementing the public prefix/basic/suffix rules (decade/year, car line, engineering vs. service `Z`, revision suffix).
- **Torque/labor tables**: our own table derived from the PTS manual and OLP cross-checks, with a `source` per row.
- **Retailer price/availability beyond RockAuto and eBay**: from-scratch scrapers if ever needed; assume ToS friction.
