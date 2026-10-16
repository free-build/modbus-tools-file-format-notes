from __future__ import annotations

import argparse
import hashlib
import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path


MAX_FILE_SIZE = 64 * 1024 * 1024
BINARY_SIGNATURES = {
    7300: ("Modbus Slave", "7.x binary"),
    10000: ("Modbus Slave", "10.x binary"),
    6402: ("Modbus Poll", "6.4.2 binary"),
}


class FormatError(ValueError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect(path: Path) -> dict[str, object]:
    size = path.stat().st_size
    if size == 0:
        raise FormatError("empty file")
    if size > MAX_FILE_SIZE:
        raise FormatError(f"file exceeds {MAX_FILE_SIZE} bytes")

    data = path.read_bytes()
    stripped = data.lstrip(b"\xef\xbb\xbf\x20\x09\x0d\x0a")
    result: dict[str, object] = {
        "path": str(path),
        "size": size,
        "sha256": sha256(path),
    }

    if stripped.startswith(b"<?xml") or stripped.startswith(b"<ModbusPoll"):
        upper_prefix = stripped[:4096].upper()
        if b"<!DOCTYPE" in upper_prefix or b"<!ENTITY" in upper_prefix:
            raise FormatError("DTD and entity declarations are not accepted")
        try:
            root = ET.fromstring(stripped)
        except ET.ParseError as exc:
            raise FormatError(f"invalid XML: {exc}") from exc
        if root.tag != "ModbusPoll":
            raise FormatError(f"unexpected XML root: {root.tag}")
        version = root.find("Version")
        if version is None:
            raise FormatError("missing Version element")
        result.update(
            application="Modbus Poll",
            container="xml",
            format="13.x XML",
            version={
                key: version.attrib.get(key)
                for key in ("major", "minor", "patch", "build")
            },
        )
        return result

    if len(data) < 4:
        raise FormatError("truncated binary header")
    signature = struct.unpack_from("<I", data, 0)[0]
    known = BINARY_SIGNATURES.get(signature)
    if known is None:
        raise FormatError(f"unknown binary signature: {signature}")
    application, format_name = known
    result.update(
        application=application,
        container="binary",
        format=format_name,
        signature=signature,
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Identify a Modbus Poll/Slave project file")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(detect(args.file), ensure_ascii=False, indent=2))
    except (OSError, FormatError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

