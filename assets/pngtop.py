#!/usr/bin/env python3
"""Keep the top N rows of a PNG. Standard library only.

Keeping a *prefix* of scanlines needs no defiltering: every PNG row filter
references only the row above it, which the prefix still contains. So the IDAT
stream can be sliced on row boundaries and recompressed as-is.
"""
import struct
import sys
import zlib


def chunks(blob):
    pos = 8
    while pos < len(blob):
        (length,) = struct.unpack(">I", blob[pos:pos + 4])
        kind = blob[pos + 4:pos + 8]
        data = blob[pos + 8:pos + 8 + length]
        yield kind, data
        pos += 12 + length


def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def crop_top(src, dst, keep):
    blob = open(src, "rb").read()
    assert blob[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"

    idat, ihdr = b"", None
    for kind, data in chunks(blob):
        if kind == b"IHDR":
            ihdr = data
        elif kind == b"IDAT":
            idat += data

    width, height, depth, colour = struct.unpack(">IIBB", ihdr[:10])
    if ihdr[10:13] != b"\x00\x00\x00":
        raise SystemExit("interlaced or non-default PNG, not handled")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colour]
    stride = 1 + (width * channels * depth + 7) // 8

    keep = min(keep, height)
    raw = zlib.decompress(idat)[:stride * keep]

    new_ihdr = struct.pack(">II", width, keep) + ihdr[8:]
    out = [blob[:8], chunk(b"IHDR", new_ihdr)]
    for kind, data in chunks(blob):
        if kind in (b"IHDR", b"IDAT", b"IEND"):
            continue
        out.append(chunk(kind, data))
    out.append(chunk(b"IDAT", zlib.compress(raw, 9)))
    out.append(chunk(b"IEND", b""))
    open(dst, "wb").write(b"".join(out))
    return width, keep


if __name__ == "__main__":
    src, dst, keep = sys.argv[1], sys.argv[2], int(sys.argv[3])
    w, h = crop_top(src, dst, keep)
    print(f"{dst}  {w}x{h}")
