"""Rendering internals for the infographic skill.

Layering, outermost first:

    ig.py            one CLI over everything below
    build.py         spec (JSON) -> HTML document
    render_pdf.py    HTML -> PDF via headless Chrome
    check_document.py  lint the built document
    extract_source.py  source document -> fact ledger + candidate forms
    validate_theme.py  a theme's colours -> pass/fail against the six checks

    lib/registry.py  name -> renderer, plus the metadata the docs read
    lib/blocks_*.py  the renderers, grouped by the reader's job
    lib/chrome.py    axes, grids, legends, table views, shared chart furniture
    lib/theme.py     theme loading and the render context every block receives
    lib/svg.py       primitives, text metrics, scales, colour maths

Nothing here imports anything outside the standard library.
"""
