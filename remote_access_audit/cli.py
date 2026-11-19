"""
Command-line interface for Remote Access Audit.

Remote Access Audit is a guided assessment tool that assists
security professionals in performing remote access security
reviews. The tool collects environment information, conducts
a structured control assessment, and generates findings,
remediation guidance, and report outputs.
"""

import argparse

from rich.panel import Panel

from remote_access_audit.exporters.json import (
    build_findings, export_findings_json, export_assessment_responses_json
)
from remote_access_audit.exporters.markdown import export_markdown
from remote_access_audit.exporters.sureformat import export_sureformat
from remote_access_audit.review import run_assessment
from remote_access_audit.ui import console


def main() -> None:
    """
    Execute the remote access assessment workflow.
    """

    parser = argparse.ArgumentParser(
        description="Conduct remote access security reviews.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--csacyber",
        action="store_true",
        help="Export SureFormat XML instead of JSON findings",
    )
    parser.add_argument(
        "--hostname",
        help="SureCloud asset hostname (required with --csacyber)",
    )
    args = parser.parse_args()
    if args.csacyber and (not args.hostname or not args.hostname.strip()):
        parser.error("--csacyber requires a non-empty --hostname")
    if args.hostname is not None and not args.csacyber:
        parser.error("--hostname requires --csacyber")

    results = run_assessment()

    console.print()
    console.print(Panel.fit("[bold green]Assessment Complete[/bold green]"))
    console.print(f"[cyan]Responses:[/cyan] {len(results.responses)}")
    console.print(f"[red]Findings:[/red] {len(results.findings)}")
    console.print(f"[green]Positive Observations:[/green] {len(results.positives)}")

    if args.csacyber:
        export_sureformat(
            build_findings(results), args.hostname.strip(), "remote-access-review-findings.xml"
        )
    else:
        export_findings_json(results, "remote-access-review-findings.json")
    export_markdown(results, "remote-access-review-report.md")
    export_assessment_responses_json(results, "remote-access-review-notes.json")


if __name__ == "__main__":
    main()