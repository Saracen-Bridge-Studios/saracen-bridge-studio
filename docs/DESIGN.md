# Saracen Bridge Studio: Design ("The Screening Room", 0.4; crisp black from 1.2.1)

**Version:** 1.2.1, 5 November 2026 (first written 13 October 2026)
**Brief (Tim, 13 Oct):** "a really high end look … very very clean, really nice pop-ups, slick colours, using the purple, gold and black … like a million-dollar piece of software", with 3D depth, a 3D logo, a Tauri window, an in-app assistant on Gemma and an optional cloud AI.
**Revised brief (Tim, 5 Nov):**
- "more classy and rich looking";
- "less purple … make purple the luxury but make it cleaner";
- "leave the crisp black, don't dull it down".

## 1. The idea

A private screening room at night. **From 1.2.1 the walls are crisp black, and purple is the jewel, not the room.** It appears only where it means something: the crest, the Home marquee's light, the suite's icon wells, the AI (Jonny, notices, AI pills) and switches. Gold light falls only on what matters: the primary action, the selected control, and the figures that decide something. Ivory is for reading. The app is dark by design, because the brand is dark.

| Role | Colour | Used for |
|---|---|---|
| Room (ink 0–5) | #050505 → #2a2a2d, true blacks; lighter means higher. Hairlines are warm white at 8.5 / 14 / 24% | Backgrounds and raised surfaces (elevation by lightness, not shadow) |
| Purple (plum) | #241240 → #e6d4ff; crest #3f1f70 / #6b3fb4; icon wells #5a2fa0 → #241040 | The jewel: crest, marquee light, icon wells, the AI, switches |
| Gold | #6c4b0f → #fff0c4, centre #dba534. Metal gradient #fbe7ad → specular #fff6d8 → #efc65f → #d9a53a → #a8761c; selected sweep #fff1c8 → #ad7a1c | Primary actions, selection, key figures, the crest |
| Ivory | #f4efe6; greys #c6c0b6 / #938d84 / #67625c | Text |
| States | green #82caa0, amber #e3946a, red #e88686 (desaturated) | Ready / preliminary / fail, never competing with gold |

**History of the palette:**
- **13 Oct:** Tim asked for "richer purples and sharper gold colours". The purple moved from the crest's dusty #382843 to a royal aubergine, which tinted every surface (#07050b → #2d203e).
- **5 Nov:** he asked for less purple and crisp black. The room went to true black and the purple was gathered into the jewel places.

**Type.** All three fonts are bundled (SIL OFL) in `ui/fonts`; nothing loads from the internet.
- **Source Serif 4** for display: titles, figures, the hero.
- **Geist** for interface text and, from 1.2.1, labels: capitals at 600 weight, tracking .15em, with the `case` feature on.
- **Geist Mono** only for keys and genuine codes.
- Numbers in tables are lining and tabular in Geist.
- The bundled Source Serif 4 has no small caps (checked 5 Nov: its OpenType features are ccmp, dnom, frac, liga, locl, numr, pnum, tnum), and `font-synthesis` forbids faked ones.

Why Source Serif 4 (13 Oct): Tim asked for a serif "like this but not as compressed … slightly wider".
- Instrument Serif (0.4.6 and earlier) was replaced by Source Serif 4, about 20% wider at the same size.
- It has true italics, lining figures and an optical-size axis the browser follows automatically.
- Candidates set side by side: Newsreader (133%, too wide), Libre Caslon Display (111%, no italic), Cormorant (116%, old-style figures), Playfair, Bodoni Moda, Gilda, Fraunces and DM Serif Display.

**Scale lock (0.4.7).** Text and layout scale as one.
- A single uniform zoom on the page (`--uiz`), never a per-axis stretch, so letters keep their shape on any screen.
- Auto follows the window's shorter side against the 1440 × 900 design size, damped by half and held between 90% and 120%. Settings › Display can pin 90, 100, 110 or 125%.
- Viewport units in the CSS divide by `--uiz`, so a zoomed page still fits the window exactly.
- Browser text inflation is off, faked bold is off (`font-synthesis: style`), widths are fixed at normal, and kerning is on.
- A monitor driven at a non-native, stretched resolution distorts every program, and the app can't undo that. Settings › Display says how to set Windows back to its recommended resolution.

**Restraint (1.2.1).**
- Gold reads as polished metal (a specular band and a darker rim) with a short, low glow.
- The "connect the AI engine" notice is a quiet hairline strip, not a filled banner.
- A card inside a card keeps only a hairline.
- Form fields are lifted rather than sunken, with the gold focus ring just outside.
- Tables have softer rules.
- A 44 px gold hairline closes each page's title block. It is an ornament, not a category label.

## 2. Components

- **Frame.** The rail sits on the bare room. The content is an inset sheet with rounded corners and a gold hairline across its top edge, so it reads as an application, not a web page. A sticky blurred top bar holds breadcrumbs, search, **Ask Saracen** and three shortcuts.
- **Rail (1.2.1).** All 17 pages and their groups fit at 900 px: 28 px rows and a slightly smaller crest plate. On shorter windows the rail keeps the current page in view, and fades an edge only when there is more list beyond it.
- **Home marquee.** A cinematic banner with:
  - slow-drifting purple and gold light (three radial layers moving by `transform` only);
  - a vignette and film grain;
  - the serif headline and the gold **Read a script** button;
  - a ledger of three facts: tools working, Library size, AI state.
- **The Suite.** One grid of all the tools, with filter chips by group. Each card has:
  - a gradient hairline border;
  - a spotlight that follows the pointer;
  - a faint serif tool number as a watermark;
  - a gentle 3D tilt (max 9°/7°), with the icon and title raised on `translateZ`.
  The icon wells are the purple jewels on black.
- **The 3D crest.** Jon's crest and wordmark were traced to vectors (potrace) from his own artwork: the crest from the 3000 px Analytics logo, the wordmark from the purple Studio logo. It is rendered in SVG as layers:
  - a soft gold glow;
  - an extruded side (stacked offset copies in dark gold under a drop shadow);
  - a polished face (a banded metal gradient through a specular-lighting bevel filter);
  - a light sweep.
  CSS 3D stacks the plate, crest and wordmark at different depths. It sits straight on and tilts only under the pointer. It is used in the rail, the start-up intro, the app icon and the installer panels.
- **Pressable gold button.** Josh Comeau's three-layer principle: a thicker gold edge below, a front that rises on hover with a slight overshoot and presses down in 34 ms, and a light sweep across the face on hover.
- **Selected = gold (0.4.7).** Tim: "when a tab is selected … a gold gradient similar to how Google Chrome does gradients, only when selected", pushed to every part of the app.
  - Every "you are here / this one is on" control carries the same luminous gradient (`--gold-tab`: a soft light at the top left over a champagne-to-deep-gold sweep).
  - It has dark ink text, a fine bevel, a warm glow beneath (shorter from 1.2.1), and one sheen across the face when it becomes selected.
  - It applies to: tool tabs, the Quick/Deep switch, the cloud provider picker, the sidebar's current page, the suite filter chips, Local compute and Cloud, the interface-size picker, and Jon's **Reads this page** toggle.
  - Unselected controls stay quiet. Lists moved through with the keyboard (the palette, the name finder) keep their soft highlight.
- **Privacy lamp (1.0.1).** In the sidebar footer, "Private · offline" has a small lamp: green and breathing on Local compute; red, with the words gone dark, while Cloud is on. "Private" appears once.
- **Shortlist (1.0.1).** Brand rows are picked by clicking: a gold tick, a gold bar on the left and a soft gold wash. The picks gather above the table as gold chips, each with its own remove.
- **Page head (0.4.7).** A page opens straight on its title. The category (Development, Sales & Marketing…) is already in the breadcrumb, so no label repeats it above the title (Tim, 13 Oct). The Library and Settings labels went the same way, and a saved run shows its date under the title instead.
- **Toasts, modals and the command palette.**
  - Toasts: bottom right, at most four, pause on hover, with a countdown hairline.
  - Modals: scale .96 → 1 with opacity; Esc and the scrim close them.
  - Command palette: Ctrl/Cmd+K or /, covering tools, places, actions and your recent work. Keyboard first, with no animation because it is keyboard-triggered.
- **Ask Saracen.** A glass drawer from the right (a bottom sheet on phones), with:
  - an engine line (Gemma on this PC, or a purple **Cloud** tag);
  - page-aware suggestions;
  - streamed answers with a gold caret;
  - in-app links rendered as gold chips;
  - a Stop button and a **Reads this page** toggle.
- **Jon / Jonny (0.4.1; renamed Jonny on 15 Oct).** Tim's idea: a helper character like Microsoft's paperclip. He is an original cartoon clapperboard (concept A of three).
  - He sits bottom right, blinks, watches the pointer, snaps his clapper as he talks, looks up while thinking, frowns at errors and hops at successes.
  - Clicking him opens the assistant.
  - Clippy's lessons are rules here: he offers and never insists; at most one tip per page and five per session; never while a field is being typed in; "Not now" snoozes that kind of tip; after three ignored tips in a row he stays quiet for the session; "Turn off tips" silences him for good.
  - He answers from Saracen Bridge's own documents, indexed locally (SQLite FTS5, BM25, `data/knowledge.db`).

## 3. Motion rules

- Ease-out `cubic-bezier(.23, 1, .32, 1)`.
- Most transitions under 300 ms.
- Entrances from `scale(.95–.96)` plus opacity; presses at `scale(.97)`.
- Hover effects only behind `@media (hover: hover)`.
- No animation on keyboard-triggered UI.
- Blur kept under about 20 px on large areas, and never animated.
- `prefers-reduced-motion` switches off drift, float, sweep, tilt and the intro.

## 4. Research (Rule 1)

**Round 1 (12–13 Oct), premium dark interfaces.** Findings used:
- elevate by lightness, and desaturate accents;
- ease-out under 300 ms, nothing animated for keyboard-triggered UI, scale-from-.95 entrances, a .97 press;
- command palettes with a large input, groups and keyboard navigation;
- toast offsets of 32/16 px;
- `backdrop-filter` limits;
- Tauri `decorations: false` breaks Windows 11 Snap Layouts, so a native title bar is kept.

Round 1 also advised against pure black. Tim chose crisp black on 5 Nov. Elevation is still by lightness on top of it, so raised surfaces stay distinguishable.

**Round 2 (13 Oct), 3D and depth:**
- [Josh Comeau: 3D button](https://www.joshwcomeau.com/animation/3d-button/)
- [Ryan Mulligan: CSS @property](https://ryanmulligan.dev/blog/css-property-new-style/)
- [Aave: Building glass for the web](https://aave.com/design/building-glass-for-the-web)
- [Kitemetric: hover tilt](https://kitemetric.com/blogs/create-a-stunning-hover-tilt-effect-with-pure-css)
- [Paper Shaders mesh gradient](https://21st.dev/@paper-design/components/mesh-gradient-purple.md) (not used)

**Round 3 (5 Nov), the "quiet luxury" pass.** The full report is `CIPHER_SARACEN_STUDIO_COSMETIC_REVIEW_20261105.md` (register S-122). Sources it rests on:
- [Linear: behind the latest design refresh](https://linear.app/now/behind-the-latest-design-refresh): "Don't compete for attention you haven't earned"; "Structure should be felt not seen".
- [IIAD: why some websites feel expensive](https://www.iiad.edu.in/the-circle/why-some-websites-just-feel-expensive/)
- [React Doctor: no uppercase mono labels](https://www.react.doctor/docs/rules/react-doctor/no-uppercase-mono-label)
- [Anthony Hobday: letter-spacing on capitals](https://anthonyhobday.com/sideprojects/visualtechniques/techniques/text/letter-spacing-on-all-capitals)
- [Refactoring UI notes](https://gist.github.com/ynotdraw/9351627d7509cc35813eeac4245cab3b)
- [Metal gradients in CSS](https://learnhowto.vercel.app/blog/css/forge-stunning-metal-text-effects-with-pure-css-a-comprehensive-guide)
- [HextaUI scroll fade](https://hextaui.com/docs/scroll-fade)
- [Banner blindness](https://en.wikipedia.org/wiki/Banner_blindness)

**Window, cloud AI and Jon research (13 Oct):** as recorded in the 1.0.1 version of this document:
- the Tauri 2 comparison;
- the Claude, Gemini and OpenAI streaming and model docs;
- Clippy and Mico, contextual help patterns, the timing of proactive help, and mascot state machines.

## 5. Brand note

Jon's house style says never to recolour or redraw the logo. The 3D crest keeps his shapes exactly (traced, not redrawn), but it adds a metal finish and a richer purple at Tim's request. It is the Studio's app mark only, and needs Jon's sign-off before it is used anywhere else (register S-35). The helper character is an original cartoon, not a likeness, and Jon Chadwick should agree to lend his name (G-44). His original files are unchanged in `sources/` and `packaging/brand/`.
