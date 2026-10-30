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
    export_findings_json, export_assessment_responses_json
)
from remote_access_audit.exporters.markdown import export_markdown
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

    parser.parse_args()

    results = run_assessment()

    console.print()
    console.print(Panel.fit("[bold green]Assessment Complete[/bold green]"))
    console.print(f"[cyan]Responses:[/cyan] {len(results.responses)}")
    console.print(f"[red]Findings:[/red] {len(results.findings)}")
    console.print(f"[green]Positive Observations:[/green] {len(results.positives)}")

    export_findings_json(results, "remote-access-review-findings.json")
    export_markdown(results, "remote-access-review-report.md")
    export_assessment_responses_json(results, "remote-access-review-notes.json")


if __name__ == "__main__":
    main()