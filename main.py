#!/usr/bin/env python3
"""Entrypoint for the news-image-20261119 entry.

The repository holds one finished front page, entry.png, drawn by
render.py from the news of Thursday 19 November 2026. This program is the
part the grader runs: it checks the image is a whole, in-limits PNG and
then copies it to the output directory as entry.png.

Checks, in order:
  * the file exists and is at most 1 MiB
  * the first bytes are the PNG signature
  * the chunk walk reaches IEND with every chunk length in bounds and
    nothing at all after IEND
  * IHDR says the picture is at most 1024 x 1024

After copying, the output is read back and its SHA-256 compared with the
repository file, so a short or corrupted copy fails the run instead of
quietly grading the wrong bytes.
"""

import binascii
import hashlib
import os
import struct
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def read_chunks(data):
    """Yield (type, payload) for each PNG chunk, or raise ValueError.

    Every chunk's stored CRC-32 is checked against the bytes it covers,
    so a chunk can be the right length and still fail as corrupt.
    """
    pos = len(PNG_SIGNATURE)
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError("truncated chunk header")
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        end = pos + 8 + length + 4  # payload plus its CRC
        if end > len(data):
            raise ValueError(f"chunk {kind!r} runs past the end of the file")
        payload = data[pos + 8:pos + 8 + length]
        (stored_crc,) = struct.unpack(">I", data[end - 4:end])
        if binascii.crc32(kind + payload) & 0xFFFFFFFF != stored_crc:
            raise ValueError(f"chunk {kind!r} fails its CRC-32 check")
        yield kind, payload
        pos = end
        if kind == b"IEND":
            if pos != len(data):
                raise ValueError("trailing data after PNG IEND")
            return
    raise ValueError("no IEND chunk found")


def validate(data):
    if len(data) > MAX_BYTES:
        raise ValueError(f"entry.png is {len(data)} bytes, over the 1 MiB cap")
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("entry.png does not start with the PNG signature")
    chunks = list(read_chunks(data))
    if not chunks or chunks[0][0] != b"IHDR":
        raise ValueError("first chunk is not IHDR")
    width, height = struct.unpack(">II", chunks[0][1][:8])
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"entry.png is {width}x{height}, over the 1024 px cap")
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        return fail("entry.png is missing from the repository root")
    with open(source, "rb") as handle:
        data = handle.read()
    try:
        width, height = validate(data)
    except ValueError as exc:
        return fail(str(exc))

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)

    with open(target, "rb") as handle:
        written = handle.read()
    digest = hashlib.sha256(data).hexdigest()
    if hashlib.sha256(written).hexdigest() != digest:
        return fail("read-back of the copied file does not match the original")
    print(f"entry.png: PNG {width}x{height}, {len(data)} bytes, sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
