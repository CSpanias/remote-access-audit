"""SureFormat XML export for remote access findings."""

import xml.etree.ElementTree as ET
from pathlib import Path

from remote_access_audit.ui import console

FINDING_MAP = {
    "remote-access-audit": "SC-9941",
    "weak-tls-configuration": "SC-1946",
    "weak-cryptography": "SC-1520",
    "vpn-unrestricted-split-tunnelling": "SC-3425",
    "device-compliance-not-enforced": "SC-7895",
    "insufficient-logging": "SC-1501",
    "aovpn-prelogon-connectivity-disabled": "SC-3448",
}


def export_sureformat(findings: list[dict[str, str]], hostname: str, output_file: str) -> None:
    """Write mapped findings for the specified SureCloud asset."""
    root = ET.Element("items", source="SureFormat", version="1.0.0")
    item = ET.SubElement(root, "item", ipaddress="", hostname=hostname)
    services = ET.SubElement(item, "services")
    service = ET.SubElement(services, "service", name="", port="", protocol="tcp")
    vulnerabilities = ET.SubElement(service, "vulnerabilities")

    for finding in findings:
        vulnerability_id = FINDING_MAP.get(finding["id"])
        if not vulnerability_id:
            console.print(f"[yellow][!][/yellow] No SureFormat mapping found for finding: "
                          f"{finding['id']}")
            continue
        vulnerability = ET.SubElement(vulnerabilities, "vulnerability", id=vulnerability_id)
        ET.SubElement(vulnerability, "information").text = finding["description"]

    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")
    tree.write(Path(output_file), encoding="utf-8", xml_declaration=False)
