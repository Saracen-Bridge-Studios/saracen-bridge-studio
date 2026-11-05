# Saracen Bridge Studio: cosmetic review ("quiet luxury" pass)

**Date:** 5 November 2026 · **Build reviewed:** 1.2.0 · **Prototype:** a local branch, not merged. The patch is saved as `saracen_studio_refine_prototype_20261105.patch`, with before/after images in `cosmetic_review_20261105/`.

**Tim's ask (5 Nov):** "take a look at the saracen bridge app cosmetically, can it use any improvements to make it more classy and rich looking, do a rule 1 here".

## Verdict

The foundation is already high-end and stays as it is:
- the purple crest and the black-and-gold scheme;
- the serif titles;
- the cinematic Home marquee;
- elevation shown by lightness;
- film grain;
- the gold selected state.

What holds it back from feeling expensive is not missing decoration. It is **too many things asking for attention at once**:
- gold on four or five controls per screen, each with a glow;
- a terminal font on every label;
- a purple banner across the top of every tool;
- boxes inside boxes;
- form fields that read as black holes.

Luxury brands make the opposite move: restraint, with the one thing that matters lit. The research below converges on that.

There is also one real fault: at 1440 × 900 the rail can't show all its pages. Library and Settings sit under the Local compute switch, so when you're on them, the gold "you are here" bar is half hidden.

## What the prototype changes (CSS plus 10 lines of JS; no feature or layout changes)

| # | Change | Why (source) |
|---|---|---|
| 1 | **Rail fits and recedes.** Rows are 28 px, group gaps tighter and the crest plate a touch smaller, so all 17 pages fit at 900 px. Inactive items are a step dimmer. On shorter windows the rail fades only at the edge where there is more list, and scrolls to keep the current page in view. | Linear's March 2026 refresh: "Don't compete for attention you haven't earned"; the sidebar went "a few notches dimmer". Scroll-fade masks (HextaUI). |
| 2 | **Labels in the interface typeface.** WAITING, PAGES, table headers, group names and the eyebrow move from Geist Mono to Geist, uppercase, 600 weight, tracking .15em, with capital-height punctuation. Monospace stays for keys and codes. | React Doctor's design rule: "reserve monospace for values that are genuinely code-like". Anthony Hobday: open the tracking on all caps. Leg 3: the bundled Source Serif 4 has **no small caps** (checked: features ccmp, dnom, frac, liga, locl, numr, pnum, tnum), and `font-synthesis` forbids faked ones, so the labels use Geist caps. |
| 3 | **Figures set like a ledger.** Table numbers are lining and tabular in Geist instead of monospace. Geist carries `tnum` (checked). | Tabular figures for columns of numbers (MDN `font-variant-numeric`; CreativePro on tables). |
| 4 | **Gold reads as metal and glows less.** The gradient gains a specular band near the top and a darker rim. The selected-state gold keeps Tim's rule (13 Oct: gold gradient on every selected control) but is a little less saturated, with the glow cut from 20 px to 12 px. Primary buttons get a fine dark rim and a shorter, lower glow. | Metal reads as real from highlight, midtone and shadow bands, not flat yellow, and a strong glow should be toned down (LearnHowTo metal guide). Cartier-style dark plus metal works because the metal is scarce (IIAD). |
| 5 | **Notices become a quiet line.** "Connect the AI engine…" is a hairline-accented strip instead of a filled purple banner on every tool page. | Banner blindness: repeated banners stop being read. Linear: "Structure should be felt not seen". |
| 6 | **One surface per region.** A card inside a card loses its fill and lift and keeps a hairline. Cards get a faint top sheen. | Refactoring UI: fewer borders, and use background shades rather than nesting. Dev.to, "8 CSS properties that make dark UIs feel premium": a top-edge highlight gradient. |
| 7 | **Fields are lifted, not holes.** A faintly lit fill, a hairline that brightens on hover, and a gold focus ring just outside. Labels are a step brighter. | Refactoring UI: give inputs a subtle background. Premium dark UIs use focus rings with breathing room (dev.to). |
| 8 | **Tables: structure felt.** Transparent header, softer row rules, a faint gold wash on hover. | Linear: separators softened "to reduce visual noise". |
| 9 | **Page head ornament.** A 44 px gold hairline closes the title block. It is an ornament, not a category label, so Tim's 13 Oct rule (no category above the title) holds. | Editorial luxury layouts close a heading with a fine rule. |

All 285 tests still pass with the prototype. Checked by screenshot at 1440 × 900 and 1366 × 768.

## Recommended next, not yet built

1. **One hero figure per result.** On every results page (net incentive, budget total, sales take), set the deciding number large in serif gold and keep everything else quiet. The `kpi.edge` style exists but is used sparingly.
2. **Empty states with atmosphere.** The Library with few runs, and the Room before joining, leave large dead areas. A faint crest watermark and marquee light would make them feel intentional rather than unfinished.
3. **Jonny steps aside.** At 1366 × 768 he covers the "Offer tips" switch in Settings. He could dock smaller, and slide out of the way when content sits under him.
4. **Section entrances.** A 40 ms staggered fade-up of each page's sections, under 300 ms, within the existing motion rules, and off under reduced motion.
5. **Carry the finish to the phone Room.** It has its own stylesheet, so the same label, field and notice treatment would keep the iPhone app matching.

## Kept on purpose (Rule 1 leg 2: Tim's earlier directions)

- **12 Oct:** the purple Saracen Bridge logo for the program; black and gold for the software.
- **13 Oct:** the gold gradient on every selected control, only while selected. Refined here, not removed.
- **13 Oct:** no category label above a tool's title.
- **13 Oct:** Source Serif 4, chosen as "not as compressed", and the scale lock.
- **13 Oct:** "a million-dollar piece of software … very very clean, really nice pop-ups".

## Rule 1

**Leg 1, 12 online searches:**
- luxury digital restraint;
- gold-on-black contrast;
- premium dark-mode surfaces;
- why apps look expensive;
- Linear's 2026 refresh;
- tabular figures;
- film-software interfaces (Movie Magic, StudioBinder, Filmustage);
- the monospace-label critique;
- nested cards;
- Refactoring UI on forms;
- Criterion, MUBI and A24 editorial design;
- premium banking apps.

**Leg 2:**
- The conversation search returned nothing from this project.
- The design history was taken instead from the project's design document and the register: S-16, S-33, S-35, S-50, S-51 and S-52.

**Leg 3, 8 searches and fetches on the weak spots:**
- metal gradients that don't look cheap;
- scroll-fade masks;
- banner blindness;
- grain texture performance (the Studio's existing grain is already a static, stitched tile);
- small caps;
- floating helpers overlapping content;
- sidebar hierarchy.

There was also a local check of which OpenType features the bundled fonts actually carry. It changed item 2: small caps aren't available, so the labels use Geist caps.

## Sources

- [Linear: behind the latest design refresh](https://linear.app/now/behind-the-latest-design-refresh)
- [IIAD: why some websites just feel expensive](https://www.iiad.edu.in/the-circle/why-some-websites-just-feel-expensive/)
- [The 8 CSS properties that make dark UIs feel premium (dev.to)](https://dev.to/raxxostudios/the-8-css-properties-that-make-dark-uis-feel-premium-1kh7)
- [React Doctor: no-uppercase-mono-label](https://www.react.doctor/docs/rules/react-doctor/no-uppercase-mono-label)
- [Anthony Hobday: letter spacing on all capitals](https://anthonyhobday.com/sideprojects/visualtechniques/techniques/text/letter-spacing-on-all-capitals)
- [Refactoring UI notes (gist)](https://gist.github.com/ynotdraw/9351627d7509cc35813eeac4245cab3b)
- [MDN: font-variant-numeric](https://developer.mozilla.org/docs/Web/CSS/font-variant-numeric)
- [CreativePro: beautiful tables, working with numbers](https://creativepro.com/the-path-to-beautiful-tables-part-iii-working-with-numbers/2/)
- [Metal text effects with pure CSS](https://learnhowto.vercel.app/blog/css/forge-stunning-metal-text-effects-with-pure-css-a-comprehensive-guide)
- [HextaUI: scroll fade](https://hextaui.com/docs/scroll-fade)
- [SVG grain textures and performance](https://loke-dev-lokedevs-projects.vercel.app/blog/svg-grain-textures-performance)
- [Banner blindness (Wikipedia)](https://en.wikipedia.org/wiki/Banner_blindness)
