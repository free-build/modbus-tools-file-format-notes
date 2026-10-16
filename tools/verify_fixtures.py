from __future__ import annotations

import hashlib
import struct
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"

EXPECTED_BINARY = {
    "modbus-slave-7.3.0-build-1402.mbs": 7300,
    "modbus-slave-10.0.0-build-2493.mbs": 10000,
    "modbus-poll-6.4.2-build-964.mbp": 6402,
}
XML_FIXTURE = "modbus-poll-13.2.1-build-2558.mbp"


def read_manifest() -> dict[str, str]:
    result = {}
    for line in (FIXTURES / "MANIFEST.sha256").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        result[name] = digest
    return result


def main() -> None:
    manifest = read_manifest()
    expected_names = set(EXPECTED_BINARY) | {XML_FIXTURE}
    if set(manifest) != expected_names:
        raise SystemExit("manifest file list does not match the expected fixtures")

    for name, signature in EXPECTED_BINARY.items():
        data = (FIXTURES / name).read_bytes()
        if len(data) < 4 or struct.unpack_from("<I", data, 0)[0] != signature:
            raise SystemExit(f"invalid signature: {name}")

    xml_root = ET.parse(FIXTURES / XML_FIXTURE).getroot()
    if xml_root.tag != "ModbusPoll":
        raise SystemExit("invalid Modbus Poll XML root")
    version = xml_root.find("Version")
    if version is None or version.attrib != {
        "major": "13",
        "minor": "2",
        "patch": "1",
        "build": "2558",
    }:
        raise SystemExit("unexpected Modbus Poll XML version")

    for name, expected_hash in manifest.items():
        actual_hash = hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise SystemExit(f"SHA-256 mismatch: {name}")

    print(f"OK: verified {len(manifest)} fixtures")


if __name__ == "__main__":
    main()

