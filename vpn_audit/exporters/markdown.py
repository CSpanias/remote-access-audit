"""
Markdown reporting functionality.

This exporter generates a consultant-facing assessment
report containing an executive summary, commentary,
and remediation guidance.
"""

from pathlib import Path

from vpn_audit.constants import (
    FINDING_THEMES, COMMENTARY_GROUPS, REFERENCES
)
from vpn_audit.models import AssessmentResults


def _get_review_scope(
    results: AssessmentResults,
) -> str:
    """
    Return a human-readable assessment scope.
    """

    return (
        f"{results.context.vpn_vendor.value} "
        "remote access environment"
    )

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

    lines.append("## Assessment Context")
    lines.append("")

    lines.extend([
        "| Field | Value |",
        "|-------|-------|",
        f"| Client | {context.client_name} |",
        f"| VPN Solution | {context.vpn_vendor.value} |",
        f"| VPN Version | {context.vpn_version} |",
    ])

    if context.deployment_model:
        lines.append(
            f"| Deployment Model | {context.deployment_model} |"
        )

    if context.vpn_user_count is not None:
        lines.append(
            f"| VPN Users | {context.vpn_user_count} |"
        )

    if context.vpn_gateway_count is not None:
        lines.append(
            f"| VPN Gateways | {context.vpn_gateway_count} |"
        )

    if context.authentication_method:
        lines.append(
            f"| Authentication Method | {context.authentication_method} |"
        )

    if context.identity_provider:
        lines.append(
            f"| Identity Provider | {context.identity_provider} |"
        )

    if context.tunnel_type:
        lines.append(
            f"| Tunnel Type | {context.tunnel_type} |"
        )

    if context.certificate_authority:
        lines.append(
            f"| Certificate Authority | {context.certificate_authority} |"
        )

    if context.user_control:
        lines.append(
            f"| User Control | {context.user_control} |"
        )

    if context.split_tunnel_mode:
        lines.append(
            f"| Split Tunnel Mode | {context.split_tunnel_mode} |"
        )

    if context.mfa_solution:
        lines.append(
            f"| MFA Solution | {context.mfa_solution} |"
        )

    lines.append("")

    if context.context_notes:

        lines.append("### Environmental Observations")
        lines.append("")

        for field, note in context.context_notes.items():

            field_name = (field.replace("_", " ").title())
            lines.append(f"- **{field_name}:** {note}")

        lines.append("")


    return lines

def _get_identified_themes(
    results: AssessmentResults,
) -> list[str]:
    """
    Return the security themes affected by identified findings.
    """

    identified_themes = []

    finding_ids = {
        finding.finding_id
        for finding in results.findings
    }

    for theme, theme_findings in FINDING_THEMES.items():
        if finding_ids.intersection(theme_findings):
            identified_themes.append(theme)

    return identified_themes


def _get_security_posture(
    results: AssessmentResults,
) -> str:
    """
    Determine the overall security posture based on the
    ratio of positive observations to findings.
    """

    total = (
        len(results.findings)
        + len(results.positives)
    )

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

    theme_names = [
        theme.lower()
        for theme in themes
    ]

    theme_text = _format_list(theme_names)

    lines.append("## Executive Summary")
    lines.append("")

    #---------------------------------------------------------------------------
    # Introductory Paragraph
    #---------------------------------------------------------------------------
    lines.append(
        "A VPN configuration review was conducted "
        f"for the {results.context.client_name} environment "
        f"covering the {scope}. The assessment considered "
        "authentication controls, cryptographic standards, "
        "access control mechanisms, client security settings, "
        "monitoring capabilities, and administrative controls."
    )

    lines.append("")

    #---------------------------------------------------------------------------
    # Second Paragraph
    #---------------------------------------------------------------------------
    if posture == "strong":
        lines.append(
            "The review identified that security controls were generally well "
            "implemented across the assessed VPN environment. While several "
            f"opportunities for improvement relating to {theme_text} were "
            "identified, the majority of assessed controls were operating as "
            "intended."
        )

    elif posture == "moderate":
        lines.append(
            "The review identified a mixture of effective controls and "
            "opportunities for improvement across the assessed VPN "
            f"environment. Areas requiring attention related to {theme_text}."
        )

    else:
        lines.append(
            "The review identified several weaknesses affecting the "
            "implementation and enforcement of VPN security controls. "
            "Opportunities for improvement were identified relating to "
            f"{theme_text}."
        )

    lines.append("")

    #---------------------------------------------------------------------------
    # Third Paragraph
    #---------------------------------------------------------------------------
    impact_areas = []

    if "Authentication" in themes:
        impact_areas.append(
            "ensuring only authorised users can establish VPN connections"
        )

    if "Access Control" in themes:
        impact_areas.append(
            "restricting network access according to least-privilege principles"
        )

    if "Cryptography" in themes:
        impact_areas.append(
            "protecting VPN communications through secure cryptographic standards"
        )

    if "Monitoring and Detection" in themes:
        impact_areas.append(
            "detecting suspicious VPN activity and security events"
        )

    if not impact_areas:
        impact_text = ("maintaining secure remote access controls")

    else:
        impact_text = _format_list(impact_areas)

    if results.findings:

        lines.append(
            "The issues identified may reduce assurance that security "
            "requirements are applied consistently across the VPN "
            "environment. Several observations related to controls "
            f"responsible for {impact_text}. "
            "Where such controls are not consistently enforced, the "
            "likelihood of unauthorised access, network compromise, "
            "or misuse of remote access services may increase."
        )

    else:

        lines.append(
            "No significant weaknesses were identified during the review. "
            "The assessed controls were operating as intended and "
            "contributed towards the secure operation of the VPN environment "
            "and the protection of corporate information."
        )

    lines.append("")

    #---------------------------------------------------------------------------
    # Conclusion
    #---------------------------------------------------------------------------
    if posture == "strong":
        lines.append(
            "Overall, the assessed configuration provided a generally "
            "effective foundation for secure remote access operations. "
            "Addressing the identified opportunities would further "
            "improve the consistency and effectiveness of existing controls."
        )

    elif posture == "moderate":
        lines.append(
            "Overall, the VPN platform provides a foundation for secure "
            "remote access; however, further work is required to ensure "
            "that security controls are applied consistently across the "
            "environment."
        )

    else:
        lines.append(
            "Overall, significant opportunities exist to strengthen the "
            "security posture of the VPN environment. Priority should be "
            "given to improving authentication controls, strengthening "
            "access restrictions, and ensuring that security requirements "
            "are enforced consistently across remote access services."
        )

    lines.append("")

    return lines

#-------------------------------------------------------------------------------
# Technical Commentary
#-------------------------------------------------------------------------------
def _get_group_intro(
    group_name: str,
) -> str:

    intros = {
        "Authentication": (
            "The review identified weaknesses relating to the authentication "
            "mechanisms used to establish VPN connections. Strong authentication "
            "controls help ensure that remote access is restricted to authorised users."
        ),

        "Access Control": (
            "Opportunities for improvement were identified in the controls used "
            "to restrict access to internal resources. Effective access control "
            "helps limit the impact of account compromise and insider misuse."
        ),

        "Cryptography": (
            "The assessment identified areas where cryptographic controls could "
            "be strengthened to better protect VPN communications from interception "
            "or manipulation."
        ),

        "Monitoring and Detection": (
            "Several observations related to logging, monitoring, and detection "
            "capabilities. Effective monitoring improves visibility of suspicious "
            "activity and supports incident investigation."
        ),

        "Administrative Security": (
            "The review identified opportunities to strengthen administrative "
            "security controls governing the management of the VPN environment."
        ),

        "Client Security": (
            "Further observations related to the configuration and management "
            "of VPN client software used by end users."
        ),

        "Resilience and Availability": (
            "The assessment identified opportunities to improve the resilience "
            "and availability of remote access services."
        ),
    }

    return intros.get(group_name, "")


def _group_findings(
    findings,
) -> dict[str, list]:

    grouped = {}

    for group_name, group_ids in COMMENTARY_GROUPS.items():

        matches = [
            finding
            for finding in findings
            if finding.finding_id in group_ids
        ]

        if matches:
            grouped[group_name] = matches

    return grouped


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
        "A VPN configuration review was conducted "
        f"for the {results.context.client_name} environment. "
        "The assessment reviewed the effectiveness of controls "
        "used to secure remote access services and protect access "
        "to internal systems and data."
    )

    lines.append("")

    grouped_findings = _group_findings(results.findings)

    for group_name, findings in grouped_findings.items():

        lines.append(f"### {group_name}")
        lines.append("")

        intro = _get_group_intro(group_name)

        if intro:
            lines.append(intro)
            lines.append("")

        for finding in findings:
            lines.append(finding.commentary.strip())
            lines.append("")

    lines.append("")

    lines.append("### Conclusion")
    lines.append("")

    if results.findings:
        lines.append(
            "The review identified several opportunities to further "
            "strengthen the security posture of the VPN environment. "
            "Addressing the observations identified throughout the "
            "assessment would improve assurance that remote access "
            "controls are operating effectively and consistently."
        )
    else:
        lines.append(
            "No security weaknesses were identified during the review. "
            "The assessed controls appeared to provide an appropriate "
            "baseline for secure remote access operations."
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

    vendor = results.context.vpn_vendor.value

    if vendor in REFERENCES:
        for title, url in REFERENCES[vendor].items():
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
        f"# {results.context.client_name} - VPN Configuration Review",
        "",
    ]

    lines.extend(
        _generate_executive_summary(results)
    )

    lines.extend(
        _generate_assessment_context(results)
    )

    lines.extend(
        _generate_commentary(results)
    )

    lines.extend(
        _generate_remediation(results)
    )

    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )