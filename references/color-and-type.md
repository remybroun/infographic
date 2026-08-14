# Colour & type

Colour in this skill is **computed, not chosen**. Every colour a block draws
comes from a role in the active theme, and every theme is checked by a script.
If you find yourself typing a hex value into a spec, stop and read this file.

```bash
python3 scripts/ig.py validate --all       # every bundled theme
python3 scripts/validate_theme.py rentos   # one theme, in detail
```

---

## The four colour jobs

| Job | Encodes | Structure | How a block asks for it |
|---|---|---|---|
| **Categorical** | identity, which series | 8 hues, fixed order, never cycled | default for multi-series blocks |
| **Ordinal** | position in a sequence | one hue, monotone lightness steps | `"ordinal": true` |
| **Sequential** | magnitude | one hue, light → dark | heatmap, treemap |
| **Diverging** | polarity | two opposite hues + neutral gray | `diverging`, `likert` |
| **Status** | state, good → critical | fixed, reserved, always with an icon | callouts, meters, deltas |

**Categorical or ordinal?** If swapping the order would change the meaning, funnel stages, size tiers, age bands, maturity levels, it is ordinal and takes
a one-hue ramp, so the reader sees the order in the colour. Product names, teams
and regions are nominal: one series takes slot 1, N series take slots 1..N.
Colouring nominal bars darker-where-bigger double-encodes length as hue and burns
the only free channel on information the bar already shows.

## The rules that never bend

- **Fixed slot order, never cycled.** The order *is* the colourblind-safety
  mechanism. `Theme.series()` clamps past slot 8 rather than wrapping, and the
  block warns. A ninth series folds into "Other", facets into small multiples, or
  changes form.
- **Scatter, bubble and small-multiples cap at three series.** Any two marks can
  sit side by side there, so all-pairs separation binds instead of adjacent-pairs.
- **Sequential is one hue, light to dark.** Never a rainbow.
- **Diverging is two opposite hues plus a neutral gray midpoint.** The midpoint
  must read as "nothing"; two cool hues as the poles fails.
- **Status colours are reserved.** Never "series 4", always with an icon and a
  label, so severity never depends on hue alone.
- **Text wears text tokens, never the series colour.** Values, labels and legends
  stay in primary/secondary/muted ink; a coloured mark *beside* the text carries
  identity. The one exception is a label set inside a filled shape, where the ink
  is picked by the fill's luminance so it always clears contrast.

## Emphasis: the most under-used form

One series in the accent, everything else in the de-emphasis gray. When the story
is "this one went up", that is emphasis, not eight identities, and it is usually
the honest answer to "make this chart clearer".

```json
{"type": "column", "categories": ["Jan", "…", "Jun"], "values": [...], "emphasis": "Mar"}
```

The de-emphasis gray is still a **data mark**, so it is held to 3:1 against the
surface like any other. A prettier, paler gray disappears in print; the self-test
asserts the floor.

## The six checks

Every categorical palette must pass all six before it ships. Five are computable
and the validator runs them; the sixth is structural.

1. **Fixed hue anchors**: eight families in a fixed order *(structural)*
2. **Lightness band**: OKLCH L ≈ 0.43-0.77 on a light surface
3. **Chroma floor**: OKLCH C ≥ 0.10, below which a hue reads as gray
4. **CVD separation**: OKLab ΔE ×100 ≥ 8 (floor 6 with secondary encoding) under
   simulated protanopia and deuteranopia, plus a normal-vision floor of 15
5. **Contrast vs surface**: ≥ 3:1 for marks, relaxed only where a visible label
   or the table view carries the value
6. **Documented palette only**: every slot comes from a theme file

`validate_theme.py` additionally checks the ordinal ramp (monotone lightness,
ΔL ≥ 0.06 between steps, light end ≥ 2:1) and WCAG text contrast for every ink
role against every surface.

## Waivers, not exceptions

A real brand constraint is recorded as a waiver in the theme, with a reason:

```json
"waivers": {
  "chroma_floor": {
    "colors": ["#5C6B2E"],
    "reason": "brand olive measures C 0.087 against a 0.10 floor. It is the
               defining brand colour and cannot be re-stepped; every other gate passes."
  }
}
```

The check still runs and still prints its measurement, only the exit status is
spared. This is deliberate: loosening a check for everyone to accommodate one
colour hides the next real failure.

## Adding a brand theme

1. Copy `themes/default.json`. Keep the structure; replace the values.
2. Fill `surface`, `ink`, `rule`, `status` from the brand.
3. For `series`, do not hand-pick an order. Enumerate candidate orderings of the
   brand's hues and keep only those that clear every gate, then choose among the
   passing ones for looks. `scripts/validate_theme.py` plus a short permutation
   loop is exactly how the bundled `rentos` order was found, and it is why brand
   olive and terracotta are deliberately **not** adjacent slots: that pair
   measures CVD ΔE 4.5, which a protanope cannot separate.
4. Give `ordinal_steps` explicitly. The fine-grained sequential steps are too
   close together to serve as discrete ordered marks.
5. Set `ink.accent_text` separately from `accent`: the accent as small text needs
   4.5:1 while the accent as a fill needs only 3:1. Collapsing them is how a good
   mark colour becomes an unreadable link.
6. Run `ig.py validate <name>` until it is green, then
   `ig.py catalog --sheet out/sheet.pdf --theme <name>` and look at the whole
   vocabulary at once.

---

# Typography

## Roles

| Role | Face | Where |
|---|---|---|
| Hero title | display, theme weight | `hero` |
| Section title | display | `section` |
| Quote | display | `quote` |
| Block title | theme's choice, sans by default | every block's `title`, and `callout` |
| Everything else | sans | body, labels, tables, charts |
| **Figures** | **sans, always** | `stat`, `kpi`, `hero_figure` |

**The hero figure is sans, never the display face.** A serif or display number
reads as off-brand decoration rather than as data. This holds even when the theme
has a beautiful serif, `rentos` sets Instrument Serif for headings and still
renders every figure in Inter.

**The block title is the one heading a theme gets to choose.** It is the smallest
heading on the page, which makes the choice of face a real decision rather than a
foregone one, so it is opt-in: `type.block_title: "display"`. Only set it on a
theme whose display face is genuinely a second family; where display and sans are
the same stack it changes nothing but the weight. A 400-weight serif needs more
size than a 600-weight sans to hold the same presence, and the build applies that
step for you. Do not push it further: at 1.3× body the extra leading pushed the
architecture fixture's last note into the running footer, which is where the
1.2× in `build.py` comes from.

## Scale

The type scale derives from `meta.page`; do not override sizes per block. If
something needs to be bigger, it probably needs to be a different block.

## The measure

Prose is capped at **68ch** regardless of span, because a 12-span paragraph on A4
runs to about 100 characters per line and stops being readable. Block subtitles
cap at 62ch, notes at 74ch. Use `columns: 2` when you genuinely have the copy.

## Figures

- **Proportional figures for large standalone numbers.** `tabular-nums` gives
  every digit the width of a `0`, which makes `121` look loose at display size.
- **Tabular figures only where numbers align vertically**, table rows and axis
  ticks. Both are set that way already.

## Print specifics

- Body is set in px and Chrome maps CSS px to 1/96in, so 13.4px ≈ 10pt.
- `text-wrap: balance` on headings and `pretty` on ledes; both are supported and
  materially improve ragged edges.
- Embedded fonts need an absolute `file://` path and enough `--wait` to load.
  Headings in the wrong face almost always mean one of those two.
