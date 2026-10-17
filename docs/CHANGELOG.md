# Saracen Bridge Studio: revisions

Every change to the Studio gets an entry here, newest first, in the release that carries it. Each line points to its row in the issues register (`CIPHER_SARACEN_BRIDGE_ISSUES_REGISTER`, S-numbers), where the evidence and the test are. Installers are identified by their SHA-256; only the first 8 characters are shown.

Revisions before 0.3.1 are recorded only in the register (S-01 to S-23).

## 1.1.0 (17 Oct 2026), whoever starts a production hosts it
Setup `SETUPHASH`, SETUPSIZE. Replaces 1.0.8 the same day. Tested by a silent upgrade over 1.0.7 and the smoke on the installed app, including starting a production in the installed app (its Room and meetings server running under Windows), and a Studio joined to two hosts' productions. Not yet run on Tim's PC.
- Changed: no web address or founder code. **Start a production** runs the Room on this PC: the person who starts a production is its host and its executive, sends the invites, approves each device and sets everyone's access. Invite links carry the host PC's network address. (S-88)
- Added: a Studio can be in several hosts' productions at once (Jon's on Jon's PC, Colin's on Colin's): they appear together in one switcher, marked "on this PC" where they're hosted here, and every message, file, call sheet and meeting goes to the PC that holds that production. **Join with an invite** is in the switcher too. (S-88)
- Added: the Studio carries the Room's server, its phone app and the meetings server (LiveKit 1.13.10, Apache-2.0), started with the Studio on a PC that hosts. (S-88, S-90)
- Fixed: the production switcher's menu was cut off by the top bar, so it never showed. (S-89)

## 1.0.8 (17 Oct 2026), the Room
Setup `4fd0a424`, 68.3 MB. Delivered to Tim's Downloads; superseded by 1.1.0 before use. Tested by a silent upgrade over 1.0.7 and the 35-check smoke on the installed app (Room crypto bundled, Room pages, mic panel, a test Room server's health). 198 tests pass under Windows Python (3 skipped: Node and POSIX-only), 203 under Linux.
- Added: the Room, a private team space per production, end-to-end encrypted on each device before anything leaves it: a board of notes (Open, Needs review, Decision, Done; pinned; with files), channels and private messages with @mentions, files with versions and resumable uploads, a production switcher, and Members & access (invites, device approval by three safety words, tiers, contact grants, the executive oversight notice and an append-only audit log). Hidden, not locked: people see only what their tier and spaces allow, in lists, search, counts and notifications as well. (S-79, S-80, S-84)
- Added: call sheets in the Room: a strip with "X / Y confirmed", Remind the ones who haven't, each person's own times (pickup address and driver only to them and the production office), Got it per version, and a new version starts the count again. (S-81)
- Added: voice huddles (anyone in a space) and meetings of up to 75 (executives on stage, others watch and raise a hand, executives bring them up), end-to-end encrypted, never recorded, with calendar invites; the system's default microphone is used and followed when it changes, with noise suppression and echo cancelling and a level meter. (S-82)
- Added: the phone app (Today / My day, Board, Chat, Meet), installed from the invite link, with notifications that carry no content. (S-83)
- Fixed during the build: the Room server didn't stop while phones or Studios were connected (S-85); a sign-in race between the live link and a page request (S-86).

## 1.0.7 (15 Oct 2026), the AI features on Gemma
Setup `9c0a5f69`, 61.8 MB. Two earlier 1.0.7 builds (`3bb8565f`, `70c3d288`) were tested here and never delivered. Delivered to Tim's Downloads. Tested by a silent upgrade over 1.0.6 and the 30-check smoke on the installed app; each AI feature run end to end on Gemma 4 E2B in the build workspace (CPU), and all four run through the installed Windows app against Gemma (term sheet, element tagging, brand spotting and the BFI read, with their workbooks). Not yet run on Tim's PC.
- Added: Brand Integration reads a script scene by scene for brand opportunities, as Jon's brief sets out: an ID per opportunity, scene and page, the moment and exact item, category, placement type, whether the script already has it or would need changing, why it fits, risks, feasibility, commercial value and outreach priority, with a primary target and two alternatives from Jon's brand database and a no-brand fallback. Brands the script already names are listed for clearance. Targets are ranked and grouped, and outreach is drafted for the top five (subject, email, follow-up, LinkedIn, call brief), never sent and with no invented contacts. Downloads as an Excel register. (S-69, S-70)
- Added: Scheduling & Budgeting tags each scene's production elements (stunts, stunt performers, picture vehicles, weapons, animals, practical and visual effects, background, special make-up, child performers, intimacy, water, special equipment). Building the budget then adds the lines they drive, on the days they work in each case: priced from Jon's rate card where it has the role or item, otherwise Unknown to quote. Background and VFX shots use the tagging unless the producer enters figures. The workbook gets an Elements sheet. (S-69, S-71)
- Added: BFI Certification reads a script for the Cultural Test's Section A and B: setting by script length (A1), the three leads and what the script shows of their nationality (A2), the subject (A3), dialogue by spoken words counted from the script (A4) and a specific case for B, with proposed and conservative points and Jon's answer pack (Excel), never marked ready. One click puts the points into the scorer. (S-69, S-72)
- Added: Finance Plan reads a term sheet (PDF, Word or text): each instrument's party, type, amount, currency, how binding it is and its terms. Amounts are checked against the document, no source is shown as more committed than the document's words, and each line is reviewed before it goes into the plan. (S-69, S-73)
- Changed: the assistant is now called Jonny (Tim): Ask Jonny, "I'm Jonny", and the tips and Settings. It's still named after Jon and still never speaks for him. (S-74)
- Fixed: Jonny's answers flashed while they were being written: the whole conversation was rebuilt 25 times a second, so every message replayed its fade-in, a caret blinked, his mouth flicked open and shut about four times a second, and half-written formatting appeared and vanished. A photosensitivity risk and hard to read. Now finished lines appear formatted and stay put, the line being written is plain text, nothing blinks, and Settings › Jonny › Show answers can hold an answer back until it's finished. (S-75)
- Fixed: Jonny's answers could show raw code: a formula or data fenced in ``` (often marked "json"), LaTeX, or a table came through as symbols (Tim saw it in an incentives answer). Jonny is now told to write formulas in words and never use code, JSON, tables or LaTeX, and anything that still comes through is shown readably: data as a list, formulas as plain words, tables as tables, never the markers. (S-77)
- Fixed: the first 1.0.7 build left out Jon's instructions for brand spotting, the BFI read and term sheets, so those failed in the installed app (found by running the installed app against Gemma: term sheets returned a server error). They're installed now, and the smoke test checks they load. (S-76)
- Added: Sales Estimates builds a package of several actors and directors. Choosing an attachment status on a profile (Signed agreement, Letter of intent and so on, plus Pay-or-play) attaches the name; the package shows above the finders with each name's status and weight, and you can look up the next one straight away. Value this package takes it to the Territory valuation with everyone and their status filled in. (S-78)
- Fixed: the budget workbook (since 1.0.4) left a blank row under each sheet's headings. (S-71)
- Fixed: entering 0 background artists left the line Unknown; it is now priced as none. (S-71)

## 1.0.6 (15 Oct 2026), scanned scripts read by OCR
Setup `dfebcf30`, 61.7 MB (1.0.5 was 36.6 MB; the OCR engine adds 25 MB). Delivered to Tim's Downloads. Tested by a silent upgrade over 1.0.5 and the 27-check smoke on the installed app. Installed on Tim's PC on 15 Oct at 12:05 (his Studio log), where Jonny ran on Gemma 4 12B. A first 1.0.6 build (`7077301e`, 85.0 MB) carried the OCR engine's DLLs twice; it was replaced in Downloads within the half hour, before use, and the build now stops if that happens again. (S-67)
- Added: a scanned (image-only) PDF script is read by OCR on the same PC, with nothing sent anywhere: scenes, speaking roles, locations, schedule, budget and coverage now work for it. The Studio bundles Tesseract 5.3.0 (Universität Mannheim's signed Windows build, Apache-2.0, English). Such a script is marked "PDF (scanned, read by OCR)" with a note to check names and headings against the script. (S-12, S-67)
- Added: while a scanned script is being read, the intake line says which page it is on ("reading page 23 of 104 by OCR"). Each scanned file is read once and remembered. (S-67)
- Fixed: script intake ran on the Studio's main loop, so a long read would have held up every other screen until it finished; it now runs alongside. (S-67)
- Fixed: in a PDF, a line starting with a full stop was taken as a scene heading (Fountain's forced-heading mark). On Tim's PC this changed one of the 11 documents in his Library: ASSASSINATION, which has no INT./EXT. headings, read as 2 scenes and 5 speaking roles; it now reads 0 and is flagged as a possible treatment. The other 10 read identically. (S-68)
- Checked: an 18-page scan made noisy and slightly skewed read exactly like its typed original (60 of 60 scene headings, 6 of 6 speaking roles, 10 locations), in the installed Windows app as on Linux. (S-67)

## 1.0.5 (15 Oct 2026), territory sales valuation
Setup `b58cf0ff`, 36.6 MB. Delivered to Tim's Downloads. Tested by a silent upgrade over 1.0.4 and the 26-check smoke on the installed app; not yet installed on a real PC.
- Added: Sales Estimates has a Territory valuation tab running Jon's Sales Valuation Engine v4.1 exactly as his workbook calculates: Ask, Expected Close and Take for 33 territories, gross and net producer receipts, the lender collateral test, and his controls. (S-66)
- Added: inputs for his engine: the 27 intake fields, cast and director from his databases with attachment status, rights and existing sales by territory, comparable films, verified deals, public buyer-economics proxies, a documented worldwide anchor, and confirmed finance. A script in the Library can prefill the title and budget. (S-66)
- Added: each valuation is saved in the Library and downloads as his workbook with the inputs filled in, so the same numbers recalculate in Excel. (S-66)
- Fixed: Jon's engine ships with GBP as a 1:1 rate although it reports in USD; the Studio uses USD rates from his ECB table (25 Aug 2026) and lets the user enter others. (S-65)
- Checked: the Studio's evaluator reproduces all 21,759 formulas in his workbook: blank, against the values Excel saved; filled with a test project, against LibreOffice. (S-66)

## 1.0.4 (15 Oct 2026), schedule and budget
Setup `4a31126c`, 36.3 MB. Delivered to Tim's Downloads. Tested by a silent upgrade over 1.0.3 and the 25-check smoke on the installed app; not yet installed on a real PC.
- Added: Scheduling & Budgeting has a Schedule & budget tab. From a script in the Library it gives shooting days in lean, base and conservative cases (5 / 4 / 3 pages a day), a stripboard (day scenes then night scenes, grouped by site, day and night never in one day), and day-out-of-days for every speaking role. (S-64)
- Added: a budget on Jon's chart of accounts (SB-COA-1.0) priced from his 2026 rate cards for all 13 jurisdictions, with the region's cost factors: crew by role for prep, shoot and wrap, equipment, facilities, transport, locations, catering, office, post, insurance and bond at the card's rates, and 10% contingency. Fees, negotiated crew and anything the card doesn't list stay Unknown, never zero, and can be priced on screen. (S-64)
- Added: the budget is saved with the script in the Library, shown on its Library page, and downloads as an Excel workbook (top sheet, detail in all three cases, stripboard, day-out-of-days, assumptions and sources). (S-64)
- Checked: on Tim's five feature scripts the base case gives 20 to 34 shooting days for 75 to 129 pages; each script is flagged location-heavy (44 to 99 sites). (S-64)

## 1.0.3 (15 Oct 2026), audit for "running flawlessly"
Setup `677ba5fe`, 35.7 MB. Delivered to Tim's Downloads; not yet installed on a real PC.
- Fixed: the script reader missed scene headings written with a colon ("INT: KITCHEN – DAY"). Tim's "Ultimate Feature" read as 12 scenes of 162 and was titled with its first heading; WEREWOLF missed one scene (133 → 134). Reader version 3; on first start the Library re-reads older scripts and marks coverage written from the old reading "Write again". (S-59)
- Fixed: a title taken from the file name drops draft notes and dates ("Ultimate Feature - FINAL Sept 2026" → "Ultimate Feature"); look books use the same rule. (S-59)
- Fixed: saved Finance, Incentives, BFI, Greenlight and Term Sheet runs opened in the Library as raw data. They now show the tool's result, what was entered, and a link back. (S-60)
- Fixed: Term Sheet Builder showed a raw validation report and a dead temporary path for the wrong workbook, and "Term sheet built" for a blank one. (S-61)
- Fixed: an unknown incentive programme gave a server error; Calculate, Score and Decide showed nothing when a request failed; Finance sent a gross budget of 0 when the field was empty. (S-62)
- Checked and fine: a browser sweep of every page, tab and saved run at six window sizes plus 11 actions; the fontTools log line has no effect on Tim's PDFs. (S-63)

## 1.0.2 (13 Oct 2026)
Setup `9f8dfe75`.
- Fixed: the installer's own Gemma download timed out on Jon's PC (Windows error 12002) and restarted from zero. The installer now only records the choice; the Studio downloads the engine and model in the background, resumes after any drop, checks each file's SHA-256, and shows progress in Settings and the sidebar. (S-58)

## 1.0.1 (13 Oct 2026)
Setup `9aeb8387`.
- Changed: "Private" appeared twice in the sidebar footer; now a lamp that is green on Local and red on Cloud. (S-53)
- Changed: the home page and Settings no longer claim nothing needs the internet; they state the choice between private and cloud compute and its risk. (S-54)
- Changed: Visual Feedback says Coming soon; "Core ready" became "Ready · more coming"; "Not built yet" became "Coming soon". (S-55)
- Added: clear one failed job, or all of them, from the queue. (S-56)
- Added: Brand shortlist: click brands to pick several, download as CSV; a script read in Brand Integration takes the shortlist as its brand targets. (S-57)

## 0.4.7 (13 Oct 2026)
Setup `e0c38f14`. The version on Tim's PC at the 15 Oct audit.
- Changed: a gold gradient on every selected control, only while selected. (S-50)
- Changed: tool pages open on their title, without the category label. (S-51)
- Changed: type and layout scale-locked against stretched monitors (Auto, or a pinned size in Settings); Source Serif 4 replaces Instrument Serif. (S-52)

## 0.4.6 (13 Oct 2026)
- Fixed: Crew rates and other wide tables couldn't be scrolled sideways; they now fit at 1280 px and up. (S-49)

## 0.4.5 (13 Oct 2026)
- Fixed: Tim's WEREWOLF draft read as 1 scene of 133, titled "Written and Created b y" (scene numbers glued to headings; credits taken as the title). Older readings are re-read when opened. (S-48)

## 0.4.4 (13 Oct 2026)
- Fixed: Ask Jon gave wrong facts about the tools; retried jobs left their failures on the queue. (S-47)

## 0.4.3 (13 Oct 2026)
- Fixed: the screen named the model; Ask Jon cited other tools' documents. (S-46)
- Shipped 0.4.2's fixes. (S-39 to S-45)

## 0.4.2 (13 Oct 2026, superseded by 0.4.3 before use)
- Fixed: Sales name search needed a button; type-ahead and profiles added. (S-39, S-40)
- Fixed: BFI and Finance tables overflowed their cards. (S-41)
- Fixed: UI faults from a page-by-page pass. (S-42)
- Fixed: "Context size has been exceeded" when Ask Jon ran beside a Deep coverage job (two engine slots, a thinking budget). (S-44)
- Fixed: failed jobs showed raw engine text; letter-spaced and doubled titles. (S-45)

## 0.4.1 (13 Oct 2026)
- Fixed: Ask Saracen wrote tool links as full local addresses. (S-37)
- Added: Jon, the helper character, answering from Saracen Bridge's own documents. (S-38)

## 0.4.0 (13 Oct 2026)
- Added: the new design, the Studio window, the 3D crest, Ask Saracen on Gemma, optional cloud AI. (S-33 to S-36)

## 0.3.5 (13 Oct 2026)
- Fixed: Tim's 100-page Final Draft PDF read as 0 scenes (scene numbers at both margins). (S-32)

## 0.3.4 (13 Oct 2026)
- Fixed: the Studio hung at start on Tim's PC (Windows WMI service stuck); opens in an Edge app window. (S-31)

## 0.3.3 (13 Oct 2026)
- Mitigated: the window never appeared on Tim's PC; falls back to the browser after 20 s and logs why. (S-29)
- Fixed: calls to this machine could go through a system proxy. (S-30)

## 0.3.2 (12 Oct 2026)
- Changed: no blue left; gold with black text. (S-27)
- Fixed: narrow windows scrolled sideways. (S-28)

## 0.3.1 (12 Oct 2026)
- Changed: the llama.cpp engine downloads with the model instead of sitting inside Setup.exe. (S-25)
