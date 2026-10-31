# Saracen Bridge Studio: Standalone Engine Architecture

**Version:** 1.0.7, 15 October 2026
**Status:** a launcher of independent tools, like Jon's GPT list. Calculation tools work offline now; writing tools wait on an AI engine choice.

## 1. The principle

Jon's GPTs mix three things in one chat window: his rules, his calculations, and a model's judgement. The standalone pulls them apart:

| Layer | Does | Runs on | Can it invent a number? |
|---|---|---|---|
| **Engine** (Python) | All arithmetic, gates, scores, caps, double-count checks | This computer | No. It is code with tests |
| **Reference data** (SQLite) | Programme rules, FX, rates, accounts, talent, brands, BFI points | This computer | No. Loaded from Jon's files with provenance |
| **Local model** | Reads scripts, contracts and decks; drafts narrative | This computer (Ollama) | No. Its output is a *Proposal* until a person confirms it |
| **Renderers** | Branded .docx/.xlsx/PDF from engine output | This computer | No |
| **Rules refresh** | Re-checks official sources on demand | The only outbound call | It proposes diffs and a person approves them |

ChatGPT is gone from every path. Nothing needs the internet except the optional, user-triggered rules refresh.

Jon's newest tool, the Production Agreement Builder, was already built this way: the model proposes, the scripts write, and assets are hash-locked. The rest of the suite follows his pattern.

## 2. What exists now

### The product (changed in 0.2)

0.1 opened on one sample project's finance numbers. That was wrong. 0.2 works like the GPT site: a home screen of tools, grouped as Jon grouped them, each opened on its own and each keeping its own history.

| Group | Tool | Works offline now | Needs an AI engine |
|---|---|---|---|
| Development | 02 Script Coverage | Batch intake (PDF, .fdx, Fountain, file or folder), breakdown, Library, weighted scoring matrix | **Built:** Jon's full 11-section coverage and a branded Word report, through a resumable queue |
| | 01 Look Book Analytics | (nothing yet) | All of it (reads images) |
| Production | 03 Scheduling & Budgeting | Script breakdown; crew rates for 13 jurisdictions | Element tagging, budget build |
| | 06 Location & Incentives | 76 audited programmes (69 active), route comparison, gates | None |
| | 07 BFI Certification | Cultural Test scorer: proposed vs conservative, caps, golden-points rule | Reading the script for A1–A3 |
| Sales & Marketing | 04 Sales Estimates | Director (500, fee bands) and actor (1,004) lookups | Valuation narrative; engine port pending |
| | 05 Brand Integration | 110-brand database; script intake | Scene-by-scene opportunities |
| Finance | 08 Finance Plan | Sources and uses, package and residual-debt sizing, double-count check | Reading term sheets |
| | 09 Greenlight & Closing | Jon's decision rules (55 / 80 / 90 and sub-score minimums) | Data-room audit (243-check matrix awaited) |
| | 10 Term Sheet Builder | Jon's own workflow, in-process | None |
| Creative | Storyboard | Opens **A.I.D.E.N.** | (separate program) |
| | Visual Feedback | Opens **F.R.A.T.** | (separate program) |

The SHADE figures survive only as an optional "Load SHADE example" button in Finance Plan, and as test data.

### 0.4 (13 Oct): the look, the window, the assistant

- **Design ("The Screening Room").** A new interface throughout: an inset app sheet, a cinematic home banner, one tool grid with filters, 3D tilting cards, a pressable gold button, toasts, modals and a Ctrl+K command palette, in richer purple, sharper gold and black. Fonts bundled. Details, motion rules and research: `docs/DESIGN.md`.
- **The 3D crest.** Jon's crest and wordmark traced to vectors from his own artwork and rendered as layered SVG metal with CSS depth (rail, start-up intro, app icon, installer panels). Brand sign-off: S-35.
- **The Studio window (Tauri 2).** `studio-window.exe` (3.3 MB, plus Microsoft's signed `WebView2Loader.dll`) is a native window around the local page: a dark title bar coloured through DWM on Windows 11 (the native frame keeps Snap Layouts), the crest icon, web links sent to the default browser, and dropped files left for the page. The launcher starts the engine, opens this window and stops the engine when it closes. If the window cannot show the page within 25 s, the launcher falls back to the Edge app window of 0.3.4–0.3.5 (`--no-shell` forces that). Cross-compiled on Linux with mingw-w64 (`packaging/shell`).
- **Ask Jon** (named Ask Saracen in 0.4.0). An assistant drawer on every page (button in the top bar, Ctrl+J). It knows the twelve tools and, unless switched off, reads the page on screen, so it can walk a user through a tool, explain a result or give notes on the film. It never computes figures: it explains them and links to the tool. Answers stream. It runs on the local engine.
- **Jon (0.4.1).** A helper character (a cartoon clapperboard) docked bottom right: click him for Ask Jon; he offers help when someone looks stuck, under rules taken from Clippy's failure (one tip per page, never while typing, snooze and switch-off). Ask Jon answers from Saracen Bridge's own documents: `scripts/build_knowledge.py` indexes 51 of Jon's documents (1,022 sections) into `data/knowledge.db` (SQLite FTS5, BM25, title weighted over body); each question retrieves five sections, the page's own tool first, and the answer lists them. Details: `docs/DESIGN.md`.
- **0.4.2–0.4.6.** Look Book Analytics ships: decks are read page by page as images by Gemma's vision add-on (the installer adds the 175 MB add-on for the 12B, or the E4B's, beside a chosen or kept model), then Jon's 16-section analysis. Sales Estimates has a type-ahead name finder over the actor and director databases, with full profiles and Jon's attachment-certainty ladder. The built-in engine runs two slots with their own full context (`-np 2 --no-kv-unified`, one slot if memory is short), so a background job and Ask Jon can't take each other's room; Deep mode thinks within a budget (`reasoning_budget_tokens`); Ask Jon fits each request to the context and keeps its sources to the page's subject; no model names on screen outside Settings and report colophons. Register S-39 to S-49.
- **0.4.7.** Look and feel: every selected control carries one gold gradient (S-50); tool pages open straight on their title, the category staying in the breadcrumb (S-51); the display serif is Source Serif 4, about 20% wider than Instrument Serif, and the interface is scale-locked: one uniform zoom (`--uiz`, set by `uiScale()` in `ui/studio.js`, Auto or pinned in Settings › Display) with viewport units divided by it (S-52). See DESIGN.md.
- **1.0.1.** Named by Tim. The sidebar's privacy lamp (S-53); copy that no longer promises offline-only while Cloud exists (S-54); Visual Feedback Coming soon, "Ready · more coming", "Coming soon" lists (S-55); failed jobs clear one at a time or all at once, `POST /api/jobs/clear`, status `cleared` (S-56); Brand Integration's shortlist (`GET/PUT /api/brand/shortlist`, `/api/brand/shortlist.csv`) and per-script brand targets (`PUT /api/runs/brand/{id}/targets`, set at intake from the shortlist) (S-57).
- **Optional cloud AI (bring your own key).** Off by default. In Settings the user can switch on their own Claude, ChatGPT or Gemini account, choose a model (listed from their account) and tick what it serves: Ask Saracen, and/or the writing tools (coverage). The key is kept only on that PC, encrypted with Windows DPAPI for the signed-in user (`cloud_keys.json`, never in `settings.json` and never sent back to the page). Turning it on asks for confirmation; every cloud answer carries a **Cloud** tag. With writing tools ticked the whole script goes to the provider, which the confidentiality rule weighs against (S-34).

### 1.0.8 and 1.1.0 (17 Oct): the Room

A private team space per production, end-to-end encrypted, beside the tools (register S-79 to S-90).
- **Who hosts.** Whoever starts a production hosts it (Tim's ruling, 17 Oct): their Studio runs the Room's hub (`engine/room_hub`, FastAPI) inside the Studio on its own listener, port 8710 on the network, with LiveKit 1.13.10 beside it for calls (TCP 7880 and 7881, UDP 50000 to 50100), and makes them the executive who invites, approves devices and sets access (`engine/studio/room/host.py`). The Studio's own pages and API stay on 127.0.0.1. A Studio in several hosts' productions keeps one Room per host (`%APPDATA%\SaracenStudio\room` and `room\hubs\<id>`) and shows every production in one switcher; each request goes to the host that holds its production, space, item, file or meeting (`service.resolve`).
- **What the hub sees.** Ciphertext only. Each device holds X25519 and Ed25519 keys (sealed with DPAPI on Windows); each space has a key per epoch (XChaCha20-Poly1305), sealed to each member device and signed; items carry one key wrapped for each space they're shared to; files go in 4 MB encrypted chunks and resume. The hub enforces membership as well (hidden, not locked), keeps an append-only, hash-chained audit log, and deletes archived productions 90 days on.
- **Joining.** An invite link carries the host's address and a one-time code. The new device and an executive compare three safety words (commit-then-reveal, BIP39 list, the founder's key in the hash); trust runs by signature from the founder's device, so the hub can't add a device.
- **Calls.** Huddles and meetings of up to 75 on LiveKit; executives decide who is on stage; the media key rides in the encrypted meeting item, so LiveKit never has it; nothing is recorded.
- **Phones.** The hub serves the Room as an installable web app (`room_hub/static`) with the same encryption (libsodium.js); notifications carry only a production id.
- **Code.** `engine/room_crypto` (shared formats, mirrored in `room_hub/static/room-crypto.js`), `engine/room_hub` (hub, meetings, push, retention), `engine/studio/room` (client, service, routes, call sheets, meetings, host), `ui/room*.js`. Tests: `tests/test_room_*.py`.

### Scripts at scale

- Intake reads in batches of 10 and saves each script as its own Library item. A file that can't be read is reported and the batch continues.
- Each file's SHA-256 is recorded. The same file dropped again is skipped, so a stopped batch of hundreds picks up where it left off.
- **Territory sales valuation (1.0.5, `engine/studio/sales.py`, `engine/studio/xlcalc.py`).** Jon's Sales Valuation Engine v4.1 workbook is bundled and evaluated as written: the project's inputs are written into his input cells only, `xlcalc` evaluates his formulas (operators, 21 functions, Excel's blank/text/error rules), and CONTROLLED_OUTPUT, FINANCE_SUMMARY and his controls are returned. The parsed workbook stays in memory; inputs from the previous valuation are reset first. `GET /api/runs/sales/{id}/engine.xlsx` gives the filled workbook for Excel. Checked against Excel's saved values and LibreOffice (S-65, S-66).
- **Schedule and budget (1.0.4, `engine/studio/budget.py`).** From a script's breakdown: scene lengths in eighths; a stripboard per case (day scenes then night scenes, by site, scenes split across days to fill them) at 5 / 4 / 3 pages a day; day-out-of-days per speaking role; budget lines on Jon's chart of accounts priced from his rate card for the chosen jurisdiction, region factors and crew tier; producer figures override any line; Unknown is never zero. Saved on the script's Library item (`outputs.budget`); `GET /api/runs/{tool}/{id}/budget.xlsx` builds the workbook (top sheet as SUMIFS formulas over the detail). Sources for every non-Jon assumption are in `budget.SOURCES` and on screen (S-64).
- The screenplay reader is versioned. When it changes (1.0.3: colon headings such as "INT: KITCHEN – DAY", S-59), the Library re-reads older scripts once in the background on the next start, replaces titles the reader made up, and marks coverage written from the old reading "Write again".
- Saved runs of the calculation tools (Finance, Incentives, BFI, Greenlight, Term Sheet) open in the Library as the same result the tool page shows, with what was entered (1.0.3, S-60).
- The Library is indexed (`library.db`) for search and paging. The run folders are the record, and the index rebuilds from them if deleted.
- Measured in the build workspace: 1,000 Fountain scripts (23 MB) in 23 s; a 48-page PDF in 0.63 s (13 ms/page); first Library page 15 ms at 1,000 items. Tim's PC will differ; nothing has been measured there yet.
- **Scanned scripts (1.0.6, `engine/studio/ocr.py`).** A PDF whose text layer averages under 40 characters a page is read by OCR on the same PC: PDFium renders each page at 200 dpi and Tesseract 5.3.0 (Universität Mannheim's signed Windows build, Apache-2.0, English model; installed in `_internal\ocr`) returns word boxes, which are put back into screenplay lines (indentation from each line's left edge, blank lines from the gaps) so the same reader finds headings and cues. Pages run side by side, one Tesseract thread each, one fewer than the processor count up to 4; the result is cached by SHA-256 in `ocr/` under the Studio's data folder. Intake runs off the server's event loop and `GET /api/tools/script/ocr` gives pages read of pages for the progress line. The reading is marked "PDF (scanned, read by OCR)" with a warning to check names and headings (S-12, S-67). A PDF mixing typed and scanned pages is read from its text layer only.
- A leading "." forces a scene heading only in Fountain, and only before some text; in a PDF it is ordinary text (1.0.6, S-68).
- **iPhone app (`ios/`, the team companion).** `ios/Package.swift` is RoomCore: `Invite` (links, pasted messages, `saracenbridge://join?invite=`), `HostStore` (one entry per host address, each with a loopback port fixed for good from 47380, so the Room page's storage, tied to its origin, survives), and `RoomRelay` (FlyingFox on 127.0.0.1:PORT, passing HTTP and WebSockets to the host's hub; `/livekit/*` to the host's call server, learned from the meeting token it rewrites). `ios/App` is the SwiftUI app (XcodeGen): Studios list, join (paste, QR via VisionKit), `RoomWebView` (WKWebView on the relay; microphone granted to the Room's origin only; downloads to the share sheet; the `saracen` bridge for Keychain items `device` and `state`), Face ID lock. `ios/roomrelay` runs the relay on a desktop for testing; `ios/ci/studio_for_tests.py` hosts, seeds and approves for the UI test. Nothing of the Studio's engine runs on the phone.
- **Shooting order (1.1.6, `engine/studio/schedreason.py`).** `optimise` searches scene orders from the first pass for the fewest shooting days, then company moves, then days actors are held (the talent scheduling problem), with an evaluator that reproduces `budget.stripboard`'s packing without building it (checked against it on random orders); it stops when a pass improves nothing or after 5 s. The AI pass (`reason`, a `schedreason` job, Deep by default) starts from the optimised board; its answer is repaired (repeats dropped, missing scenes placed, mixed day/night days split) and measured beside the other two. `budget.build(reasoned=...)` takes the AI's days for the base case, or an order packed at each case's pace. Budget allowances (1.1.6) carry status `allowance`: an amount, but outside the priced total and the bases of insurance, bond and contingency, and still counted as a line to price.
- **Reading a script scene by scene with Gemma (1.0.7, `engine/studio/sceneai.py`).** `script.scene_texts` gives every scene's number, heading, page (the number printed on the PDF page, else estimated at 56 lines a page) and text, from the same reader as the breakdown, so numbers always agree (checked on all six scripts in Tim's Library). Scenes go to the model in groups sized to the context (a share of `context` × 3.5 characters a token; a long scene is split), each labelled `[SCENE n, page p]`, and every answer is constrained to the scene numbers it was shown. The answer budget grows with the group. Four background jobs use it, all on the existing queue (`jobs.py`): `brandspot` (Brand Integration, `brandspot.py`), `elements` (Scheduling & Budgeting, `elements.py`), `bfiread` (BFI, `bfiread.py`); the term-sheet reader (`termsheet.py`) is one call, made while the user waits.
- **Jonny (1.0.7, was Ask Jon).** Renamed by Tim. The chat builds each message once and updates the answer in place: finished lines formatted (`mdLite`), the line being written as plain text, at most about 7 updates a second, no blinking caret or mouth flicker (WCAG 2.3.1 sets three flashes a second as the limit). `localStorage` `jonny-reveal` = `finished` holds an answer back until it's done (Settings › Jonny › Show answers) (S-74, S-75). `mdLite` also turns code fences (any language tag), JSON, LaTeX and markdown tables into readable lists, plain words and tables; Jonny's instructions forbid them in the first place (S-77).
- **Grounding.** Brands only from Jon's database (the answer is constrained to its IDs, and a pick from another category is dropped); brands the script names are found by text search and always registered for clearance; amounts in a term sheet must appear in the document; no source is more committed than the document's own words; BFI shares and spoken words are computed by the Studio, not the model; element lines are priced only from Jon's rate cards, otherwise Unknown (S-69 to S-73).

### Code

```
saracen-studio/
  studio_launcher.py     starts the engine on 127.0.0.1, opens the Studio window (Edge app window, then browser, as fallbacks)
  ui/                    index.html, studio.css, studio.js: plain HTML/JS, no build step; fonts/, brand/marks.js (traced crest)
  tools/catalog.json     the 12 tools, groups, "needs" lists (Jon's), what works now, what needs AI
  engine/studio/
    server.py            local API, one section per tool
    llm.py               AI engine: Ollama / OpenAI-compatible / bundled llama.cpp, optional cloud (Claude, OpenAI, Gemini); Quick and Deep; streaming
    assist.py            Ask Jon: system prompt from the catalog, the page on screen and Jon's documents; history trimming
    knowledge.py         search over Jon's documents (SQLite FTS5), built by scripts/build_knowledge.py
    keys.py              cloud API keys, DPAPI-encrypted on Windows, never returned to the page
    coverage.py          Jon's #2 coverage writer (two-pass), composite, consistency and casting checks
    report.py            Word reports built on Jon's master template
    jobs.py              background queue worker (resumes after restart)
    script.py            PDF / Final Draft / Fountain parser and breakdown
    ocr.py               scanned PDFs: PDFium pages -> Tesseract word boxes -> screenplay lines (1.0.6)
    budget.py            schedule, day-out-of-days and budget on Jon's accounts and rate cards (1.0.4)
    sales.py, xlcalc.py  territory valuation: Jon's engine workbook and the formula evaluator that runs it (1.0.5)
    sceneai.py           reading a script scene by scene with the model: groups sized to the context, answers tied to scene numbers (1.0.7)
    brandspot.py         Brand: opportunity register, ranked targets, outreach drafts, Excel (1.0.7)
    elements.py          Schedule: element tagging per scene; budget.py prices the lines it drives (1.0.7)
    bfiread.py           BFI: Section A/B script read, answer pack, Excel (1.0.7)
    termsheet.py         Finance: term sheets into proposed sources (1.0.7)
    casting.py           Casting Director: roles from the breakdown, the model's reading, shortlists from the actor database (1.1.6)
    schedreason.py       Schedule: optimised shooting order (local search, no AI), then the AI's reasoned order, checked (1.1.6)
    estimates.py         Sales: an existing sales estimate (xlsx, CSV, Word, PDF) read into the workbook's territories (1.1.6)
    store.py             settings, run folders, Library index, duplicate detection
    incentive.py         audited incentive engine
    finance.py           sources/uses, package sizing, residual debt, double-count control
    bfi.py               Cultural Test scorer
    greenlight.py        decision rules
    agreement.py         runs Jon's agreement builder in-process
    lookups.py           talent, brands, crew rates, programmes
    refdata.py, model.py reference data access; local model adapter (Proposals)
  sources/               every extracted file, deduplicated (114 files), MANIFEST.json with SHA-256 (all verified)
  data/studio_reference.db  41 tables (38 data, 9,839 rows), provenance per row
  packaging/             PyInstaller spec, Inno Setup script, Windows build script, smoke.py; shell/ (Tauri 2 window); ocr/ (Tesseract, not in the source zip: `fetch_ocr.sh` makes it from Mannheim's signed installer, checked by SHA-256)
  docs/                  ARCHITECTURE.md, DESIGN.md
  tests/                 155 tests (1.0.7)
```

### Test results (offline, 12 Oct 2026)

| Suite | What it proves | Result |
|---|---|---|
| Jon's audit regressions R01–R12 | Engine gives his audited workbook's answers (Spain €1.55m, UK IFTC £3.18m / £2.385m net, caps, elections, unknown → PRELIMINARY) | Pass |
| SHADE workbook | Residual debt €3,168,657.42 to the cent; catches the double count in Jon's v2 and the GPT's v3 | Pass |
| Agreement Builder | Jon's own 33 checks | 33/33 |
| Tools API | Every tool end to end: intake of all three formats, duplicates skipped, no overwrite on same title, Library search and rebuild, coverage matrix, incentives, BFI pass/borderline/golden rule, finance, greenlight, term sheet, lookups, linked apps, AI status | Pass |
| Packaged app (`packaging/smoke.py`, 26 checks) | The frozen build carries everything: UI, catalog, database, engine figures, script intake, Library, Jon's term-sheet workflow, his coverage spec, a full Word report render, the actor database, AI status, Look Book page rendering, the name finder | Pass (1.0.2 Windows build under Wine, fresh install, 13 Oct; 23 checks) |
| Real model, end to end | Gemma 4 E2B through the bundled engine, in both the source and the packaged app: two-pass read, all five schemas, queue, result saved. Writing quality at E2B is not client-grade (S-19) | Pass (CPU, 1-page fixture) |

## 3. Reference data loaded

| Area | Tables | Rows | Source |
|---|---|---|---|
| Incentives | programme rules, programme database, FX, coverage gaps, sources/audit, regressions | ~336 | Audited v1.1 (26 Aug 2026) |
| Rates | 13 jurisdictions: crew 3,944, cast 182, supplemental 361, non-labour 778, regional factors 196, labour rules 124, sources 228 | ~5,800 | Rate DB v1.2 (13 Sep 2026) |
| Budget structure | chart of accounts 280, Filmustage category/account/field/validation maps | ~595 | CoA v1.0, Filmustage spec v1.0 |
| Talent | actors 1,004, directors 500 (+ scorecard, fees, weights), tier assumptions | ~2,540 | Actor DB v2.2, Director DB v4.3 |
| Sales | control panel, territory baselines/overlays, proxy assumptions, FX, data dictionary, lists, attachment certainty | ~250 | Sales Engine v4.1 |
| Brands | 110 brand accounts, 110 evidence rows, HubSpot map | 248 | Brand DB |
| BFI | 17 Cultural Test criteria | 17 | BFI pack (checked 12 Jul 2026) |
| Vocabularies | 12 controlled lists (status, gates, RAG, CP states, workstreams…) | — | 02 Protocol, SKILL files |

**Deliberately not loaded:** the Brand DB *Contacts* sheet (named individuals; lawful basis unconfirmed, G-17).

## 4. How a tool runs

```
user drops files ──► model task (reads) ──► Proposal ──► user confirms ──► engine (calculates, gates)
                                                                          │
                                         change control marks stale ◄─────┤
                                                                          ▼
                                                         renderer (.docx/.xlsx/PDF, branded)
```

1. **Intake.** Files go into the project's local folder (the data room for #8/#9).
2. **Read.** Model tasks extract structured facts against a JSON schema (scene index, term-sheet terms, contract CPs). Each fact keeps its source page or clause.
3. **Confirm.** The UI shows proposals beside their source. Confirmed facts become engine inputs; unconfirmed facts stay *Proposed* and keep results PRELIMINARY.
4. **Calculate.** The engine runs Jon's rules. Unknown stays unknown and is never zero.
5. **Render.** The report is built from the master template. Every figure is an engine value, and the narrative may only reference them (T-SHADE-05).
6. **Change control.** Any change to budget, schedule, route, FX or lender terms marks downstream outputs stale until they are re-run.

## 5. Stack

- **Engine:** Python 3.13+, pure functions, pytest.
- **Shell:** `studio_launcher.py` runs the engine as a local server bound to 127.0.0.1. From 0.4 on Windows it opens the Studio window (Tauri 2, above), and falls back to the 0.3.4 route if that window cannot show the page. The 0.3.4 route shows the app in its own Microsoft Edge app window (`msedge --app=`, no tabs or address bar); Edge is on every Windows 10/11 PC. If no window shows the page within 25 s it tries the default browser, then a message box gives the address. The embedded WebView2 window (pywebview over .NET) is opt-in with `--native`; macOS and Linux use it by default. Every start writes `studio.log` in the data folder before anything else loads; other start-up failures show a message box. The app stops itself 150 s after its window closes. Calls to 127.0.0.1 bypass any system proxy. A first-run hook (`packaging/rth_no_wmi.py`) stops Python querying WMI, which hung every start on Tim's PC on 13 Oct (see S-31); setuptools is no longer bundled. Tauri was set aside on 12 Oct and added on 13 Oct at Tim's request as a thin window only (no sidecar, no native commands): the engine and every fallback stay in Python.
- **Packaging:** PyInstaller app folder (onedir: fewer antivirus false positives than onefile) wrapped by Inno Setup into one per-user `SaracenBridgeStudio-Setup-<version>.exe` (0.3.5: 28.0 MB); no admin rights, and nothing is downloaded at install unless Gemma is chosen. Upgrades replace the program folder; user data in `%APPDATA%\SaracenStudio` is never touched. Jon's agreement-builder scripts ship as data, so their imports (lxml and stdlib) are declared in the spec.
- **Build:** three routes to the same `SaracenBridgeStudio-Setup-<version>.exe`: `packaging/build_windows.ps1` on any Windows PC; the GitHub Actions workflow; or `packaging/build_windows_on_linux.sh`, which runs Windows Python, PyInstaller and Inno Setup under Wine 11 on Linux. 0.3.0 to 0.3.5 were built by the Linux route on 12–13 Oct. For 0.3.5: 71/71 tests under Windows Python, 16/16 smoke checks on the installed program, clean install and uninstall. Port 8799 is never used (A.I.D.E.N. on DADS_BEAST).
- **Brand:** 0.4 uses the 3D crest (Jon's traced shapes in gold on a richer purple plate) for the .exe and window icon, installer panels and the rail; Jon's original logo files are unchanged. The software is purple, gold and black (Tim, 13 Oct): gold for actions and selection, purple for atmosphere and the AI. Reports keep Jon's master template. See `docs/DESIGN.md`.
- **AI engine (decided 12 Oct: local, Gemma for now, Ada later).** `studio.llm` is a single client for Ollama, any OpenAI-compatible server (llama.cpp, LM Studio, vLLM, later Ada) and an optional built-in model. A fresh install uses **Automatic** mode: Gemma in Ollama on the machine first (F.R.A.T.'s engine on the 3090, if it runs under Ollama), then the bundled model, then none. Port 8799 is never used.
- **Reasoning switch.** **Quick** (thinking off, the default) and **Deep** (thinking on, with extra token budget) are chosen per job. Each mode may name its own model, for example Gemma 4 for Quick and a heavier model for Deep. Gemma 4 thinks by default; left on, it spent a whole budget thinking and returned nothing (S-14).
- **Gemma in the installer (0.3.1).** Setup.exe (28.0 MB) has an "AI engine for written coverage" page: **Install Gemma 4 12B** (7.0 GB, preselected on PCs with 15 GB+ memory), **Install Gemma 4 E4B** (5.2 GB, preselected below that), or **Skip**. On upgrades it offers "Keep the Gemma already installed". Nothing is downloaded on Skip. If a model is chosen, the installer downloads two things, each checked against a SHA-256 fixed in the installer: the llama.cpp server (release b11577, Vulkan build, 32 MB zip from llama.cpp's GitHub release, unpacked to `<install folder>\llm`) and the model, from Google's official Hugging Face repository, to `<install folder>\llm\models`. The server was first packed inside Setup.exe, which made it 41.8 MB, over the 30 MB limit for sending a file here, so it moved to download (S-25). Upgrades keep it; uninstall removes it. Silent installs: `/GEMMA=12b|e4b|skip` (default skip). Tested under Wine on a fresh profile: the installer downloaded the engine and the real E4B, both passed their hash checks, and the installed program loaded the model and answered. If the engine stops part-way through a job (seen once in testing: killed for lack of memory), the job fails with a plain explanation and Retry restarts the engine (S-26). A hard kill of the Studio also stopped the engine (Windows job object).
- **Gemma downloaded by the Studio (1.0.2).** On Jon's PC the installer's own downloader stalled on the 6.1 GB E4B and Windows gave up ("Error reading data: (12002) The operation timed out"); its "Try again" restarts a file from zero. The installer no longer downloads anything: the Gemma page records the choice in `<install folder>\llm\wanted.json`, and the Studio (`engine/studio/fetch.py`) fetches the engine zip, the model and its vision add-on in the background with HTTP Range requests into `<name>.part`. A dropped or stalled connection (60 s without a byte) is retried with back-off up to a minute, for about 40 attempts without progress; a closed Studio or a restart carries on from the last byte; each file is checked against its SHA-256 (a damaged file is fetched once more, never used); the zip is unpacked beside the models. If the install folder is read-only it uses `%APPDATA%\SaracenStudio\llm`, which the engine search now includes. Settings › Gemma on this PC shows progress, speed and time left with Pause/Resume, or Download buttons with a recommendation from the PC's memory; the sidebar shows the percentage; writing tools switch on when it finishes, without a restart. "Skip for now" on a reinstall withdraws an unfinished request. Checked: the real Hugging Face source answers Range requests through its CDN redirect (206, sizes as the manifest); tests with a server that drops the connection half way, sends a damaged file, or leaves a partial file; on Windows (Wine), a fresh silent install with `/GEMMA=e4b` wrote `wanted.json`, the installed Studio fetched, checked and unpacked all three files from a throttled test source and reported the built-in engine connected with vision; pause, resume and a source that vanished mid-file and came back were checked by hand. Register S-58.
- **Not bundled:** Ollama; the model and its server (optional download, above); OCR; LibreOffice (only needed for workbook recalculation and PDF rendering, which are not built yet).

## 6. Build order from here

1. **Coverage writer (built 12 Oct).** Jon's SKILL.md is used verbatim as the instructions. The model reads the script in scene-aligned parts and takes structured notes, then writes the 11 sections in four schema-constrained calls with the verified breakdown facts. The composite is computed in code with Jon's weights. Verdict and readiness stay proposals, since G-01/G-02 are open. The report is built on Jon's master template by cloning its own panels and tables. Jobs queue in `library.db`, run one at a time and resume after a restart. Next: benchmark models on real scripts (throughput on the 3090 is unmeasured).
2. Scanned-PDF OCR, so every script in a folder can be read.
3. Schedule & Budget on the script index plus the rate and chart-of-accounts tables.
4. Sales Estimates: port the v4.1 engine; Barefoot Boys is the calibration test.
5. Finance Plan: debt schedule, cashflow, waterfall, sensitivity, 13-tab workbook.
6. Look Book, Brand opportunities, BFI script reading (all model tasks).
7. Greenlight data-room audit once the 243-check matrix arrives.

## 7. Blocked on Jon

See the issues register §D. The questions that change the engine are: G-27/G-36 (capital-structure policy), G-28/G-14 (advance rate on unsold territories, and the double discount on proxy territories), G-34 (closing matrix), G-21 (GMOT workbook), G-01/02/19/35 (score → verdict rules). Answered from Jon's files on 13 Oct, or now only a yes/no: G-03, G-08, G-12, G-13, G-15, G-20, G-25, G-29, G-38, G-41.
