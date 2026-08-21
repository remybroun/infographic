#!/usr/bin/env python3
"""Run a whole theme through the computable color checks.

`validate_palette.py` (vendored from the dataviz skill, unmodified) checks one
palette. This runs every part of a theme that can be measured, against that
theme's OWN surfaces, which is the part people skip when they swap in brand
colors, and the reason a "brand-safe" palette so often turns out not to be:

  * categorical slots, adjacent pairs (stacks, bars, lines);
  * categorical slots, all pairs, first three (scatter, bubble, small multiples);
  * the sequential ramp as an ordinal ramp;
  * ink-on-surface pairs against WCAG text contrast.

Never eyeball any of this. Run it, and fix every FAIL before shipping a theme.

    python3 scripts/validate_theme.py rentos
    python3 scripts/validate_theme.py --all
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import validate_palette as vp  # noqa: E402
from lib.theme import Theme  # noqa: E402

TEXT_PAIRS = (
    ("body text", "ink.secondary", "surface.page", 4.5),
    ("primary text", "ink.primary", "surface.page", 4.5),
    ("muted text", "ink.muted", "surface.page", 4.5),
    ("body on card", "ink.secondary", "surface.card", 4.5),
    ("muted on sunken", "ink.muted", "surface.sunken", 4.5),
    ("accent as small text", "ink.accent_text", "surface.page", 4.5),
    ("accent as a fill", "accent", "surface.page", 3.0),
    ("good delta text", "status.good_text", "surface.page", 4.5),
    ("warning mark text", "status.warning_text", "surface.page", 4.5),
    ("critical delta text", "status.critical_text", "surface.page", 4.5),
    ("gridline", "rule.grid", "surface.card", 1.12),
)


def dig(theme: Theme, path: str) -> str:
    if path == "accent":
        return theme.accent
    group, key = path.split(".")
    return theme.data[group][key]


WAIVABLE = {"Lightness band": "lightness_band", "Chroma floor": "chroma_floor"}


def report(theme: Theme, rows, ok_all):
    """Print each check. A documented waiver downgrades a FAIL to WAIVED and
    prints the recorded reason, the measurement is never hidden."""
    effective = True
    for name, ok, detail in rows:
        if not ok and WAIVABLE.get(name) and theme.waiver(WAIVABLE[name]):
            waiver = theme.waiver(WAIVABLE[name])
            print(f"  [WAIVE] {name:<26} {detail}")
            print(f"          ↳ waived: {waiver['reason']}")
            continue
        if not ok:
            effective = False
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<26} {detail}")
    return effective


def check_theme(name: str, strict: bool = False) -> bool:
    theme = Theme.load(name)
    surface_light = theme.surface("card")
    palette = theme.data["series"]
    ok = True

    print(f"\n=== theme: {theme.name} ({theme.data.get('label', '')}) ===")
    print(f"surface (card) {surface_light} · page {theme.surface('page')}")

    if theme.grayscale:
        print("color model: grayscale, hue carries no identity, so the band and "
              "chroma checks are waived by design and texture is forced on.")

    print("\ncategorical slots, adjacent pairs (bars, stacks, lines)")
    rows, good = vp.validate(palette, "light", surface_light, "adjacent")
    ok = report(theme, rows, good) and ok

    print("\ncategorical slots 1-3, all pairs (scatter, bubble, small multiples)")
    rows, good = vp.validate(palette[:3], "light", surface_light, "all")
    ok = report(theme, rows, good) and ok

    print("\nordinal ramp (discrete ordered marks)")
    rows, good = vp.validate_ordinal(theme.ordinal_steps(), "light", surface_light)
    ok = report(theme, rows, good) and ok

    print("\nordinal ramp, alternate hue")
    rows, good = vp.validate_ordinal(theme.ordinal_steps(alt=True), "light", surface_light)
    ok = report(theme, rows, good) and ok

    print("\ntext & chrome contrast (WCAG)")
    for label, fg_path, bg_path, minimum in TEXT_PAIRS:
        fg, bg = dig(theme, fg_path), dig(theme, bg_path)
        ratio = vp.contrast(fg, bg)
        passed = ratio >= minimum
        if not passed:
            ok = False
        print(f"  [{'PASS' if passed else 'FAIL'}] {label:<26} {fg} on {bg}, "
              f"{ratio:.2f}:1 (need {minimum}:1)")

    print(f"\n  → {'ALL CHECKS PASS' if ok else 'FAILURES ABOVE, fix before shipping this theme'}")
    if theme.data.get("force_texture"):
        print("  note: this theme forces the texture channel; hue carries no identity here, "
              "so every multi-series block must also direct-label.")
    return ok


def main():
    parser = argparse.ArgumentParser(description="Validate an infographic theme's colors.")
    parser.add_argument("theme", nargs="?", default="default")
    parser.add_argument("--all", action="store_true", help="check every bundled theme")
    args = parser.parse_args()

    names = Theme.available() if args.all else [args.theme]
    results = {name: check_theme(name) for name in names}
    failed = [n for n, ok in results.items() if not ok]
    if failed:
        print(f"\nFAILED: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
