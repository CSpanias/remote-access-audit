import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from remote_access_audit import cli
from remote_access_audit.exporters.sureformat import export_sureformat
from remote_access_audit.models import (
    AssessmentResults,
    Finding,
    RemoteAccessPlatform,
    ReviewContext,
)


def sample_results():
    return AssessmentResults(
        context=ReviewContext(
            client_name="Example",
            remote_access_solution=RemoteAccessPlatform.ALWAYS_ON_VPN,
        ),
        findings=[
            Finding(
                finding_id="weak-cryptography", title="Weak crypto", theme="Crypto",
                expected_value="Strong", description="Weak <crypto> & protocols",
                commentary="", solution="",
            ),
            Finding(
                finding_id="user-mfa-not-enforced", title="No MFA", theme="Auth",
                expected_value="MFA", description="MFA disabled",
                commentary="", solution="",
            ),
        ],
    )


class SureFormatTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=os.environ["TEMP"])
        self.old_cwd = os.getcwd()
        os.chdir(self.directory.name)
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(os.chdir, self.old_cwd)

    def test_cli_exports_xml_and_retains_notes(self):
        with patch("sys.argv", ["remote-access-audit", "--csacyber", "--hostname", "vpn.test"]), \
             patch.object(cli, "run_assessment", return_value=sample_results()), \
             patch.object(cli, "export_markdown") as markdown, \
             patch("remote_access_audit.exporters.sureformat.console.print") as warning:
            cli.main()
        root = ET.parse("remote-access-review-findings.xml").getroot()
        item = root.find("item")
        service = item.find("./services/service")
        findings = service.findall("./vulnerabilities/vulnerability")
        self.assertEqual(root.attrib, {"source": "SureFormat", "version": "1.0.0"})
        self.assertEqual(item.attrib, {"ipaddress": "", "hostname": "vpn.test"})
        self.assertEqual(service.attrib, {"name": "", "port": "", "protocol": "tcp"})
        self.assertEqual([f.attrib["id"] for f in findings], ["SC-9941", "SC-1520"])
        self.assertEqual(findings[1].findtext("information"), "Weak <crypto> & protocols")
        self.assertTrue(
            any("user-mfa-not-enforced" in str(call) for call in warning.call_args_list)
        )
        self.assertFalse(os.path.exists("remote-access-review-findings.json"))
        with open("remote-access-review-notes.json", encoding="utf-8") as file:
            self.assertEqual(json.load(file), {"responses": []})
        markdown.assert_called_once()

    def test_default_cli_keeps_generic_json(self):
        with patch("sys.argv", ["remote-access-audit"]), \
             patch.object(cli, "run_assessment", return_value=sample_results()), \
             patch.object(cli, "export_markdown"):
            cli.main()
        with open("remote-access-review-findings.json", encoding="utf-8") as file:
            findings = json.load(file)["findings"]
        self.assertEqual([f["id"] for f in findings], [
            "remote-access-audit", "weak-cryptography", "user-mfa-not-enforced"
        ])
        self.assertFalse(os.path.exists("remote-access-review-findings.xml"))

    def test_hostname_validation_occurs_before_assessment(self):
        for args in (
            ["--csacyber"], ["--csacyber", "--hostname", "  "], ["--hostname", "vpn.test"]
        ):
            with self.subTest(args=args), patch("sys.argv", ["remote-access-audit", *args]), \
                 patch.object(cli, "run_assessment") as assessment, \
                 patch("sys.stderr"):
                with self.assertRaises(SystemExit):
                    cli.main()
                assessment.assert_not_called()

    def test_unmapped_id_is_not_written(self):
        with patch("remote_access_audit.exporters.sureformat.console.print") as warning:
            export_sureformat([{"id": "unknown", "description": "omitted"}], "host", "test.xml")
        root = ET.parse("test.xml").getroot()
        self.assertEqual(root.findall(".//vulnerability"), [])
        self.assertIn("unknown", str(warning.call_args))


if __name__ == "__main__":
    unittest.main()
