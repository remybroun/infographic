"""Pictograms: a small library of drawn objects, for when the subject has a shape.

Every other drawing primitive in this skill is abstract. `svg.py` computes arcs,
bands, ribbons and scales; the kit classes in `drawing.md` name nodes, edges,
fields and rings. All of it is geometry, and geometry is the right vocabulary
for the thing this skill is mostly about: containment, convergence, attenuation,
spread.

But some documents are about apartments, or people, or aeroplanes, and for those
the geometry vocabulary quietly forces a translation. "Properties by city"
becomes a bar chart because a bar is what the toolkit has, not because a bar is
what the reader needs. The isotype tradition solved this a century ago, and this
skill shipped `unit` under the name "isotype / waffle" while only being able to
draw squares.

So: fifty-two silhouettes on a shared 24-unit grid, available anywhere a block
takes a `glyph` or an `icon`, and referenceable from an authored `figure` as
`<use href="#ig-pic-home"/>`.

**None of this is required, and most documents should not use it.** A waffle of
plain squares is often the better chart, because a square is unambiguous and a
tiny drawn house is one bad render away from clip art. The whole library is
opt-in: no block reaches for a pictogram unless the spec names one, and the
defaults are exactly what they were before this module existed. The judgement of
whether a picture of the subject earns its place belongs to whoever is writing
the spec, and `references/drawing.md` says how to make that call rather than
making it for them.

Three properties make them safe to mix with the rest of the skill:

* **They carry no paint.** Not one shape in this file has a `fill` attribute, so
  every pictogram inherits colour from wherever it is placed. A `<use>` inside a
  chart gets the series colour; a `<use>` inside an authored `figure` gets the
  kit class, and the figure's colour-literal check passes without a special
  case, because there is no colour here to be a literal.
* **They live in the document, not in the block.** Emitted once as `<symbol>`
  defs alongside the arrowheads, for the same reason: a reference resolves
  against the document, so nothing has to carry a copy.
* **They cost no words.** A pictogram is not `<text>`, so it is not charged
  against the budget in `density.py`. That is the one respect in which drawing
  the subject is cheaper than naming it, and it is the argument for the whole
  module.

Shapes needing holes are written as a single path with `fill-rule="evenodd"`,
which is why several of them look like one long `d` with rectangle subpaths
inside: those subpaths are the windows.
"""

from __future__ import annotations

import difflib

# The grid every silhouette is drawn on. Shared, so pictograms of different
# subjects sit at the same optical weight when they appear in the same row.
GRID = 24.0

ID_PREFIX = "ig-pic-"

# name -> (category, inner markup). Categories exist for `ig.py pictograms`,
# which prints the library grouped, and for nothing else: there is no behaviour
# attached to a category.
PICTOGRAMS = {

    # -- place -------------------------------------------------------------

    "home": ("place",
             '<path d="M12 2.4 1.6 11.6h2.9v9.9h5.1v-5.9h4.8v5.9h5.1v-9.9h2.9z"/>'),

    "building": ("place",
                 '<path fill-rule="evenodd" d="M4.5 2.4h15v19.2h-15z'
                 'M7.2 5.4v2.9h3.5V5.4zM13.3 5.4v2.9h3.5V5.4z'
                 'M7.2 10.1v2.9h3.5v-2.9zM13.3 10.1v2.9h3.5v-2.9z'
                 'M7.2 14.8v2.9h3.5v-2.9zM13.3 14.8v2.9h3.5v-2.9z'
                 'M10.3 18.3v3.3h3.4v-3.3z"/>'),

    "apartment": ("place",
                  '<path fill-rule="evenodd" d="M12 1.8 1.8 6.9v14.7h20.4V6.9z'
                  'M5.6 11.2v3.4h4.2v-3.4zM14.2 11.2v3.4h4.2v-3.4z'
                  'M9.8 17.4v4.2h4.4v-4.2z"/>'),

    "city": ("place",
             '<path fill-rule="evenodd" d="M1.8 21.6v-9.4h5V8.2h4.6V3.4h5.2v6.4h5.6v11.8z'
             'M3.8 14.2v5.4h2.2v-5.4zM8.8 10.2v9.4h2.2v-9.4zM13.4 5.4v14.2h2.2V5.4z'
             'M18 11.8v7.8h2.2v-7.8z"/>'),

    "door": ("place",
             '<path fill-rule="evenodd" d="M4.6 2.2h14.8v19.6H4.6z'
             'M7.2 4.8v6.2h9.6V4.8zM7.2 13v6.2h5.4V13z'
             'M14.6 14.4a1.5 1.5 0 1 0 3 0 1.5 1.5 0 1 0-3 0z"/>'),

    "key": ("place",
            '<path fill-rule="evenodd" d="M3.2 12a4.4 4.4 0 1 0 8.8 0 4.4 4.4 0 1 0-8.8 0z'
            'M6 12a1.6 1.6 0 1 0 3.2 0A1.6 1.6 0 0 0 6 12z"/>'
            '<path d="M10.4 10.4h11.4v3.2H10.4zM16.2 13.6h2.2V17h-2.2z'
            'M19.6 13.6h2.2v2.4h-2.2z"/>'),

    "bed": ("place",
            '<path d="M2.4 6.6h2.8v9.2h16.4v5.6h-2.8v-2.8H5.2v2.8H2.4z"/>'
            '<path d="M6.6 10.6h3.8v3.4H6.6z"/>'
            '<path d="M11.6 9.6h7a2.8 2.8 0 0 1 2.8 2.8v1.6h-9.8z"/>'),

    "map_pin": ("place",
                '<path fill-rule="evenodd" d="M12 2.2a7.4 7.4 0 0 0-7.4 7.4'
                'c0 5.3 7.4 12.2 7.4 12.2s7.4-6.9 7.4-12.2A7.4 7.4 0 0 0 12 2.2z'
                'M12 6.8a2.8 2.8 0 1 1 0 5.6 2.8 2.8 0 0 1 0-5.6z"/>'),

    "globe": ("place",
              '<path fill-rule="evenodd" d="M12 2.4a9.6 9.6 0 1 0 0 19.2 9.6 9.6 0 0 0 0-19.2z'
              'M12 4.6a7.4 7.4 0 1 1 0 14.8 7.4 7.4 0 0 1 0-14.8z"/>'
              '<path d="M4.6 10.9h14.8v2.2H4.6z"/>'
              '<path fill-rule="evenodd" d="M12 2.4c2.6 0 4.6 4.3 4.6 9.6s-2 9.6-4.6 9.6'
              '-4.6-4.3-4.6-9.6S9.4 2.4 12 2.4z'
              'M12 4.6c-1.3 0-2.4 3.3-2.4 7.4s1.1 7.4 2.4 7.4 2.4-3.3 2.4-7.4-1.1-7.4-2.4-7.4z"/>'),

    # -- people ------------------------------------------------------------

    "person": ("people",
               '<path d="M12 2.6a4.2 4.2 0 1 1 0 8.4 4.2 4.2 0 0 1 0-8.4z"/>'
               '<path d="M12 12.4c4.4 0 8 2.9 8 6.5v2.7H4v-2.7c0-3.6 3.6-6.5 8-6.5z"/>'),

    "people": ("people",
               '<path d="M8.4 3.4a3.7 3.7 0 1 1 0 7.4 3.7 3.7 0 0 1 0-7.4z"/>'
               '<path d="M16.8 4.6a3.2 3.2 0 1 1 0 6.4 3.2 3.2 0 0 1 0-6.4z"/>'
               '<path d="M8.4 12.2c3.9 0 7 2.5 7 5.6v3.2H1.4v-3.2c0-3.1 3.1-5.6 7-5.6z"/>'
               '<path d="M17.2 12.4c3 0 5.4 1.9 5.4 4.3v4.3h-5.3v-3.2'
               'c0-1.9-.7-3.6-1.9-4.9.6-.3 1.2-.5 1.8-.5z"/>'),

    "group": ("people",
              '<path d="M12 3a3.6 3.6 0 1 1 0 7.2A3.6 3.6 0 0 1 12 3z"/>'
              '<path d="M5 5.4a3 3 0 1 1 0 6 3 3 0 0 1 0-6z"/>'
              '<path d="M19 5.4a3 3 0 1 1 0 6 3 3 0 0 1 0-6z"/>'
              '<path d="M12 11.6c3.3 0 6 2.2 6 4.9v4.9H6v-4.9c0-2.7 2.7-4.9 6-4.9z"/>'
              '<path d="M4.6 12.6c.6 0 1.2.1 1.7.3a7.4 7.4 0 0 0-2.3 5.3v3.2H.8v-4.3'
              'c0-2.5 1.7-4.5 3.8-4.5z"/>'
              '<path d="M19.4 12.6c2.1 0 3.8 2 3.8 4.5v4.3H20v-3.2a7.4 7.4 0 0 0-2.3-5.3'
              'c.5-.2 1.1-.3 1.7-.3z"/>'),

    # -- travel ------------------------------------------------------------

    "suitcase": ("travel",
                 '<path fill-rule="evenodd" d="M9 2.6h6a2.4 2.4 0 0 1 2.4 2.4v1.6h3.4'
                 'a1.8 1.8 0 0 1 1.8 1.8v11a1.8 1.8 0 0 1-1.8 1.8H3.2'
                 'a1.8 1.8 0 0 1-1.8-1.8v-11a1.8 1.8 0 0 1 1.8-1.8h3.4V5A2.4 2.4 0 0 1 9 2.6z'
                 'M9.4 5v1.6h5.2V5z"/>'),

    "plane": ("travel",
              '<path d="M22 12.6c0 .9-.7 1.6-1.6 1.6h-5.6l-3.4 6.6H9.2l1.7-6.6H6.6'
              'l-1.5 2.2H3.2l1.1-3.8-1.1-3.8h1.9l1.5 2.2h4.3L9.2 4.4h2.2l3.4 6.6h5.6'
              'c.9 0 1.6.7 1.6 1.6z"/>'),

    "car": ("travel",
            '<path fill-rule="evenodd" d="M3 11.4 5.2 5.8A2.6 2.6 0 0 1 7.6 4.2h8.8'
            'a2.6 2.6 0 0 1 2.4 1.6l2.2 5.6v6a1.4 1.4 0 0 1-1.4 1.4h-1.4'
            'a1.4 1.4 0 0 1-1.4-1.4v-.6H6.8v.6a1.4 1.4 0 0 1-1.4 1.4H4'
            'a1.4 1.4 0 0 1-1-1.4z'
            'M7.4 6.6 5.9 10.5h12.2l-1.5-3.9z"/>'),

    "calendar": ("travel",
                 '<path fill-rule="evenodd" d="M7.4 1.8h2.4V4h4.4V1.8h2.4V4h2.6'
                 'a2 2 0 0 1 2 2v13.8a2 2 0 0 1-2 2H4.8a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2.6z'
                 'M4.8 9.4v10.4h14.4V9.4z"/>'
                 '<path d="M7 11.6h2.6v2.6H7zM10.7 11.6h2.6v2.6h-2.6z'
                 'M14.4 11.6H17v2.6h-2.6zM7 15.4h2.6V18H7zM10.7 15.4h2.6V18h-2.6z"/>'),

    "clock": ("travel",
              '<path fill-rule="evenodd" d="M12 2.4a9.6 9.6 0 1 0 0 19.2 9.6 9.6 0 0 0 0-19.2z'
              'M12 4.8a7.2 7.2 0 1 1 0 14.4 7.2 7.2 0 0 1 0-14.4z"/>'
              '<path d="M10.9 6.6h2.2v6l4 2.3-1.1 1.9-5.1-2.9z"/>'),

    # -- money -------------------------------------------------------------

    "money": ("money",
              '<path fill-rule="evenodd" d="M1.8 5.6h20.4v12.8H1.8z'
              'M12 8.2a3.8 3.8 0 1 0 0 7.6 3.8 3.8 0 0 0 0-7.6z"/>'),

    "coins": ("money",
              '<path d="M12 3c4.6 0 8.4 1.3 8.4 3s-3.8 3-8.4 3-8.4-1.3-8.4-3S7.4 3 12 3z"/>'
              '<path d="M20.4 8.6v3c0 1.7-3.8 3-8.4 3s-8.4-1.3-8.4-3v-3'
              'c1.4 1.4 4.6 2.3 8.4 2.3s7-.9 8.4-2.3z"/>'
              '<path d="M20.4 13.6v3c0 1.7-3.8 3-8.4 3s-8.4-1.3-8.4-3v-3'
              'c1.4 1.4 4.6 2.3 8.4 2.3s7-.9 8.4-2.3z"/>'),

    "card": ("money",
             '<path fill-rule="evenodd" d="M1.6 5.2h20.8v13.6H1.6z'
             'M2.2 8.6v2.6h19.6V8.6z"/>'
             '<path d="M4.2 14h5v2.2h-5z"/>'),

    "chart": ("money",
              '<path d="M3 20.4V10h4.2v10.4zM9.9 20.4V4.6h4.2v15.8zM16.8 20.4v-7.2H21v7.2z"/>'),

    # -- document ----------------------------------------------------------

    "document": ("document",
                 '<path fill-rule="evenodd" d="M5 2.2h8.6l5.4 5.4v14.2H5z'
                 'M13.8 4.6v3.4h3.4zM7.8 11.2v1.8h8.4v-1.8zM7.8 14.8v1.8h8.4v-1.8z'
                 'M7.8 18.4v1.8h5.4v-1.8z"/>'),

    "folder": ("document",
               '<path d="M2.4 4.8h6.8l2.2 2.6h10.2a1.6 1.6 0 0 1 1.6 1.6v9.2'
               'a1.6 1.6 0 0 1-1.6 1.6H2.4A1.6 1.6 0 0 1 .8 18.2V6.4a1.6 1.6 0 0 1 1.6-1.6z"/>'),

    "envelope": ("document",
                 '<path fill-rule="evenodd" d="M1.8 4.8h20.4v14.4H1.8z'
                 'M4.2 7.2v9.6h15.6V7.2z"/>'
                 '<path d="M3.4 6 12 12.6 20.6 6 22 7.9l-10 7.6L2 7.9z"/>'),

    "chat": ("document",
             '<path d="M3.4 3.4h17.2a2 2 0 0 1 2 2v9.8a2 2 0 0 1-2 2H10l-5.6 4.4v-4.4h-1'
             'a2 2 0 0 1-2-2V5.4a2 2 0 0 1 2-2z"/>'),

    "phone": ("document",
              '<path fill-rule="evenodd" d="M7.8 2.2h8.4a2 2 0 0 1 2 2v15.6a2 2 0 0 1-2 2H7.8'
              'a2 2 0 0 1-2-2V4.2a2 2 0 0 1 2-2z'
              'M8 6.2v11.2h8V6.2z"/>'),

    "bell": ("document",
             '<path d="M12 2a2 2 0 0 1 2 2v.6a6.6 6.6 0 0 1 4.6 6.3v4l2 2.6v1.3H3.4v-1.3'
             'l2-2.6v-4A6.6 6.6 0 0 1 10 4.6V4a2 2 0 0 1 2-2z"/>'
             '<path d="M9.4 20.2h5.2a2.6 2.6 0 0 1-5.2 0z"/>'),

    # -- tech --------------------------------------------------------------

    "laptop": ("tech",
               '<path fill-rule="evenodd" d="M4.6 4.4h14.8v11.2H4.6z'
               'M6.6 6.4v7.2h10.8V6.4z"/>'
               '<path d="M1.6 16.8h20.8v1.4a1.4 1.4 0 0 1-1.4 1.4H3a1.4 1.4 0 0 1-1.4-1.4z"/>'),

    "server": ("tech",
               '<path fill-rule="evenodd" d="M3 3.4h18v6.4H3z'
               'M5.2 5.6v2h2.6v-2z"/>'
               '<path fill-rule="evenodd" d="M3 12.2h18v6.4H3z'
               'M5.2 14.4v2h2.6v-2z"/>'),

    "cloud": ("tech",
              '<path d="M7 19.6a5.4 5.4 0 0 1-.5-10.8 6.6 6.6 0 0 1 12.5 1.6'
              'a4.6 4.6 0 0 1-.8 9.2z"/>'),

    "database": ("tech",
                 '<path d="M12 2.6c4.8 0 8.6 1.4 8.6 3.2S16.8 9 12 9 3.4 7.6 3.4 5.8'
                 's3.8-3.2 8.6-3.2z"/>'
                 '<path d="M20.6 9v3.4c0 1.8-3.8 3.2-8.6 3.2s-8.6-1.4-8.6-3.2V9'
                 'c1.6 1.4 4.9 2.2 8.6 2.2s7-.8 8.6-2.2z"/>'
                 '<path d="M20.6 15.6V19c0 1.8-3.8 3.2-8.6 3.2S3.4 20.8 3.4 19v-3.4'
                 'c1.6 1.4 4.9 2.2 8.6 2.2s7-.8 8.6-2.2z"/>'),

    "lock": ("tech",
             '<path fill-rule="evenodd" d="M12 1.8a5.4 5.4 0 0 1 5.4 5.4v2.4h1.8v12.6H4.8V9.6'
             'h1.8V7.2A5.4 5.4 0 0 1 12 1.8z'
             'M12 4.2a3 3 0 0 0-3 3v2.4h6V7.2a3 3 0 0 0-3-3z'
             'M12 13.4a2.2 2.2 0 1 0 0 4.4 2.2 2.2 0 0 0 0-4.4z"/>'),

    "shield": ("tech",
               '<path d="M12 1.8 21 5v7.2c0 4.6-3.6 8.4-9 10-5.4-1.6-9-5.4-9-10V5z"/>'),

    "gear": ("tech",
             '<path fill-rule="evenodd" d="M10.4 2h3.2l.5 2.8c.6.2 1.2.4 1.8.8l2.3-1.6 2.3 2.3'
             '-1.6 2.3c.3.5.6 1.1.8 1.8l2.8.5v3.2l-2.8.5c-.2.6-.4 1.2-.8 1.8l1.6 2.3-2.3 2.3'
             '-2.3-1.6c-.5.3-1.1.6-1.8.8l-.5 2.8h-3.2l-.5-2.8c-.6-.2-1.2-.4-1.8-.8l-2.3 1.6'
             '-2.3-2.3 1.6-2.3c-.3-.5-.6-1.1-.8-1.8L1.6 14v-3.2l2.8-.5c.2-.6.4-1.2.8-1.8'
             'L3.6 6.2l2.3-2.3 2.3 1.6c.5-.3 1.1-.6 1.8-.8z'
             'M12 8.4a3.6 3.6 0 1 0 0 7.2 3.6 3.6 0 0 0 0-7.2z"/>'),

    "wifi": ("tech",
             '<path d="M12 16.6a2.6 2.6 0 1 1 0 5.2 2.6 2.6 0 0 1 0-5.2z"/>'
             '<path d="M12 10.6c2.3 0 4.4.9 5.9 2.4l-2.3 2.3a5.1 5.1 0 0 0-7.2 0l-2.3-2.3'
             'a8.3 8.3 0 0 1 5.9-2.4z"/>'
             '<path d="M12 4.6c3.9 0 7.5 1.6 10.1 4.2l-2.3 2.3a11 11 0 0 0-15.6 0L1.9 8.8'
             'A14.2 14.2 0 0 1 12 4.6z"/>'),

    # -- mark --------------------------------------------------------------

    "check": ("mark",
              '<path d="M9.6 18.6 3 12l2.5-2.5 4.1 4.1L18.5 5l2.5 2.5z"/>'),

    "cross": ("mark",
              '<path d="m12 9.5 5.9-5.9 2.5 2.5-5.9 5.9 5.9 5.9-2.5 2.5-5.9-5.9-5.9 5.9'
              '-2.5-2.5 5.9-5.9-5.9-5.9 2.5-2.5z"/>'),

    "warning": ("mark",
                '<path fill-rule="evenodd" d="M12 2.4 23 21.6H1z'
                'M10.7 8.8v6.4h2.6V8.8zM10.7 16.8v2.6h2.6v-2.6z"/>'),

    "star": ("mark",
             '<path d="m12 2.2 3 6.2 6.8.9-5 4.7 1.3 6.8-6.1-3.3-6.1 3.3 1.3-6.8-5-4.7'
             '6.8-.9z"/>'),

    "heart": ("mark",
              '<path d="M12 21.4 4.2 13.7a5.2 5.2 0 0 1 7.4-7.3l.4.4.4-.4'
              'a5.2 5.2 0 0 1 7.4 7.3z"/>'),

    "plus": ("mark",
             '<path d="M10.2 3.4h3.6v6.8h6.8v3.6h-6.8v6.8h-3.6v-6.8H3.4v-3.6h6.8z"/>'),

    "arrow_right": ("mark",
                    '<path d="M13.2 3.8 21.6 12l-8.4 8.2-2.5-2.5 4-3.9H2.4v-3.6h12.3l-4-3.9z"/>'),

    "flag": ("mark",
             '<path d="M4.4 2.2h2.4v19.6H4.4z"/>'
             '<path d="M7.6 3.2h12.8l-2.8 4.6 2.8 4.6H7.6z"/>'),

    "search": ("mark",
               '<path fill-rule="evenodd" d="M10.4 2.2a8.2 8.2 0 1 0 0 16.4 8.2 8.2 0 0 0 0-16.4z'
               'M10.4 4.8a5.6 5.6 0 1 1 0 11.2 5.6 5.6 0 0 1 0-11.2z"/>'
               '<path d="m16.1 17.9 1.8-1.8 4.5 4.5-1.8 1.8z"/>'),

    "eye": ("mark",
            '<path fill-rule="evenodd" d="M12 4.6c5 0 9.3 3 11.2 7.4-1.9 4.4-6.2 7.4-11.2 7.4'
            'S2.7 16.4.8 12C2.7 7.6 7 4.6 12 4.6z'
            'M12 7.6a4.4 4.4 0 1 0 0 8.8 4.4 4.4 0 0 0 0-8.8z"/>'),

    # -- thing -------------------------------------------------------------

    "box": ("thing",
            '<path d="M12 1.8 22.4 6.9 12 12 1.6 6.9z"/>'
            '<path d="M1.6 8.7 11.1 13.4v8.8L1.6 17.5z"/>'
            '<path d="M22.4 8.7v8.8l-9.5 4.7v-8.8z"/>'),

    "tool": ("thing",
             '<path d="M20.6 3.4a6.6 6.6 0 0 1-8.4 8.6L5.6 18.6a2.4 2.4 0 0 1-3.4-3.4'
             'l6.6-6.6a6.6 6.6 0 0 1 8.6-8.4l-3.6 3.6 1.2 3.4 3.4 1.2z"/>'),

    "tree": ("thing",
             '<path d="M12 1.8 19.4 12h-3.6l3.6 5.8h-5.6v4.4h-3.6v-4.4H4.6L8.2 12H4.6z"/>'),

    "sun": ("thing",
            '<path d="M12 7.4a4.6 4.6 0 1 1 0 9.2 4.6 4.6 0 0 1 0-9.2z"/>'
            '<path d="M10.8 1h2.4v3.8h-2.4zM10.8 19.2h2.4V23h-2.4z'
            'M19.2 10.8H23v2.4h-3.8zM1 10.8h3.8v2.4H1z'
            'm15.9-5.4 2.7 2.7-1.7 1.7-2.7-2.7zM4.4 17.9l2.7-2.7 1.7 1.7-2.7 2.7z'
            'm15.2-2 -2.7 2.7-1.7-1.7 2.7-2.7zM7.1 3.4l2.7 2.7-1.7 1.7-2.7-2.7z"/>'),

    "leaf": ("thing",
             '<path d="M20.8 3.2c1 8.6-3 15.4-10.4 15.4-1.6 0-3-.3-4.2-.9l-2.4 3.5-2-1.4'
             '2.4-3.5C2.6 14.6 2 12.4 2 10.2 2 4.4 8.4 1.4 20.8 3.2z"/>'),

    "bolt": ("thing",
             '<path d="M13.8 1.8 5.2 13.4h5l-3.4 8.8 11-13h-5.6z"/>'),

    "layers": ("thing",
               '<path d="M12 2.2 22.6 8 12 13.8 1.4 8z"/>'
               '<path d="m4.6 11.4 7.4 4 7.4-4 3.2 1.8L12 19 1.4 13.2z"/>'),
}

CATEGORY_ORDER = ("place", "people", "travel", "money", "document",
                  "tech", "mark", "thing")


def names():
    """Every pictogram name, in library order."""
    return list(PICTOGRAMS)


def by_category():
    """`[(category, [name, …]), …]` in CATEGORY_ORDER, for the catalog printer."""
    out = []
    for category in CATEGORY_ORDER:
        members = [n for n, (c, _) in PICTOGRAMS.items() if c == category]
        if members:
            out.append((category, members))
    return out


def has(name) -> bool:
    return isinstance(name, str) and name in PICTOGRAMS


def suggest(name: str, n: int = 4):
    """Near misses for an unknown name, so the error can say what was meant.

    The cutoff is high on purpose. Real typos score above 0.85 against their
    target (`aparment` 0.94, `persn` 0.91, `calender` 0.88); a name for a thing
    the library simply does not have tops out far lower (`hospital` 0.50,
    `pictogram` 0.40). At 0.45 the second group got suggestions too, so asking
    for a hospital was answered with "did you mean suitcase?", which is worse
    than no answer: the useful reply to a missing concept is that it is missing.
    """
    return difflib.get_close_matches(str(name), PICTOGRAMS, n=n, cutoff=0.7)


def resolve(name: str, where: str = "glyph") -> str:
    """The `<symbol>` id for `name`, or a build error listing what exists.

    Raises rather than falling back to a square, because a silent fallback means
    a document ships with the wrong picture and nothing says so.
    """
    if has(name):
        return f"{ID_PREFIX}{name}"
    # Counted, never written down. The first version of this message said
    # "fifty-one" and stayed saying it after a fifty-second shape was added,
    # which put a wrong number in the one place a reader is already unsure of
    # themselves and about to distrust the list printed underneath it.
    close = suggest(name)
    hint = (f"  Did you mean: {', '.join(close)}?\n" if close else
            f"  Nothing in the library is close to that, so there is probably\n"
            f"  no shape for it. A plain mark with a label is the honest answer:\n"
            f"  a near-miss silhouette is a claim the reader cannot check.\n")
    listing = "\n".join(
        f"    {category:<9} {' '.join(members)}" for category, members in by_category())
    raise SystemExit(
        f"[pictogram] {where}: unknown pictogram {name!r}.\n"
        f"{hint}"
        f"  The library is {len(PICTOGRAMS)} silhouettes, and it is optional: a chart\n"
        f"  with no `glyph` draws squares exactly as it always did.\n"
        f"{listing}\n"
        f"  See references/drawing.md for when a drawn subject earns its place.")


def symbol_defs() -> str:
    """Every pictogram as a `<symbol>`, for the document's shared defs.

    All of them, always. The alternative is scanning the spec for which are
    used, which cannot see a `<use>` written by hand inside an authored figure's
    markup, and a missing symbol renders as nothing at all with no error. The
    whole library is a few kilobytes of path data and compresses to less.
    """
    return "".join(
        f'<symbol id="{ID_PREFIX}{name}" viewBox="0 0 24 24">{markup}</symbol>'
        for name, (_category, markup) in PICTOGRAMS.items())


def use(name: str, x: float, y: float, size: float, where: str = "glyph",
        cls: str = None, fill: str = None, opacity=None) -> str:
    """One placed pictogram, square, at `size` units.

    `fill` is passed through for the built-in blocks, which compute a theme
    colour and hand it over. Authored figures leave it off and use `cls`
    instead, so the colour comes from the kit and the figure's colour-literal
    check has nothing to object to.
    """
    ref = resolve(name, where)
    bits = [f'href="#{ref}"', f'x="{_num(x)}"', f'y="{_num(y)}"',
            f'width="{_num(size)}"', f'height="{_num(size)}"']
    if cls:
        bits.append(f'class="{cls}"')
    if fill:
        bits.append(f'fill="{fill}"')
    if opacity is not None:
        bits.append(f'opacity="{_num(opacity)}"')
    return f'<use {" ".join(bits)}/>'


def _num(value) -> str:
    text = f"{float(value):.2f}".rstrip("0").rstrip(".")
    return text or "0"
