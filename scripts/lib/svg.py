"""SVG primitives, text metrics, scales and color math.

Dependency-free on purpose: every renderer in this skill emits SVG as a string,
so an infographic can be built on any machine with Python 3.9+ and printed with
headless Chrome. No matplotlib, no cairo, no font binaries required at build time.

The two things worth knowing before editing:

* `text_width` is an *approximation* built from average advance widths of a UI
  sans. It is used to decide whether a label fits inside a mark. It is tuned to
  slightly OVER-estimate, so the failure mode is "label moved outside the bar
  when it would just have fitted" rather than "label clipped". Never make it
  optimistic.
* Bars round only the corners at the data end (`bar_path`). A fully rounded bar
  detaches from its baseline and misstates the value at small magnitudes.
"""

from __future__ import annotations

import math
import re

# ---------------------------------------------------------------- escaping ---

_ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}


def esc(value) -> str:
    """XML-escape a value. All caller-supplied text goes through this."""
    return "".join(_ESC.get(ch, ch) for ch in str(value))


def num(value, places: int = 2) -> str:
    """Format a number for an SVG attribute without trailing zero noise."""
    if value is None:
        return "0"
    text = f"{float(value):.{places}f}".rstrip("0").rstrip(".")
    return text if text not in ("", "-") else "0"


def attrs(**kwargs) -> str:
    out = []
    for key, value in kwargs.items():
        if value is None or value is False:
            continue
        name = key.rstrip("_").replace("__", ":").replace("_", "-")
        if value is True:
            out.append(f'{name}=""')
        elif isinstance(value, float):
            out.append(f'{name}="{num(value)}"')
        else:
            out.append(f'{name}="{esc(value)}"')
    return (" " + " ".join(out)) if out else ""


# ------------------------------------------------------------ text metrics ---

# Average advance width as a fraction of font-size, by character class, for a
# humanist UI sans (Inter / SF / Segoe are within a few percent of each other).
_NARROW = set("ijltfrI.,:;'!|()[]{}/\\ ")
_WIDE = set("mwMW@%")
_DIGIT = set("0123456789")


def text_width(text: str, size: float, weight: int = 400, tracking: float = 0.0) -> float:
    """Approximate rendered width of `text` in px. Over-estimates by design."""
    if not text:
        return 0.0
    total = 0.0
    for ch in str(text):
        if ch in _NARROW:
            total += 0.30
        elif ch in _WIDE:
            total += 0.90
        elif ch in _DIGIT:
            total += 0.58
        elif ch.isupper():
            total += 0.68
        else:
            total += 0.53
    if weight >= 600:
        total *= 1.045
    return total * size + tracking * size * max(len(str(text)) - 1, 0) + 0.6


def truncate(text: str, size: float, max_width: float, weight: int = 400) -> str:
    """Ellipsize to fit. Returns text unchanged when it already fits."""
    text = str(text)
    if text_width(text, size, weight) <= max_width:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if text_width(text[:mid] + ell, size, weight) <= max_width:
            lo = mid
        else:
            hi = mid - 1
    return (text[:lo].rstrip() + ell) if lo else ell


def wrap(text: str, size: float, max_width: float, weight: int = 400, max_lines: int = 0):
    """Greedy word wrap into a list of lines."""
    words = re.split(r"\s+", str(text).strip())
    lines, current = [], ""
    for word in words:
        if not word:
            continue
        candidate = f"{current} {word}".strip()
        if current and text_width(candidate, size, weight) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    if max_lines and len(lines) > max_lines:
        kept = lines[:max_lines]
        kept[-1] = truncate(" ".join(lines[max_lines - 1:]), size, max_width, weight)
        lines = kept
    return lines or [""]


# ------------------------------------------------------------ number format ---

def fmt_compact(value, decimals: int = 1, currency: str = "", unit: str = "") -> str:
    """1284 -> 1.3K, 4200000 -> 4.2M. For display figures, not axis ticks."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    sign = "-" if v < 0 else ""
    v = abs(v)
    for limit, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if v >= limit:
            scaled = v / limit
            text = f"{scaled:.{decimals}f}".rstrip("0").rstrip(".")
            return f"{sign}{currency}{text}{suffix}{unit}"
    if not v % 1:
        return f"{sign}{currency}{int(v):,}{unit}"
    text = f"{v:,.{decimals}f}".rstrip("0").rstrip(".")
    # A non-zero value must never print as "0": rounding 0.031 to one decimal and
    # stripping the zero would display a real quantity as nothing. Keep adding
    # precision until at least one significant digit survives.
    if v > 0 and float(text.replace(",", "")) == 0:
        for extra in range(decimals + 1, decimals + 7):
            text = f"{v:,.{extra}f}".rstrip("0").rstrip(".")
            if float(text.replace(",", "")) != 0:
                break
    return f"{sign}{currency}{text}{unit}"


def fmt_plain(value, decimals: int = 0, currency: str = "", unit: str = "") -> str:
    """Thousands-separated. For axis ticks and table cells."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    if decimals == 0 and abs(v - round(v)) < 1e-9:
        return f"{currency}{int(round(v)):,}{unit}"
    return f"{currency}{v:,.{decimals}f}{unit}"


def fmt_delta(value, decimals: int = 1, unit: str = "%") -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    sign = "+" if v > 0 else ("−" if v < 0 else "")
    text = f"{abs(v):.{decimals}f}".rstrip("0").rstrip(".")
    return f"{sign}{text}{unit}"


# ------------------------------------------------------------------- color ---

def hex_to_rgb(value: str):
    value = str(value).strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb) -> str:
    return "#" + "".join(f"{max(0, min(255, int(round(c)))):02x}" for c in rgb)


def _srgb_to_linear(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(color: str) -> float:
    r, g, b = (_srgb_to_linear(c) for c in hex_to_rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def ink_on(fill: str, light: str = "#ffffff", dark: str = "#0b0b0b") -> str:
    """Pick the label color that clears contrast on a given fill."""
    return light if contrast(fill, light) >= contrast(fill, dark) else dark


def mix(a: str, b: str, t: float) -> str:
    """Linear sRGB-space mix. t=0 -> a, t=1 -> b."""
    ra, ga, ba = hex_to_rgb(a)
    rb, gb, bb = hex_to_rgb(b)
    return rgb_to_hex((ra + (rb - ra) * t, ga + (gb - ga) * t, ba + (bb - ba) * t))


def alpha_over(color: str, backdrop: str, alpha: float) -> str:
    """Flatten `color` at `alpha` over `backdrop` into an opaque hex.

    Print pipelines and PDF viewers handle opaque fills more predictably than
    alpha, and a flattened value keeps contrast checks meaningful.
    """
    return mix(backdrop, color, max(0.0, min(1.0, alpha)))


# ------------------------------------------------------------------ scales ---

class Linear:
    """Continuous scale, domain -> range."""

    def __init__(self, d0, d1, r0, r1):
        self.d0, self.d1, self.r0, self.r1 = float(d0), float(d1), float(r0), float(r1)
        if self.d1 == self.d0:
            self.d1 = self.d0 + 1.0

    def __call__(self, value) -> float:
        t = (float(value) - self.d0) / (self.d1 - self.d0)
        return self.r0 + t * (self.r1 - self.r0)

    def invert(self, pos) -> float:
        t = (float(pos) - self.r0) / (self.r1 - self.r0)
        return self.d0 + t * (self.d1 - self.d0)


class Band:
    """Discrete scale with padding, like d3.scaleBand."""

    def __init__(self, count: int, r0: float, r1: float, padding: float = 0.28):
        self.count = max(int(count), 1)
        self.r0, self.r1 = float(r0), float(r1)
        span = self.r1 - self.r0
        self.step = span / self.count
        self.bandwidth = max(self.step * (1.0 - padding), 1.0)
        self.offset = (self.step - self.bandwidth) / 2.0

    def __call__(self, index: int) -> float:
        return self.r0 + self.step * index + self.offset

    def center(self, index: int) -> float:
        return self(index) + self.bandwidth / 2.0


def nice_ticks(lo: float, hi: float, target: int = 5):
    """Round tick values covering [lo, hi]. Always includes a zero baseline
    when the data straddles or touches zero."""
    lo, hi = float(lo), float(hi)
    if hi == lo:
        hi = lo + 1.0
    raw = (hi - lo) / max(target, 1)
    magnitude = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for multiple in (1, 2, 2.5, 5, 10):
        step = magnitude * multiple
        if raw <= step:
            break
    start = math.floor(lo / step) * step
    end = math.ceil(hi / step) * step
    ticks, value, guard = [], start, 0
    while value <= end + step * 1e-9 and guard < 200:
        ticks.append(round(value, 10))
        value += step
        guard += 1
    return ticks


def extent(values, pad: float = 0.0, include_zero: bool = True):
    """Domain for a value axis.

    Padding must never carry the domain across zero: an all-positive series that
    picks up a −20K tick because of 6% headroom is stating something false about
    the data. So the padded bound is clamped back to zero on whichever side the
    data never crosses.
    """
    numbers = [float(v) for v in values if v is not None]
    if not numbers:
        return 0.0, 1.0
    raw_lo, raw_hi = min(numbers), max(numbers)
    lo, hi = (min(raw_lo, 0.0), max(raw_hi, 0.0)) if include_zero else (raw_lo, raw_hi)
    if lo == hi:
        hi = lo + 1.0
    span = hi - lo
    padded_lo, padded_hi = lo - span * pad, hi + span * pad
    if raw_lo >= 0:
        padded_lo = max(padded_lo, 0.0)
    if raw_hi <= 0:
        padded_hi = min(padded_hi, 0.0)
    return padded_lo, padded_hi


# ------------------------------------------------------------------- paths ---

def bar_path(x: float, y: float, w: float, h: float, r: float, end: str = "top") -> str:
    """Rectangle rounded ONLY at the data end, square at the baseline.

    `end` is the side the bar grows toward: top | bottom | left | right | none.
    """
    r = max(0.0, min(r, min(abs(w), abs(h)) / 2.0))
    if r <= 0.01 or end == "none":
        return f"M{num(x)},{num(y)}h{num(w)}v{num(h)}h{num(-w)}Z"
    X, Y, W, H = num, num, num, num
    if end == "top":
        return (f"M{X(x)},{Y(y + h)}V{Y(y + r)}A{num(r)},{num(r)} 0 0 1 {X(x + r)},{Y(y)}"
                f"H{X(x + w - r)}A{num(r)},{num(r)} 0 0 1 {X(x + w)},{Y(y + r)}"
                f"V{Y(y + h)}Z")
    if end == "bottom":
        return (f"M{X(x)},{Y(y)}V{Y(y + h - r)}A{num(r)},{num(r)} 0 0 0 {X(x + r)},{Y(y + h)}"
                f"H{X(x + w - r)}A{num(r)},{num(r)} 0 0 0 {X(x + w)},{Y(y + h - r)}"
                f"V{Y(y)}Z")
    if end == "right":
        return (f"M{X(x)},{Y(y)}H{X(x + w - r)}A{num(r)},{num(r)} 0 0 1 {X(x + w)},{Y(y + r)}"
                f"V{Y(y + h - r)}A{num(r)},{num(r)} 0 0 1 {X(x + w - r)},{Y(y + h)}"
                f"H{X(x)}Z")
    if end == "left":
        return (f"M{X(x + w)},{Y(y)}H{X(x + r)}A{num(r)},{num(r)} 0 0 0 {X(x)},{Y(y + r)}"
                f"V{Y(y + h - r)}A{num(r)},{num(r)} 0 0 0 {X(x + r)},{Y(y + h)}"
                f"H{X(x + w)}Z")
    return f"M{X(x)},{Y(y)}h{W(w)}v{H(h)}h{W(-w)}Z"


def rounded_rect(x, y, w, h, r) -> str:
    return f'<rect{attrs(x=x, y=y, width=w, height=h, rx=r, ry=r)}/>'


def polyline_path(points, close: bool = False) -> str:
    if not points:
        return ""
    head = f"M{num(points[0][0])},{num(points[0][1])}"
    rest = "".join(f"L{num(px)},{num(py)}" for px, py in points[1:])
    return head + rest + ("Z" if close else "")


def smooth_path(points, tension: float = 0.35, close: bool = False) -> str:
    """Catmull-Rom -> cubic bezier. Use sparingly: smoothing invents values
    between real data points, so it is wrong for anything read precisely."""
    if len(points) < 3:
        return polyline_path(points, close)
    out = [f"M{num(points[0][0])},{num(points[0][1])}"]
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3.0, p1[1] + (p2[1] - p0[1]) * tension / 3.0)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3.0, p2[1] - (p3[1] - p1[1]) * tension / 3.0)
        out.append(f"C{num(c1[0])},{num(c1[1])} {num(c2[0])},{num(c2[1])} {num(p2[0])},{num(p2[1])}")
    return "".join(out) + ("Z" if close else "")


def arc_path(cx, cy, r_outer, r_inner, a0, a1) -> str:
    """Donut/pie segment between angles in degrees, 0 = 12 o'clock, clockwise."""
    def point(radius, angle):
        rad = math.radians(angle - 90.0)
        return cx + radius * math.cos(rad), cy + radius * math.sin(rad)

    large = 1 if (a1 - a0) % 360 > 180 else 0
    x0, y0 = point(r_outer, a0)
    x1, y1 = point(r_outer, a1)
    if r_inner <= 0:
        return (f"M{num(cx)},{num(cy)}L{num(x0)},{num(y0)}"
                f"A{num(r_outer)},{num(r_outer)} 0 {large} 1 {num(x1)},{num(y1)}Z")
    x2, y2 = point(r_inner, a1)
    x3, y3 = point(r_inner, a0)
    return (f"M{num(x0)},{num(y0)}A{num(r_outer)},{num(r_outer)} 0 {large} 1 {num(x1)},{num(y1)}"
            f"L{num(x2)},{num(y2)}A{num(r_inner)},{num(r_inner)} 0 {large} 0 {num(x3)},{num(y3)}Z")


def ribbon_path(x0, y0a, y0b, x1, y1a, y1b) -> str:
    """Sankey link: a horizontal band with bezier sides."""
    mx = (x0 + x1) / 2.0
    return (f"M{num(x0)},{num(y0a)}"
            f"C{num(mx)},{num(y0a)} {num(mx)},{num(y1a)} {num(x1)},{num(y1a)}"
            f"L{num(x1)},{num(y1b)}"
            f"C{num(mx)},{num(y1b)} {num(mx)},{num(y0b)} {num(x0)},{num(y0b)}Z")


def arrow_marker(x, y, size, direction: str = "right", fill: str = "#000") -> str:
    s = size
    if direction == "right":
        pts = [(x, y - s / 2), (x + s * 0.85, y), (x, y + s / 2)]
    elif direction == "down":
        pts = [(x - s / 2, y), (x, y + s * 0.85), (x + s / 2, y)]
    elif direction == "left":
        pts = [(x, y - s / 2), (x - s * 0.85, y), (x, y + s / 2)]
    else:
        pts = [(x - s / 2, y), (x, y - s * 0.85), (x + s / 2, y)]
    return f'<path{attrs(d=polyline_path(pts, close=True), fill=fill)}/>'


# ------------------------------------------------------------------ canvas ---

class Canvas:
    """Accumulates SVG fragments and serializes a responsive, print-safe root.

    The root carries `viewBox` plus `width="100%"` and `height="auto"` styling so
    a block scales to whatever grid column it lands in without the caller having
    to know page geometry.
    """

    def __init__(self, width: float, height: float, theme=None, class_name: str = "ig-svg"):
        self.width = float(width)
        self.height = float(height)
        self.theme = theme
        self.class_name = class_name
        self.parts = []
        self.defs = []
        self._uid = 0

    def uid(self, prefix: str = "u") -> str:
        self._uid += 1
        return f"{prefix}{self._uid}"

    def add(self, fragment: str):
        if fragment:
            self.parts.append(fragment)
        return self

    def define(self, fragment: str):
        if fragment:
            self.defs.append(fragment)
        return self

    # -- shapes ------------------------------------------------------------

    def rect(self, x, y, w, h, fill, r=0, **kw):
        return self.add(f'<rect{attrs(x=x, y=y, width=max(w, 0), height=max(h, 0), rx=r or None, ry=r or None, fill=fill, **kw)}/>')

    def bar(self, x, y, w, h, fill, r=4, end="top", **kw):
        return self.add(f'<path{attrs(d=bar_path(x, y, w, h, r, end), fill=fill, **kw)}/>')

    def line(self, x1, y1, x2, y2, stroke, width=1, dash=None, cap="butt", **kw):
        return self.add(f'<line{attrs(x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke, stroke_width=width, stroke_dasharray=dash, stroke_linecap=cap, **kw)}/>')

    def path(self, d, fill="none", stroke=None, width=None, **kw):
        return self.add(f'<path{attrs(d=d, fill=fill, stroke=stroke, stroke_width=width, stroke_linejoin="round", stroke_linecap="round", **kw)}/>')

    def circle(self, cx, cy, r, fill, stroke=None, width=None, **kw):
        return self.add(f'<circle{attrs(cx=cx, cy=cy, r=r, fill=fill, stroke=stroke, stroke_width=width, **kw)}/>')

    def text(self, x, y, content, size=11, fill="#0b0b0b", weight=400, anchor="start",
             baseline=None, family=None, tracking=None, opacity=None, **kw):
        return self.add(
            f'<text{attrs(x=x, y=y, font_size=size, fill=fill, font_weight=weight, text_anchor=anchor, dominant_baseline=baseline, font_family=family, letter_spacing=tracking, opacity=opacity, **kw)}>{esc(content)}</text>'
        )

    def text_lines(self, x, y, lines, size=11, fill="#0b0b0b", weight=400, anchor="start",
                   line_height=1.4, **kw):
        for i, line in enumerate(lines):
            self.text(x, y + i * size * line_height, line, size=size, fill=fill,
                      weight=weight, anchor=anchor, **kw)
        return self

    def group(self, fragment, **kw):
        return self.add(f"<g{attrs(**kw)}>{fragment}</g>")

    # -- output ------------------------------------------------------------

    def render(self) -> str:
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(self.width)} {num(self.height)}" '
            f'class="{esc(self.class_name)}" role="img" preserveAspectRatio="xMidYMid meet" '
            f'style="width:100%;height:auto;display:block;overflow:visible">'
            f"{defs}{''.join(self.parts)}</svg>"
        )

    def __str__(self) -> str:
        return self.render()
