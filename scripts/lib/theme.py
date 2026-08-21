"""Theme loading and the render context every block receives.

A theme is data, never code: `themes/*.json` supplies ramps, ink, surfaces,
geometry and type. Renderers read roles (`t.ink("secondary")`, `t.series(2)`)
and never literal hex, so swapping a theme re-skins the whole document without
touching a single block.
"""

from __future__ import annotations

import json
import os
import re

from . import svg

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(os.path.dirname(HERE))
THEME_DIR = os.path.join(SKILL_ROOT, "themes")


class Theme:
    def __init__(self, data: dict, path: str = ""):
        self.data = data
        self.path = path
        self.name = data.get("name", "custom")

    # -- loading -----------------------------------------------------------

    @classmethod
    def load(cls, name_or_path: str = "default") -> "Theme":
        candidates = [
            name_or_path,
            os.path.join(THEME_DIR, f"{name_or_path}.json"),
            os.path.join(THEME_DIR, name_or_path),
        ]
        for candidate in candidates:
            if candidate and os.path.isfile(candidate):
                with open(candidate, "r", encoding="utf-8") as handle:
                    return cls(json.load(handle), os.path.abspath(candidate))
        available = sorted(
            f[:-5] for f in os.listdir(THEME_DIR) if f.endswith(".json")
        )
        raise SystemExit(
            f"[theme] unknown theme {name_or_path!r}. Available: {', '.join(available)}"
        )

    @classmethod
    def available(cls):
        return sorted(f[:-5] for f in os.listdir(THEME_DIR) if f.endswith(".json"))

    # -- roles -------------------------------------------------------------

    def surface(self, role: str = "card") -> str:
        return self.data["surface"].get(role, self.data["surface"]["card"])

    def ink(self, role: str = "primary") -> str:
        return self.data["ink"].get(role, self.data["ink"]["primary"])

    def rule(self, role: str = "grid") -> str:
        return self.data["rule"].get(role, self.data["rule"]["grid"])

    def status(self, role: str = "good") -> str:
        return self.data["status"].get(role, self.data["status"]["good"])

    @property
    def accent(self) -> str:
        return self.data.get("accent", self.data["series"][0])

    @property
    def deemphasis(self) -> str:
        return self.data.get("deemphasis", self.rule("axis"))

    def series(self, index: int) -> str:
        """Categorical slot. Assigned in fixed order, NEVER cycled.

        Past slot 8 the honest answers are: fold the tail into "Other", facet
        into small multiples, or switch form. A generated 9th hue is
        indistinguishable under CVD, so we clamp and let `check_document.py`
        report it rather than silently inventing a color.
        """
        slots = self.data["series"]
        return slots[min(int(index), len(slots) - 1)]

    def series_count(self) -> int:
        return len(self.data["series"])

    def ramp(self, alt: bool = False):
        key = "sequential_alt" if alt else "sequential"
        return self.data.get(key, self.data["sequential"])["steps"]

    def sequential(self, t: float, alt: bool = False) -> str:
        """Continuous magnitude: 0 -> lightest step, 1 -> darkest."""
        steps = self.ramp(alt)
        t = max(0.0, min(1.0, float(t)))
        return steps[int(round(t * (len(steps) - 1)))]

    def ordinal_steps(self, alt: bool = False):
        """The discrete ordered ramp, a separate, coarser list than the
        continuous one. It must clear ΔL ≥ 0.06 between steps and 2:1 at the
        light end, which the fine-grained sequential steps deliberately do not.
        `validate_theme.py` checks exactly this list."""
        key = "sequential_alt" if alt else "sequential"
        block = self.data.get(key, self.data["sequential"])
        return block.get("ordinal_steps") or block["steps"][3:]

    def ordinal(self, index: int, total: int, alt: bool = False) -> str:
        """Discrete ordered marks: funnel stages, tiers, process steps."""
        usable = self.ordinal_steps(alt)
        if total <= 1:
            return usable[len(usable) // 2]
        pos = max(0, min(int(index), total - 1)) / (total - 1)
        return usable[int(round(pos * (len(usable) - 1)))]

    def waiver(self, check: str):
        """A documented, reasoned exemption from a computable check.

        Waivers exist so a real brand constraint can be recorded rather than
        hidden by loosening the check for everyone. The check still runs and
        still reports; only the exit status is spared.
        """
        return self.data.get("waivers", {}).get(check)

    @property
    def grayscale(self) -> bool:
        return self.data.get("color_model") == "grayscale"

    def diverging(self, t: float) -> str:
        """t in [-1, 1]; 0 is the neutral midpoint that must read as 'nothing'."""
        d = self.data["diverging"]
        t = max(-1.0, min(1.0, float(t)))
        if t >= 0:
            return svg.mix(d["mid"], d["high"], t)
        return svg.mix(d["mid"], d["low"], -t)

    # -- typography & geometry --------------------------------------------

    def font(self, role: str = "sans") -> str:
        return self.data["type"].get(role, self.data["type"]["sans"])

    @property
    def display_weight(self) -> int:
        return int(self.data["type"].get("display_weight", 650))

    @property
    def title_face(self) -> str:
        """Which face block titles take: `sans` (default) or `display`.

        Only worth setting on a theme whose display face is genuinely a second
        family. Where display and sans are the same stack, this changes nothing
        but the weight.
        """
        return str(self.data["type"].get("block_title", "sans"))

    def geom(self, key: str, fallback=0):
        return self.data.get("geometry", {}).get(key, fallback)

    # -- helpers -----------------------------------------------------------

    def ink_on(self, fill: str) -> str:
        return svg.ink_on(fill, self.ink("on_fill_dark"), self.ink("on_fill_light"))

    def wash(self, color: str, amount: float = 0.12, on: str = None) -> str:
        """Flatten a series hue to a pale opaque fill on the given surface."""
        return svg.alpha_over(color, on or self.surface("card"), amount)

    def fonts_dir(self) -> str:
        fonts_dir = self.data.get("fonts_dir", "")
        if fonts_dir.startswith("SKILL:"):
            fonts_dir = os.path.abspath(os.path.join(SKILL_ROOT, fonts_dir[len("SKILL:"):]))
        return fonts_dir

    def fonts_css(self) -> str:
        css = self.data.get("fonts_css", "")
        if not css:
            return ""
        fonts_dir = self.fonts_dir()
        return css.replace("{FONTS}", "file://" + fonts_dir if fonts_dir else "")

    def missing_font_files(self):
        """The @font-face sources this theme declares that are not on disk.

        A missing file is silent: Chrome falls back to the next family in the
        stack and the page still renders, just in Georgia instead of the brand
        face, which nobody notices until it is printed. `fonts_dir` can point
        outside the skill, so this is a real failure mode for anyone who has the
        skill but not the brand assets beside it.
        """
        css = self.data.get("fonts_css", "")
        if not css:
            return []
        fonts_dir = self.fonts_dir()
        names = re.findall(r"\{FONTS\}/([^']+)", css)
        return sorted({n for n in names
                       if not os.path.isfile(os.path.join(fonts_dir, n))})

    def texture_def(self, uid: str, color: str, angle: int = 45) -> str:
        """The accessibility channel: one directional fill at 45 or 135 degrees.
        Never decorative, never on by default."""
        return (
            f'<pattern id="{uid}" width="6" height="6" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate({angle})">'
            f'<rect width="6" height="6" fill="{svg.esc(self.wash(color, 0.16))}"/>'
            f'<line x1="0" y1="0" x2="0" y2="6" stroke="{svg.esc(color)}" stroke-width="2.2"/>'
            f"</pattern>"
        )


class Ctx:
    """Everything a block renderer needs that is not its own payload.

    `width` is the block's rendered width in SVG user units. Blocks are authored
    at a nominal width and scale to their grid column, so this is a design width,
    not a physical one.
    """

    def __init__(self, theme: Theme, width: float = 720.0, options: dict = None,
                 texture: bool = False, doc: dict = None, density: str = "graphic"):
        self.theme = theme
        self.width = float(width)
        self.options = options or {}
        self.texture = bool(texture) or bool(theme.data.get("force_texture"))
        self.doc = doc or {}
        self.density = density
        self.warnings = []

    @property
    def graphic(self) -> bool:
        """True when the picture carries the idea, so a renderer should choose
        its tile form over its prose form.

        `lesson` counts. It is graphic density with room to teach, not a step
        towards report density: a lesson that renders its definitions as a
        two-column list of sentences is the glossary-at-the-back failure this
        skill added the lesson mode to prevent.
        """
        return self.density in ("graphic", "lesson")

    def warn(self, message: str):
        self.warnings.append(message)

    def opt(self, key: str, fallback=None):
        return self.options.get(key, fallback)

    def sub(self, width: float, options: dict = None) -> "Ctx":
        child = Ctx(self.theme, width, options or self.options, self.texture,
                    self.doc, self.density)
        child.warnings = self.warnings
        return child
