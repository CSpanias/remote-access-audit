"""
Markdown reporting functionality.

This exporter generates a consultant-facing assessment
report containing an executive summary, commentary,
and remediation guidance.
"""

from collections import defaultdict
from pathlib import Path

from remote_access_audit.constants import(
    THEMES, REFERENCES, COMMENTARIES, GROUP_INTROS
)
from remote_access_audit.models import AssessmentResults


def _get_review_scope(
    results: AssessmentResults,
) -> str:
    """
    Return a human-readable assessment scope.
    """

    return f"{results.context.remote_access_solution.value} deployment"

#-------------------------------------------------------------------------------
# Executive Summary
#-------------------------------------------------------------------------------
def _generate_assessment_context(
    results: AssessmentResults,
) -> list[str]:
    """
    Generate the assessment context section.
    """

    context = results.context

    lines = []

    lines.extend([
        f"| Organisation | {context.client_name} |",
        f"| Remote Access Solution | {context.remote_access_solution.value} |",
    ])

    if context.vpn_authentication_method:
        lines.append(
            f"| Authentication Method | {context.vpn_authentication_method} |"
        )

    if context.identity_provider:
        lines.append(f"| Identity Provider | {context.identity_provider} |")

    if context.tunnel_type:
        lines.append(f"| Tunnel Type | {context.tunnel_type} |")

    if context.certificate_authority:
        lines.append(
            f"| Certificate Authority | {context.certificate_authority} |"
        )

    if context.split_tunnel_mode:
        lines.append(f"| Split Tunnel Mode | {context.split_tunnel_mode} |")

    return lines


def _get_identified_themes(
    results: AssessmentResults,
) -> list[str]:

    identified = {
        finding.theme
        for finding in results.findings
    }

    return [
        theme
        for theme in THEMES
        if theme in identified
    ]


def _get_security_posture(
    results: AssessmentResults,
) -> str:
    """
    Determine the overall security posture based on the
    ratio of positive observations to findings.
    """

    total = (len(results.findings) + len(results.positives))

    if total == 0:
        return "unknown"

    ratio = len(results.positives) / total

    if ratio >= 0.8:
        return "strong"

    if ratio >= 0.5:
        return "moderate"

    return "weak"


def _format_list(items: list[str]) -> str:

    if not items:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return (
        ", ".join(items[:-1])
        + f", and {items[-1]}"
    )


def _generate_executive_summary(
    results: AssessmentResults,
) -> list[str]:
    """
    Generate the executive summary section.
    """

    lines = []

    posture = _get_security_posture(results)

    scope = _get_review_scope(results)

    themes = _get_identified_themes(results)

    theme_text = _format_list([
        theme.lower()
        for theme in themes
    ])

    lines.append("## Executive Summary")
    lines.append("")

    #---------------------------------------------------------------------------
    # Introductory Paragraph
    #---------------------------------------------------------------------------
    if posture == "strong":
        finding_summary = (
            "The assessed remote access environment demonstrated a "
            "generally mature and well-managed security posture. However, "
            "a small number of opportunities were identified for improvement."
        )

    elif posture == "moderate":
        finding_summary = (
            "The assessed remote access environment demonstrated a mixture of "
            "effective controls as well as opportunities for improvement."
        )

    else:
        finding_summary = (
            "The assessed remote access environment demonstrated several "
            "weaknesses affecting the operation and enforcement of remote "
            "access security controls."
        )

    lines.append(
        "A remote access configuration review was conducted for the "
        f"{results.context.client_name} environment covering the {scope}. "
        "The assessment considered authentication controls, cryptographic "
        "standards, access control mechanisms, monitoring capabilities, "
        "logging and audit controls, administrative security controls, and "
        f"solution-specific security functionality. {finding_summary}"
    )

    lines.append("")

    #---------------------------------------------------------------------------
    # Second Paragraph (High-Level Findings)
    #---------------------------------------------------------------------------
    theme_commentaries = []

    for theme in themes:

        commentary = COMMENTARIES.get(theme)

        if commentary:
            theme_commentaries.append(commentary)

    if theme_commentaries:

        lines.append(
            "The review identified observations across several control areas. "
            + " ".join(theme_commentaries)
        )

        lines.append("")

    #---------------------------------------------------------------------------
    # Conclusion
    #---------------------------------------------------------------------------
    if posture == "strong":
        lines.append(
            "Overall, the assessed configuration provided a generally "
            "effective foundation for secure remote access operations. "
            "The opportunities identified do not indicate any significant "
            "weaknesses; however, addressing them would further improve the "
            "consistency and effectiveness of existing controls."
        )

    elif posture == "moderate":
        lines.append(
            "Overall, the remote access platform provides a foundation for "
            "secure remote access; however, further work is required to "
            "improve the consistency and effectiveness of key security "
            "controls. Addressing the observations identified would reduce "
            "security risk and strengthen assurance in the remote access "
            "environment."
        )

    else:
        lines.append(
            "Overall, significant opportunities exist to strengthen the "
            "security posture of the remote access environment. While the "
            "issues identified do not necessarily indicate an immediate "
            "compromise, they may reduce the effectiveness of controls "
            "intended to protect remote access services. Priority should "
            "be given to improving authentication controls, strengthening "
            "access restrictions, and ensuring that security requirements "
            "are enforced consistently across remote access services."
        )

    lines.append("")

    return lines

#-------------------------------------------------------------------------------
# Technical Commentary
#-------------------------------------------------------------------------------

def _group_findings(
    findings,
) -> dict[str, list]:

    grouped = defaultdict(list)

    for finding in findings:
        grouped[finding.theme].append(finding)

    return dict(grouped)


def _generate_commentary(
    results: AssessmentResults,
) -> list[str]:
    """
    Generate the assessment commentary section.
    """

    lines = []

    lines.append("## Commentary")
    lines.append("")

    lines.append(
        "A remote access configuration review was conducted for the "
        f"{results.context.client_name} environment. The assessment reviewed "
        "the effectiveness of controls used to secure remote access services "
        "and protect access to internal systems and data."
    )

    lines.append("")

    # Context Table
    lines.extend(_generate_assessment_context(results))

    lines.append("")

    # Findings
    grouped_findings = _group_findings(results.findings)

    for group_name, findings in grouped_findings.items():

        intro = GROUP_INTROS.get(group_name)

        if intro:
            lines.append(intro)
            lines.append("")

        for finding in findings:

            lines.append(
                f"- **{finding.title}** - {finding.commentary.strip()}"
            )

            lines.append("")

    return lines

#-------------------------------------------------------------------------------
# Remediation
#-------------------------------------------------------------------------------
def _generate_remediation(
    results: AssessmentResults,
) -> list[str]:
    """
    Generate the remediation section.
    """

    lines = []

    lines.append("## Remediation")
    lines.append("")

    if not results.findings:
        lines.append("No remediation actions are currently required.")
        lines.append("")

    else:
        lines.append("The following remediation actions are recommended:")
        lines.append("")

        recommendations = set()

        for finding in results.findings:
            recommendations.add(finding.solution.strip())

        for recommendation in sorted(recommendations):
            lines.append(f"- {recommendation}")

        lines.append("")

    lines.append("### References")
    lines.append("")

    for title, url in REFERENCES["Generic"].items():
        lines.append(f"- [{title}]({url})")

    platform = results.context.remote_access_solution.value

    if platform in REFERENCES:
        for title, url in REFERENCES[platform].items():
            lines.append(f"- [{title}]({url})")


    return lines


def export_markdown(
    results: AssessmentResults,
    output_file: str,
) -> None:
    """
    Export assessment report as Markdown.
    """

    path = Path(output_file)

    lines = [
        f"# {results.context.client_name} - Remote Access Configuration Review",
        "",
    ]

    lines.extend(_generate_executive_summary(results))

    lines.extend(_generate_commentary(results))

    lines.extend(_generate_remediation(results))

    path.write_text("\n".join(lines), encoding="utf-8")