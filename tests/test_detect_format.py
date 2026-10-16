from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from detect_format import FormatError, detect  # noqa: E402


class DetectFormatTests(unittest.TestCase):
    def test_all_published_fixtures(self) -> None:
        expected = {
            "modbus-slave-7.3.0-build-1402.mbs": ("Modbus Slave", "binary", 7300),
            "modbus-slave-10.0.0-build-2493.mbs": ("Modbus Slave", "binary", 10000),
            "modbus-poll-6.4.2-build-964.mbp": ("Modbus Poll", "binary", 6402),
        }
        for name, (application, container, signature) in expected.items():
            result = detect(ROOT / "fixtures" / name)
            self.assertEqual(application, result["application"])
            self.assertEqual(container, result["container"])
            self.assertEqual(signature, result["signature"])

        xml_result = detect(ROOT / "fixtures" / "modbus-poll-13.2.1-build-2558.mbp")
        self.assertEqual("Modbus Poll", xml_result["application"])
        self.assertEqual("xml", xml_result["container"])
        self.assertEqual("13", xml_result["version"]["major"])
        self.assertEqual("2558", xml_result["version"]["build"])

    def assert_rejected(self, content: bytes) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.mbp"
            path.write_bytes(content)
            with self.assertRaises(FormatError):
                detect(path)

    def test_empty_file_is_rejected(self) -> None:
        self.assert_rejected(b"")

    def test_truncated_binary_is_rejected(self) -> None:
        self.assert_rejected(b"\x02\x19\x00")

    def test_unknown_signature_is_rejected(self) -> None:
        self.assert_rejected(b"\xff\xff\xff\xff")

    def test_wrong_xml_root_is_rejected(self) -> None:
        self.assert_rejected(b'<?xml version="1.0"?><Other/>')

    def test_xml_without_version_is_rejected(self) -> None:
        self.assert_rejected(b'<?xml version="1.0"?><ModbusPoll/>')

    def test_xml_dtd_is_rejected(self) -> None:
        self.assert_rejected(
            b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY x "x">]><ModbusPoll><Version/></ModbusPoll>'
        )


if __name__ == "__main__":
    unittest.main()

