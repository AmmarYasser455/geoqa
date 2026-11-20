"""The CLI must not crash on consoles that can't encode emoji (default Windows console)."""

import io

from geoqa.cli import _make_console_safe


def _stream(encoding):
    raw = io.BytesIO()
    return raw, io.TextIOWrapper(raw, encoding=encoding, newline="")


def test_cp1252_console_replaces_emoji_instead_of_crashing():
    raw, stream = _stream("cp1252")
    _make_console_safe(stream)
    stream.write("\U0001f30d GeoQA — Quality checks")
    stream.flush()
    assert raw.getvalue() == "? GeoQA — Quality checks".encode("cp1252")


def test_utf8_console_is_left_alone():
    raw, stream = _stream("utf-8")
    _make_console_safe(stream)
    stream.write("\U0001f30d")
    stream.flush()
    assert raw.getvalue() == "\U0001f30d".encode("utf-8")
