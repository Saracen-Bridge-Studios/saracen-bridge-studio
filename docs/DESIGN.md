# Saracen Bridge Studio: Design ("The Screening Room", 0.4)

**Version:** 1.0.1, 13 October 2026
**Brief (Tim, 13 Oct):** "a really high end look … very very clean, really nice pop-ups, slick colours, using the purple, gold and black … like a million-dollar piece of software", with 3D depth, a 3D logo, a Tauri window, an in-app assistant on Gemma and an optional cloud AI.

## 1. The idea

A private screening room at night. The walls are aubergine-black, the crest's purple tints the room, and gold light falls only on what matters: the primary action, the selected tool, figures that decide something. Ivory is for reading. Dark by design: the brand is dark.

| Role | Colour | Used for |
|---|---|---|
| Room (ink 0–5) | #07050b → #2d203e, purple-tinted blacks, lighter = higher | Backgrounds and raised surfaces (elevation by lightness, not shadow) |
| Purple (plum) | #241240 → #e6d4ff, crest #3f1f70 / #6b3fb4 | Atmosphere, the AI, the assistant, cloud state |
| Gold | #6c4b0f → #fff0c4, centre #dba534; metal gradient #fff3c8 → #f8d56f → #e3ad3a → #b8821f | Primary actions, selection, key figures, the crest |
| Ivory | #f1ebe0 and three greys | Text |
| States | green #82caa0, amber #e3946a, red #e88686 (desaturated) | Ready / preliminary / fail, never competing with gold |

Tim asked on 13 Oct for "richer purples and sharper gold colours": the purple moved from the crest's dusty #382843 to a royal aubergine, and the gold gained brighter highlights and a steeper metal gradient.

Type: **Source Serif 4** for display (titles, figures, the hero), **Geist** for interface text, **Geist Mono** for labels, codes and numbers in tables. All three are bundled (SIL OFL) in `ui/fonts`; nothing loads from the internet. Tim asked on 13 Oct for a serif "like this but not as compressed … slightly wider": Instrument Serif (0.4.6 and earlier) was replaced by Source Serif 4, about 20% wider at the same size, with true italics, lining figures and an optical-size axis that the browser follows automatically (display cuts at title sizes, sturdier cuts small). Candidates set side by side: Newsreader (133%, too wide), Libre Caslon Display (111%, no italic), Cormorant (116%, old-style figures), Playfair, Bodoni Moda, Gilda, Fraunces, DM Serif Display.

**Scale lock (0.4.7).** Text and layout scale as one: a single uniform zoom on the page (`--uiz`), never a per-axis stretch, so letters keep their shape on any screen. Auto follows the window's shorter side against the 1440 × 900 design size, damped by half and held between 90% and 120%; Settings › Display can pin 90/100/110/125%. Viewport units in the CSS divide by `--uiz`, so a zoomed page still fits the window exactly. Browser text inflation is off, faked bold is off (`font-synthesis: style`), widths are fixed at normal, kerning is on. A monitor driven at a non-native, stretched resolution distorts every program; the app can't undo that, so Settings › Display says how to set Windows back to its recommended resolution.

## 2. Components

- **Frame.** The rail sits on the bare room; the content is an inset sheet with rounded corners and a gold hairline across its top edge, so it reads as an application, not a web page. A sticky blurred top bar holds breadcrumbs, search, **Ask Saracen** and three shortcuts.
- **Home marquee.** A cinematic banner: slow-drifting purple and gold light (three radial layers moving by `transform` only), a vignette, film grain, the serif headline, the gold **Read a script** button, and a ledger of three facts (tools working, Library size, AI state).
- **The Suite.** One grid of all twelve tools with filter chips by group. Cards have a gradient hairline border, a spotlight that follows the pointer, a faint serif tool number as a watermark, and a gentle 3D tilt (max 9°/7°) with the icon and title raised on `translateZ`.
- **The 3D crest.** Jon's crest and wordmark traced to vectors (potrace) from his own artwork: the crest from the 3000 px Analytics logo, the wordmark from the purple Studio logo. Rendered in SVG as layers: a soft gold glow, an extruded side (stacked offset copies in dark gold under a drop shadow), a polished face (banded metal gradient through a specular-lighting bevel filter) and a light sweep. CSS 3D stacks the plate, crest and wordmark at different depths; it sits straight on and tilts only under the pointer. Used in the rail, the start-up intro, the app icon and the installer panels.
- **Pressable gold button.** Josh Comeau's three-layer principle: a thicker gold edge below, a front that rises on hover with a slight overshoot and presses down in 34 ms, a light sweep across the face on hover.
- **Selected = gold (0.4.7).** Tim: "when a tab is selected … a gold gradient similar to how Google Chrome does gradients, only when selected", pushed to every part of the app. Every "you are here / this one is on" control carries the same luminous gradient (`--gold-tab`: a soft light at the top left over a champagne-to-deep-gold sweep), dark ink text, a fine bevel, a warm glow beneath, and one sheen across the face when it becomes selected: tool tabs, the Quick/Deep switch, the cloud provider picker, the sidebar's current page, the suite filter chips, Local compute and Cloud, the interface-size picker and Jon's **Reads this page** toggle. Unselected controls stay quiet. Lists moved through with the keyboard (the palette, the name finder) keep their soft highlight.
- **Privacy lamp (1.0.1).** In the sidebar footer, "Private · offline" has a small lamp: green and breathing on Local compute; red, with the words gone dark, while Cloud is on. "Private" appears once.
- **Shortlist (1.0.1).** Brand rows are picked by clicking: a gold tick, a gold bar on the left and a soft gold wash; the picks gather above the table as gold chips, each with its own remove.
- **Page head (0.4.7).** A page opens straight on its title. The category (Development, Sales & Marketing…) is already in the breadcrumb, so no label repeats it above the title (Tim, 13 Oct); the Library and Settings labels went the same way, and a saved run shows its date under the title instead.
- **Toasts** (bottom right, at most four, pause on hover, a countdown hairline), **modals** (scale .96 → 1 with opacity, Esc and the scrim close them), and the **command palette** (Ctrl/Cmd+K or /: tools, places, actions and your recent work; keyboard first; no animation, because it is keyboard-triggered).
- **Ask Saracen.** A glass drawer from the right (a bottom sheet on phones): engine line (Gemma on this PC, or a purple **Cloud** tag), page-aware suggestions, streamed answers with a gold caret, in-app links rendered as gold chips, a Stop button, and a **Reads this page** toggle.

- **Jon (0.4.1).** Tim's idea: a helper character like Microsoft's paperclip. Jon is an original cartoon clapperboard (concept A of three; B "Director" and C "Crest" were offered). He sits bottom right, blinks, watches the pointer, snaps his clapper as he talks, looks up while thinking, frowns at errors and hops at successes. Clicking him opens **Ask Jon** (the assistant, renamed from Ask Saracen). He offers help when someone looks stuck: the first visit to a tool (a walkthrough), a long pause on a tool with fields to fill, an error, a preliminary or failing result appearing, or the same button pressed three times. Clippy's lessons are rules here: he offers and never insists; at most one tip per page and five per session; never while a field is being typed in; "Not now" snoozes that kind of tip; three ignored tips in a row and he stays quiet for the session; "Turn off tips" (or Settings) silences him for good. He answers from **Saracen Bridge's own documents**: 51 of Jon's GPT instructions, references and shared standards (Markdown and Word) are indexed locally (SQLite FTS5, BM25, 1,022 sections, `data/knowledge.db`); the best five sections go in front of the model and are listed under each answer.

## 3. Motion rules

Ease-out `cubic-bezier(.23, 1, .32, 1)`; most transitions under 300 ms; entrances from `scale(.95–.96)` plus opacity; presses at `scale(.97)`; hover effects only behind `@media (hover: hover)`; no animation on keyboard-triggered UI; blur kept under ~20 px on large areas and never animated; `prefers-reduced-motion` switches off drift, float, sweep, tilt and the intro.

## 4. Research (Rule 1)

**Round 1 (12–13 Oct), premium dark interfaces.** Findings used: avoid pure black, elevate by lightness, desaturate accents; ease-out under 300 ms, nothing animated for keyboard-triggered UI, scale-from-.95 entrances, .97 press; command palettes with a large input, groups and keyboard navigation; toast offsets of 32/16 px; `backdrop-filter` limits (blur under ~20 px on large areas, three or four layers at most, never animate the blur); Tauri `decorations: false` breaks Windows 11 Snap Layouts, so a native title bar is kept. The URLs of round 1 were not kept when the session's context was compacted.

**Round 2 (13 Oct), 3D and depth, after Tim asked:**
- [Josh Comeau: 3D button](https://www.joshwcomeau.com/animation/3d-button/): the layered pushable button and its timings.
- [Ryan Mulligan: CSS @property and the new style](https://ryanmulligan.dev/blog/css-property-new-style/): registered properties to animate angles (used for the Ask button's rotating border and the crest's float).
- [Aave: Building glass for the web](https://aave.com/design/building-glass-for-the-web): specular highlights and rim light on glass; noted, not copied (SVG displacement was more than this app needs).
- [Kitemetric: hover tilt with CSS](https://kitemetric.com/blogs/create-a-stunning-hover-tilt-effect-with-pure-css): perspective 1000 px, ~10° rotations, `translateZ` layering. The Studio uses smaller angles so text stays readable.
- [Digital Strategy Force on 2026 Awwwards trends](https://digitalstrategyforce.com/journal/why-are-immersive-experiences-dominating-the-2026-awwwards/): WebGL and depth dominate award sites. A vendor's article with unverified figures; its performance cautions (60 fps on mid-range hardware, a plain fallback) are what was taken.
- [Paper Shaders mesh gradient (21st.dev)](https://21st.dev/@paper-design/components/mesh-gradient-purple.md): considered for the marquee. Not used: CSS gradient layers moving by transform give the same feel without a WebGL context.

**Window (Tauri), 13 Oct:** [Digital Applied, 2026 comparison](https://www.digitalapplied.com/blog/desktop-apps-web-stack-tauri-electron-deno-wails-2026) (Tauri 2: 3–15 MB, 20–100 MB RAM, WebView2 on Windows; Electron 50–150 MB+, 100–300 MB RAM), [Tauri runtime releases](https://tauri.app/release/tauri-runtime/all-versions/) (2.12.1, 30 Sep 2026).

**Cloud AI, 13 Oct:** [Claude streaming events](https://platform.claude.com/docs/en/build-with-claude/streaming), [Gemini OpenAI compatibility](https://ai.google.dev/api/compatibility), [OpenAI model list (endoflife.date)](https://endoflife.date/openai-api-models). Model names change often, so Settings lists the models on the user's own account.

**Jon, 13 Oct:** [what went wrong with Clippy (The New Stack, Nass)](https://thenewstack.io/humanity-vs-clippy-lessons-from-microsofts-failed-virtual-assistant/): repetition without learning, interrupting at the wrong moments; [Mico, Microsoft's 2025 successor](https://www.news4jax.com/business/2025/10/23/microsoft-hopes-mico-succeeds-where-clippy-failed-as-tech-companies-warily-imbue-ai-with-personality/): optional, emoji-like, not sycophantic; [contextual help patterns (Chameleon)](https://www.chameleon.io/blog/contextual-help-ux): friction signals, frequency caps, dismissal; [timing of proactive help (City, University of London)](https://openaccess.city.ac.uk/id/eprint/15028/5/timingAssistance_avi_0412.pdf): individual preference matters more than delay; [state-driven mascot animation](https://dev.to/uianimation/building-duolingo-style-ai-mascot-animations-with-rive-2446): idle, thinking, talking, reacting; [docs search with SQLite FTS5](https://scottspence.com/posts/give-coding-agents-your-project-docs-with-node-sqlite-and-fts5): split on headings, weight titles above body.

## 5. Brand note

Jon's house style says never to recolour or redraw the logo. The 3D crest keeps his shapes exactly (traced, not redrawn), but it adds a metal finish and a richer purple at Tim's request. It is the Studio's app mark only, and needs Jon's sign-off before it is used anywhere else (register S-35). The helper character is named Jon at Tim's request; he is an original cartoon, not a likeness, and Jon Chadwick should agree to lend his name (G-44). His original files are unchanged in `sources/` and `packaging/brand/`.

## 6. The Room (1.0.8)

- **Same room, same light.** The Room uses the Studio's tokens: ink surfaces, gold only for the selected control and the primary action, ivory for reading. The phone app carries the same palette and fonts (bundled), sized for a thumb: a bottom bar (Today, Board, Chat, Meet) and 44 px targets.
- **Calm by rule (photosensitivity).** Speaking is a steady gold ring, never a pulse; the level meter is smoothed and updates every 500 ms under reduced motion; nothing flashes. Live updates redraw the board in place.
- **Plain words for security.** "Encrypted" in the top bar; the oversight notice says executives can read every space and every read is logged; safety words appear as three large words on both screens; a call that can't be encrypted is refused with a sentence that says so.
- **Starting and joining.** Two cards and no jargon: Join with an invite, or Start a production (it lives on this PC). The switcher lists every production the person is in, marks those hosted on this PC, and offers both actions.
