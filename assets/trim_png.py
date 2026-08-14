#!/usr/bin/env python3
"""Trim the blank tail off a rasterised page, keeping its ground colour.

A README image is a fixed frame and a paginated page is a fixed height, so the
last sheet of a document, and any sheet whose next row would not fit, arrives
with a band of empty page under the content. Left alone it reads as an image
that failed to load. `sips --cropOffset` is centre-relative and crops the wrong
thing here, so this does it directly.

Standard library only. pdftoppm writes 8-bit non-interlaced RGB, which is the
only case handled: anything else is left alone rather than silently mangled.

The threshold is deliberately not "not white". Every page in this kit is drawn
on a near-white ground (#f9f9f7) and most cards on another (#fcfcfb), so a test
for pure white finds content in the margin. What it looks for is a pixel darker
than any of those grounds, which is ink.
"""
import struct
import sys
import zlib

INK = 235          # a channel below this is a mark, not a page ground
PAD = 28           # rows of page left under the last mark, so it can breathe


def chunks(blob):
    pos = 8
    while pos < len(blob):
        (length,) = struct.unpack(">I", blob[pos:pos + 4])
        kind = blob[pos + 4:pos + 8]
        yield kind, blob[pos + 8:pos + 8 + length]
        pos += 8 + length + 4


def chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))


def unfilter(raw, width, height, stride, bpp):
    """PNG scanline defiltering, the five filter types, in place."""
    out = bytearray(height * stride)
    prev = bytearray(stride)
    pos = 0
    for y in range(height):
        kind = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if kind == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif kind == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif kind == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif kind == 4:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                up = prev[i]
                upleft = prev[i - bpp] if i >= bpp else 0
                p = left + up - upleft
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - upleft)
                best = left if (pa <= pb and pa <= pc) else (up if pb <= pc else upleft)
                line[i] = (line[i] + best) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return out


def trim(src, dst=None):
    blob = open(src, "rb").read()
    header, data = None, bytearray()
    for kind, payload in chunks(blob):
        if kind == b"IHDR":
            header = payload
        elif kind == b"IDAT":
            data += payload
    width, height, depth, colour, _c, _f, interlace = struct.unpack(">IIBBBBB", header)
    if depth != 8 or interlace or colour not in (2, 6):
        return None
    bpp = 3 if colour == 2 else 4
    stride = width * bpp
    pixels = unfilter(zlib.decompress(bytes(data)), width, height, stride, bpp)

    bottom = 0
    for y in range(height - 1, -1, -1):
        row = pixels[y * stride:(y + 1) * stride]
        if any(row[i] < INK for i in range(0, stride, bpp)):
            bottom = y
            break
    keep = min(height, bottom + PAD)
    if keep >= height:
        return height

    body = bytearray()
    for y in range(keep):
        body.append(0)
        body += pixels[y * stride:(y + 1) * stride]
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", width, keep, 8, colour, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(bytes(body), 9))
    out += chunk(b"IEND", b"")
    open(dst or src, "wb").write(out)
    return keep


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(path, trim(path))
