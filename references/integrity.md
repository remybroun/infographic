# Integrity & accessibility

An infographic is a persuasive form, which is exactly why it needs rules. The
same techniques that make a finding land make a false finding land harder.

---

## Never fabricate

- **Do not invent data to complete a shape.** If the source says "bookings grew
  steadily since 2021" without the yearly numbers, you have a `stat` or a
  `callout`, not a line chart. A fabricated series is worse than no chart,
  because it looks like evidence.
- **Do not compute a total the source never stated** and present it as a fact.
  Derive it if you must, and say so in the block's `note`.
- **Do not fill gaps by interpolation.** A `null` inside `values` breaks the
  line, deliberately. Bridging it invents observations.
- **Do not round a real quantity to nothing.** `fmt_compact` keeps a significant
  digit precisely so 0.031 never prints as "0".

## Never distort

- **Bars start at zero.** Length encodes magnitude, so a truncated baseline
  multiplies the apparent difference. Lines and dumbbells may use a fitted domain
  because they encode *position and change*, not length, that difference is why
  `bar` forces zero and `dumbbell` does not.
- **One axis.** A dual axis invents a correlation the data does not contain.
- **Comparable charts share a scale.** Two heatmaps that each normalize to
  themselves look comparable and are not. Pin `min` and `max`.
- **Do not sort away a meaningful order.** Sorting ordered bands by value
  destroys the thing the reader needed. Use `sort: null`.
- **Areas and angles are decoded loosely.** Treemaps and donuts always carry
  labels and a table view.
- **Percentages need their base.** "61%" of what, out of how many? Put it in the
  `note`.

## Name the uncertainty

- **Say which statistic it is.** A median and a mean tell different stories; a
  document that shows one and implies the other is misleading even when every
  number is correct.
- **Name the comparison in a delta.** `delta_period` exists because "+22%" against
  nothing means nothing.
- **Mark judgement as judgement.** `quadrant` positions are normalized opinions,
  not measurements. Say so in the note.
- **Small samples get their n.** A percentage from 12 responses is a
  conversation, not a finding.
- **Correlation is not cause.** If the document implies a mechanism the data does
  not establish, a `callout` naming that limit is not optional.

## What the document must always carry

- A `footnotes` block: source, period, exclusions, and what not to conclude.
- A `note` on any block whose numbers are derived, estimated or partial.
- The real definition of any metric the reader might define differently.

---

# Accessibility

The output is a PDF, so most interactive escape hatches are unavailable. That
raises the bar rather than lowering it.

## Never colour alone

Every meaning carried by hue is also carried by something else:

- **Legends** for ≥2 series, always, never colour-matching alone.
- **Direct labels** on the marks the argument depends on.
- **Status** always ships an icon and a label alongside the colour.
- **Deltas** carry an arrow as well as a colour, and the arrow and the number
  never disagree.
- **Matrix cells** use distinct shapes (check, cross, dash), not just fills.
- **Texture** (`--texture`) is the backup channel for full CVD, greyscale print
  and forced-colors. One directional fill at 45°/135°, never decorative, never on
  by default.

## The table view is not optional

Every chart ships a table-view twin: collapsed on screen, force-opened in print.
It is the only route to a value that lives inside a mark too small to label, and
the only route for a screen reader. `--no-tables` is an accessibility regression
and the linter reports its absence as an **error**.

## Contrast floors

| Content | Minimum |
|---|---|
| body and label text | 4.5:1 |
| large text (≥24px, or ≥19px bold) | 3:1 |
| data marks, icons, focus rings | 3:1 |
| the de-emphasis gray, still a mark | 3:1 |

`validate_theme.py` checks every ink role, and every status text role, against
every surface, and the self-test pins the de-emphasis floor. Do not eyeball any
of it.

## Structure

- Real heading elements (`h1`/`h2`/`h3`) in document order, so the PDF has an
  outline.
- Every `<img>` has `alt`; the linter errors without it.
- Charts are `role="img"`; their content is reachable via the table view.
- Text stays selectable, legends, labels and tables are HTML, not paths.
- Set `meta.lang`.

## The greyscale test

Build the document a second time with `--theme mono` and look at it. Anything
that stops working there was relying on hue alone, and will fail for a
photocopier and for a reader with severe colour vision deficiency alike. The
`mono` theme forces the texture channel on for exactly this reason.
