#!/usr/bin/env python3
"""Turn a source document into a normalized fact ledger, plus a first pass at
which visual forms its content can support.

    python3 scripts/extract_source.py report.pdf -o out/ledger.json

What comes out is evidence, not a design. The ledger records what is *in* the
source, headings, tables, numbers with the sentence they came from, dates,
sequences, and `candidates` lists forms the data could take, each with the
evidence that suggested it. Choosing among them is a judgement call made
against references/choosing-a-visual.md, never a lookup.

Two rules this file exists to enforce:

* **Every number keeps its sentence.** A figure without its context is how an
  infographic ends up asserting something the source never said.
* **Nothing is invented.** If a total is not in the source, the ledger does not
  compute one and present it as a fact; derived values are marked `derived`.

Supported: .txt .md .markdown .csv .tsv .json .html .htm .pdf .docx, or stdin.
"""

from __future__ import annotations

import argparse
import csv
import html as html_mod
import io
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

# --------------------------------------------------------------- readers ----


def read_txt(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def read_pdf(path):
    if not shutil.which("pdftotext"):
        raise SystemExit(
            "[extract] reading PDF needs `pdftotext` (poppler). "
            "Install it (brew install poppler / apt install poppler-utils), "
            "or convert the file to text first."
        )
    out = subprocess.run(["pdftotext", "-layout", "-nopgbrk", path, "-"],
                         capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise SystemExit(f"[extract] pdftotext failed: {out.stderr.strip()}")
    return out.stdout


def read_docx(path):
    """DOCX is a zip of XML, no third-party library needed."""
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"</w:tr>", "\n", xml)
    xml = re.sub(r"</w:tc>", "\t", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    return html_mod.unescape(text)


def read_html(path):
    raw = read_txt(path)
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)</(p|div|li|tr|h[1-6]|section)>", "\n", raw)
    raw = re.sub(r"(?i)<br[^>]*/?>", "\n", raw)
    raw = re.sub(r"(?i)</t[dh]>", "\t", raw)
    return html_mod.unescape(re.sub(r"<[^>]+>", "", raw))


def read_delimited(path, delimiter):
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
        rows = [r for r in csv.reader(fh, delimiter=delimiter) if any(c.strip() for c in r)]
    return rows


def read_json_source(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------- parsing ----

NUM_RE = re.compile(
    r"(?<![\w.])"
    r"(?P<currency>[$€£¥])?\s?"
    r"(?P<value>-?\d{1,3}(?:[, \s]\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?)"
    r"\s?(?P<suffix>%|percent|pp|bps|[kKmMbB](?![\w])|million|billion|thousand|"
    r"x(?![\w])|hours?|days?|weeks?|months?|years?|min(?:utes?)?|s(?:ec(?:onds?)?)?)?"
)

DATE_RE = re.compile(
    r"\b((?:19|20)\d{2}(?:-\d{2}(?:-\d{2})?)?"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(?:19|20)?\d{2,4}"
    r"|Q[1-4]\s?(?:19|20)?\d{2,4})\b"
)

MULTIPLIERS = {"k": 1e3, "m": 1e6, "b": 1e9, "thousand": 1e3, "million": 1e6, "billion": 1e9}

SEQUENCE_HINTS = re.compile(
    r"\b(first|second|third|then|next|finally|step\s*\d|stage\s*\d|phase\s*\d|"
    r"begins?|followed by|afterwards?|subsequently)\b", re.I)
CAUSE_HINTS = re.compile(r"\b(because|therefore|as a result|leads? to|causes?|so that|hence)\b", re.I)
CONTRAST_HINTS = re.compile(r"\b(versus|vs\.?|whereas|but|however|in contrast|instead of|rather than)\b", re.I)
PART_HINTS = re.compile(r"\b(of (?:all|the total)|share of|makes? up|accounts? for|out of|breakdown|split)\b", re.I)
TREND_HINTS = re.compile(r"\b(grew|fell|rose|declined|increased|decreased|since|between \d|over the (?:past|last)|trend|year[- ]on[- ]year|month[- ]on[- ]month)\b", re.I)
CYCLE_HINTS = re.compile(r"\b(cycle|loop|iterat|feedback|continuous|repeats?|virtuous|vicious)\b", re.I)
HIERARCHY_HINTS = re.compile(r"\b(consists? of|composed of|made up of|sub-?(?:system|category)|reports? to|parent|child|contains?)\b", re.I)
COMPARE_HINTS = re.compile(r"\b(compared (?:to|with)|relative to|outperform|cheaper|faster|slower|better than|worse than)\b", re.I)


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(\[])", text)
    return [p.strip() for p in parts if p.strip()]


def parse_number(match):
    raw_value = match.group("value").replace(",", "").replace(" ", "").replace(" ", "")
    try:
        value = float(raw_value)
    except ValueError:
        return None
    suffix = (match.group("suffix") or "").lower()
    unit = ""
    if suffix in ("%", "percent"):
        unit = "%"
    elif suffix in ("pp", "bps"):
        unit = suffix
    elif suffix in MULTIPLIERS:
        value *= MULTIPLIERS[suffix]
        unit = "count"
    elif suffix:
        unit = suffix
    if match.group("currency"):
        unit = unit or "currency"
    return {
        "raw": match.group(0).strip(),
        "value": value,
        "unit": unit,
        "currency": match.group("currency") or "",
    }


def extract_numbers(text, limit=400):
    found = []
    for sentence in split_sentences(text):
        if len(sentence) > 600:
            continue
        for match in NUM_RE.finditer(sentence):
            parsed = parse_number(match)
            if not parsed:
                continue
            parsed["context"] = sentence.strip()
            found.append(parsed)
            if len(found) >= limit:
                return found
    return found


def extract_headings(text):
    sections, current = [], None
    for line in text.splitlines():
        stripped = line.strip()
        md = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        setext = None
        if md:
            level, title = len(md.group(1)), md.group(2).strip()
        elif (stripped and len(stripped) < 90 and stripped == stripped.upper()
              and re.search(r"[A-Z]{3}", stripped) and not stripped.endswith(".")):
            level, title = 2, stripped.title()
        elif re.match(r"^\d+(\.\d+)*[.)]\s+\S", stripped) and len(stripped) < 90:
            level, title = 3, stripped
        else:
            if current is not None and stripped:
                current["text"].append(stripped)
            elif stripped:
                current = {"heading": None, "level": 0, "text": [stripped]}
                sections.append(current)
            continue
        current = {"heading": title, "level": level, "text": []}
        sections.append(current)
    for section in sections:
        section["text"] = " ".join(section["text"]).strip()
    return [s for s in sections if s["heading"] or s["text"]]


def looks_numeric(value):
    if value is None:
        return False
    text = str(value).strip().replace(",", "").replace("%", "").replace("$", "") \
        .replace("€", "").replace("£", "")
    if not text or text in ("-", ", ", "n/a", "N/A"):
        return False
    try:
        float(text)
        return True
    except ValueError:
        return False


def to_number(value):
    text = str(value).strip().replace(",", "").replace("%", "").replace("$", "") \
        .replace("€", "").replace("£", "").replace(" ", "")
    try:
        return float(text)
    except ValueError:
        return None


def extract_tables_from_text(text):
    """Recovers markdown pipe tables and tab/multi-space aligned blocks."""
    tables = []
    lines = text.splitlines()

    # markdown pipe tables
    i = 0
    while i < len(lines):
        if lines[i].count("|") >= 2 and i + 1 < len(lines) and re.match(
                r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows, j = [], i + 2
            while j < len(lines) and lines[j].count("|") >= 2:
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            if rows:
                tables.append({"columns": header, "rows": rows, "origin": "markdown"})
            i = j
            continue
        i += 1

    # tab or 2+ space aligned blocks
    block = []
    for line in lines + [""]:
        if "\t" in line or re.search(r"\S {2,}\S", line):
            cells = [c.strip() for c in re.split(r"\t|\s{2,}", line.strip()) if c.strip()]
            if len(cells) >= 2:
                block.append(cells)
                continue
        if len(block) >= 3:
            widths = {len(r) for r in block}
            if len(widths) <= 2:
                width = max(widths)
                normalized = [r + [""] * (width - len(r)) for r in block]
                numeric_rows = sum(1 for r in normalized[1:] if any(looks_numeric(c) for c in r))
                if numeric_rows >= 2:
                    tables.append({"columns": normalized[0], "rows": normalized[1:],
                                   "origin": "aligned-text"})
        block = []
    return tables


# ------------------------------------------------------------ candidates ----

TIME_HEADER = re.compile(
    r"^(19|20)\d{2}$|^(Q[1-4]|H[12])[\s-]?(19|20)?\d{0,4}$|"
    r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", re.I)

BEFORE_AFTER = (
    ("before", "after"), ("start", "end"), ("old", "new"), ("was", "now"),
    ("baseline", "current"), ("pre", "post"), ("from", "to"), ("previous", "current"),
    ("2023", "2024"), ("last year", "this year"),
)


def table_candidates(table, index):
    """Suggest forms for one recovered table, each with its evidence."""
    columns = [str(c).strip() for c in table["columns"]]
    rows = table["rows"]
    out = []
    numeric_cols = [
        i for i in range(len(columns))
        if sum(1 for r in rows if i < len(r) and looks_numeric(r[i])) >= max(2, len(rows) * 0.6)
    ]
    label_col = next((i for i in range(len(columns)) if i not in numeric_cols), None)
    if label_col is None or not numeric_cols:
        return out

    labels = [str(r[label_col]) for r in rows if label_col < len(r)]
    ref = f"table[{index}]"

    time_like = sum(1 for i in numeric_cols if TIME_HEADER.match(columns[i])) >= max(2, len(numeric_cols) * 0.6)

    if len(numeric_cols) == 1:
        values = [to_number(r[numeric_cols[0]]) for r in rows if numeric_cols[0] < len(r)]
        values = [v for v in values if v is not None]
        total = sum(values)
        out.append({
            "form": "bar", "ref": ref, "confidence": "high",
            "why": f"one numeric column ({columns[numeric_cols[0]]}) across "
                   f"{len(labels)} named categories, a magnitude comparison",
            "watch": "sort by value unless the category order is itself meaningful",
        })
        if 97 <= total <= 103 and all(0 <= v <= 100 for v in values):
            out.append({
                "form": "share_bar", "ref": ref, "confidence": "high",
                "why": f"the column sums to {total:.0f}, these are shares of one whole",
                "alternatives": ["unit", "donut"],
                "watch": "confirm the parts are mutually exclusive before showing a whole",
            })
        if len(labels) > 12:
            out.append({"form": "lollipop", "ref": ref, "confidence": "medium",
                        "why": f"{len(labels)} categories, solid bars would flood the page"})
        if len(values) >= 3 and all(v >= 0 for v in values) and \
                values == sorted(values, reverse=True):
            out.append({"form": "funnel", "ref": ref, "confidence": "medium",
                        "why": "values fall monotonically across ordered rows, possibly stages",
                        "watch": "only a funnel if the same population moves between stages"})
        if any(v < 0 for v in values):
            out.append({"form": "diverging", "ref": ref, "confidence": "high",
                        "why": "values sit on both sides of zero"})

    elif time_like:
        out.append({
            "form": "line", "ref": ref, "confidence": "high",
            "why": f"{len(numeric_cols)} columns read as periods "
                   f"({', '.join(columns[i] for i in numeric_cols[:4])}…), a trend",
            "watch": "one axis only; if the series have different scales, index them to 100",
        })
        if len(numeric_cols) == 2:
            out.append({"form": "slope", "ref": ref, "confidence": "medium",
                        "why": "exactly two periods, a slope shows rank change directly"})

    else:
        header_pair = None
        lowered = [c.lower() for c in columns]
        for a, b in BEFORE_AFTER:
            ia = next((i for i, c in enumerate(lowered) if a in c), None)
            ib = next((i for i, c in enumerate(lowered) if b in c), None)
            if ia is not None and ib is not None and ia in numeric_cols and ib in numeric_cols:
                header_pair = (columns[ia], columns[ib])
                break
        if header_pair or len(numeric_cols) == 2:
            out.append({
                "form": "dumbbell", "ref": ref, "confidence": "high" if header_pair else "medium",
                "why": (f"columns {header_pair[0]!r} and {header_pair[1]!r} are a before/after pair"
                        if header_pair else "two numeric columns per item, likely two states"),
                "alternatives": ["slope"],
            })
        out.append({
            "form": "column", "ref": ref, "confidence": "medium",
            "why": f"{len(numeric_cols)} measures across {len(labels)} categories, grouped columns",
            "watch": "grouped bars past 3 series stop being comparable; consider small multiples",
        })
        if len(numeric_cols) >= 4 and len(labels) >= 4:
            out.append({"form": "heatmap", "ref": ref, "confidence": "medium",
                        "why": f"a {len(labels)}x{len(numeric_cols)} numeric grid reads better as a heatmap"})
        if all(looks_numeric(r[i]) for r in rows[:3] for i in numeric_cols) and len(numeric_cols) > 5:
            out.append({"form": "table", "ref": ref, "confidence": "medium",
                        "why": "many measures per row, exact values matter more than shape"})
    return out


def text_candidates(text, numbers, dates):
    out = []
    sentences = split_sentences(text)

    dated = [s for s in sentences if DATE_RE.search(s)]
    if len(dated) >= 3:
        out.append({"form": "timeline", "ref": "prose", "confidence": "high",
                    "why": f"{len(dated)} sentences carry an explicit date, an event sequence",
                    "sample": dated[:3]})

    seq = [s for s in sentences if SEQUENCE_HINTS.search(s)]
    if len(seq) >= 3:
        out.append({"form": "process", "ref": "prose", "confidence": "high",
                    "why": f"{len(seq)} sentences use ordering language (first / then / step N)",
                    "sample": seq[:3]})
    if CYCLE_HINTS.search(text) and len(seq) >= 3:
        out.append({"form": "cycle", "ref": "prose", "confidence": "medium",
                    "why": "ordering language plus loop vocabulary, check the last step feeds the first"})

    contrasts = [s for s in sentences if CONTRAST_HINTS.search(s)]
    if len(contrasts) >= 2:
        out.append({"form": "comparison", "ref": "prose", "confidence": "medium",
                    "why": f"{len(contrasts)} sentences frame one option against another",
                    "alternatives": ["matrix", "checklist"], "sample": contrasts[:2]})

    if HIERARCHY_HINTS.search(text):
        out.append({"form": "tree", "ref": "prose", "confidence": "medium",
                    "why": "containment language (consists of / made up of / reports to)"})

    ratios = [n for n in numbers if n["unit"] == "%"]
    if ratios:
        small = [n for n in ratios if n["value"] <= 100]
        if small:
            out.append({"form": "unit", "ref": "prose", "confidence": "medium",
                        "why": f"{len(small)} percentages in prose, a waffle keeps 'x in 100' countable",
                        "alternatives": ["share_bar", "stat"],
                        "sample": [n["context"] for n in small[:2]]})

    standout = [n for n in numbers if n["value"] >= 1000 or n["unit"] in ("%", "x")]
    if standout:
        out.append({"form": "stat", "ref": "prose", "confidence": "high",
                    "why": "single headline figures stated in prose deserve stat tiles, "
                           "not one-bar charts",
                    "sample": [f'{n["raw"]}, {n["context"][:120]}' for n in standout[:3]]})

    if TREND_HINTS.search(text):
        out.append({"form": "line", "ref": "prose", "confidence": "low",
                    "why": "movement vocabulary (grew / fell / since), look for the "
                           "underlying series, and ask for it if the source omits it"})

    if CAUSE_HINTS.search(text):
        out.append({"form": "process", "ref": "prose", "confidence": "low",
                    "why": "causal language, a chain diagram may explain it better than prose"})

    # Allow the markdown furniture these headings normally wear: #, *, -, **.
    lead = r"(?:[#*\-\s]|\*\*)*"
    pros = re.findall(rf"(?im)^{lead}(?:pros?|benefits?|advantages?|upsides?|do)\b.*$", text)
    cons = re.findall(rf"(?im)^{lead}(?:cons?|risks?|drawbacks?|downsides?|don'?ts?)\b.*$", text)
    if pros and cons:
        out.append({"form": "checklist", "ref": "prose", "confidence": "medium",
                    "why": "the source already separates upsides from downsides"})
    return out


def rank(candidates):
    weight = {"high": 0, "medium": 1, "low": 2}
    return sorted(candidates, key=lambda c: (weight.get(c.get("confidence"), 3), c["form"]))


# ---------------------------------------------------------------- driver ----

def load(path):
    if path == "-":
        return "stdin", sys.stdin.read(), []
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".markdown", ".rst", ".log"):
        return ext.lstrip("."), read_txt(path), []
    if ext == ".pdf":
        return "pdf", read_pdf(path), []
    if ext == ".docx":
        return "docx", read_docx(path), []
    if ext in (".html", ".htm"):
        return "html", read_html(path), []
    if ext in (".csv", ".tsv"):
        rows = read_delimited(path, "\t" if ext == ".tsv" else ",")
        table = {"columns": rows[0] if rows else [], "rows": rows[1:], "origin": ext.lstrip(".")}
        flat = "\n".join("\t".join(r) for r in rows)
        return ext.lstrip("."), flat, [table]
    if ext == ".json":
        data = read_json_source(path)
        tables = []
        if isinstance(data, list) and data and isinstance(data[0], dict):
            columns = list(data[0].keys())
            tables.append({"columns": columns,
                           "rows": [[str(row.get(c, "")) for c in columns] for row in data],
                           "origin": "json"})
        return "json", json.dumps(data, indent=2, ensure_ascii=False), tables
    return "text", read_txt(path), []


def build_ledger(path):
    kind, text, tables = load(path)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    tables = tables + extract_tables_from_text(text)
    numbers = extract_numbers(text)
    dates = sorted({m.group(1) for m in DATE_RE.finditer(text)})
    sections = extract_headings(text)

    candidates = []
    for i, table in enumerate(tables):
        candidates.extend(table_candidates(table, i))
    candidates.extend(text_candidates(text, numbers, dates))

    return {
        "source": {
            "path": path,
            "kind": kind,
            "chars": len(text),
            "words": len(text.split()),
            "sections": len(sections),
            "tables": len(tables),
            "numbers": len(numbers),
        },
        "sections": sections[:120],
        "tables": tables,
        "numbers": numbers,
        "dates": dates,
        "candidates": rank(candidates),
        "text": text,
    }


def summarize(ledger):
    s = ledger["source"]
    lines = [
        f"source     {s['path']}  ({s['kind']}, {s['words']:,} words)",
        f"structure  {s['sections']} sections · {s['tables']} tables · "
        f"{s['numbers']} numbers · {len(ledger['dates'])} dates",
        "",
        "candidate forms (evidence, not a decision, choose with references/choosing-a-visual.md):",
    ]
    if not ledger["candidates"]:
        lines.append("  none detected. The source may be pure narrative; consider process, "
                     "comparison, definitions, or a concept diagram.")
    for c in ledger["candidates"]:
        lines.append(f"  [{c['confidence']:<6}] {c['form']:<12} {c['ref']:<10} {c['why']}")
        if c.get("alternatives"):
            lines.append(f"                                    or: {', '.join(c['alternatives'])}")
        if c.get("watch"):
            lines.append(f"                                    watch: {c['watch']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Extract a fact ledger from a document.")
    parser.add_argument("path", help="source file, or - for stdin")
    parser.add_argument("-o", "--out", help="write the full ledger JSON here")
    parser.add_argument("--json", action="store_true", help="print the ledger instead of the summary")
    parser.add_argument("--no-text", action="store_true", help="omit the full text from the ledger")
    args = parser.parse_args()

    ledger = build_ledger(args.path)
    if args.no_text:
        ledger.pop("text", None)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(ledger, fh, indent=2, ensure_ascii=False)
        print(f"[extract] wrote {args.out}")
    if args.json:
        print(json.dumps(ledger, indent=2, ensure_ascii=False))
    else:
        print(summarize(ledger))


if __name__ == "__main__":
    main()
