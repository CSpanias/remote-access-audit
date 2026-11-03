"""
Markdown reporting functionality.

This exporter generates a consultant-facing assessment
report containing an executive summary, commentary,
and remediation guidance.
"""

from collections import defaultdict
from pathlib import Path

from remote_access_audit.constants import(
    THEMES, REFERENCES, COMMENTARIES
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
def _format_count(
    count: int,
    singular: str,
    plural: str,
) -> str:

    NUMBER_WORDS = {
        0: "no",
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
        9: "nine",
    }

    value = NUMBER_WORDS.get(count, str(count))

    if count == 1:
        return f"{value} {singular}"

    return f"{value} {plural}"


def _generate_assessment_context(
    results: AssessmentResults,
) -> list[str]:
    """
    Generate the assessment context section.
    """

    context = results.context

    lines = []

    lines.append("The assessed remote access environment is summarised below:")
    lines.append("")

    lines.extend([
        "| Property | Value |",
        "|----------|-------|",
        f"| Organisation | {context.client_name} |",
        f"| Remote Access Solution | {context.remote_access_solution.value} |",
    ])

    if context.vpn_authentication_method:
        lines.append(
            f"| Authentication Method | {context.vpn_authentication_method} |"
        )

    if context.deployment_type:
        lines.append(
            f"| Deployment Type | {context.deployment_type} |"
        )

    if context.product_version:
        lines.append(
            f"| Product Version | {context.product_version} |"
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

    finding_count = len(results.findings)
    positive_count = len(results.positives)

    finding_text = _format_count(finding_count, "finding", "findings")
    positive_text = _format_count(
        positive_count,
        "positive observation",
        "positive observations",
    )

    lines.append("## Executive Summary")
    lines.append("")

    #---------------------------------------------------------------------------
    # Introductory Paragraph
    #---------------------------------------------------------------------------
    if posture == "strong":

        finding_summary = (
            f"The assessment identified {finding_text} and {positive_text}. "
            "Security controls were generally well implemented and operating "
            "as intended across the assessed remote access environment."
        )

    elif posture == "moderate":

        finding_summary = (
            f"The assessment identified {finding_text} and {positive_text}. A "
            "mixture of effective controls and opportunities for improvement "
            "was observed across the assessed remote access environment."
        )

    else:

        finding_summary = (
            f"The assessment identified {finding_text} and {positive_text}. "
            "Weaknesses were identified across multiple security domains, "
            "indicating that expected controls were not consistently "
            "implemented or enforced."
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

    theme_text = _format_list([theme.lower() for theme in themes])

    for theme in themes:

        commentary = COMMENTARIES.get(theme)

        if commentary:
            theme_commentaries.append(commentary)

    if results.findings:

        lines.append(
            f"The most significant observations related to {theme_text}. "
            + " ".join(theme_commentaries)
        )

    else:

        lines.append(
            "No significant weaknesses were identified during the review. "
            "The assessed controls were operating as intended..."
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

def _build_authentication_commentary(
    findings: list,
) -> str:

    finding_ids = {f.finding_id for f in findings}

    paragraph = (
        "Several weaknesses were identified in the authentication controls "
        "protecting the remote access environment. "
    )

    if (
        "user-mfa-not-enforced" in finding_ids
        and "admin-mfa-not-enforced" in finding_ids
    ):
        paragraph += (
            "Multi-factor authentication was not enforced consistently for "
            "either remote access users or administrative accounts. "
        )

    elif "user-mfa-not-enforced" in finding_ids:
        paragraph += (
            "Multi-factor authentication was not enforced for remote "
            "access users. "
        )

    elif "admin-mfa-not-enforced" in finding_ids:
        paragraph += (
            "Administrative accounts were not protected through mandatory "
            "multi-factor authentication. "
        )

    if "shared-accounts-permitted" in finding_ids:
        paragraph += (
            "The review also identified the use of shared accounts, "
            "reducing accountability and auditability of user activity. "
        )

    if "local-accounts-enabled" in finding_ids:
        paragraph += (
            "Furthermore, authentication relied on locally managed "
            "accounts rather than a centrally managed identity "
            "provider, limiting the consistent enforcement of "
            "organisational authentication controls. "
        )

    if "pra-vendor-authentication-not-secure" in finding_ids:
        paragraph += (
            "Vendor authentication controls were not configured "
            "in accordance with organisational security requirements. "
        )

    paragraph += (
        "Collectively, these observations may reduce assurance that "
        "users are appropriately authenticated and increase the risk "
        "of account compromise."
    )

    return paragraph


def _build_cryptography_commentary(
    findings: list,
) -> str:

    finding_ids = {f.finding_id for f in findings}

    if not finding_ids:
        return ""

    paragraph = (
        "The configuration of cryptographic controls did not align fully with "
        "current security best practice. "
    )

    if (
        "weak-tls-configuration" in finding_ids
        and "weak-cryptography" in finding_ids
    ):
        paragraph += (
            "Deprecated TLS configurations and weak cryptographic algorithms "
            "remained enabled within the assessed environment. "
        )

    elif "weak-tls-configuration" in finding_ids:
        paragraph += (
            "Deprecated TLS configurations remained enabled. "
        )

    elif "weak-cryptography" in finding_ids:
        paragraph += (
            "Weak or deprecated cryptographic algorithms remained enabled. "
        )

    paragraph += (
        "These weaknesses may reduce the confidentiality and integrity of "
        "remote access communications."
    )

    return paragraph


def _build_monitoring_commentary(
    findings: list,
) -> str:

    finding_ids = {f.finding_id for f in findings}

    if not finding_ids:
        return ""

    paragraph = (
        "The review highlighted opportunities to improve visibility, "
        "monitoring, and audit capabilities associated with remote "
        "access services. "
    )

    if "insufficient-logging" in finding_ids:
        paragraph += (
            "Authentication, connection, and security-relevant events "
            "were not being logged and monitored to the extent expected. "
        )

    if "admin-activity-not-retained-or-reviewed" in finding_ids:
        paragraph += (
            "Administrative audit activity was not retained or "
            "reviewed appropriately. "
        )

    if "pra-session-recording-disabled" in finding_ids:
        paragraph += (
            "Privileged session recording was not enforced. "
        )

    if "pra-session-recording-can-be-disabled" in finding_ids:
        paragraph += (
            "Asset policies permitted session recording controls "
            "to be bypassed. "
        )

    if "pra-session-inactivity-timeout-not-configured" in finding_ids:
        paragraph += (
            "Inactive sessions were not terminated automatically. "
        )

    paragraph += (
        "As a result, visibility of security events may be reduced and "
        "the investigation of suspicious or privileged activity may be "
        "more difficult."
    )

    return paragraph


def _build_access_control_commentary(
    findings: list,
) -> str:

    finding_ids = {f.finding_id for f in findings}

    if not finding_ids:
        return ""

    paragraph = (
        "Several opportunities were identified to strengthen access "
        "control and governance arrangements associated with remote "
        "access services. "
    )

    if "user-access-not-reviewed" in finding_ids:
        paragraph += (
            "Remote access permissions were not subject to periodic "
            "review. "
        )

    if "pra-jump-clients-not-restricted" in finding_ids:
        paragraph += (
            "In addition, Jump Client deployments were not subject "
            "to sufficient governance controls. "
        )

    if "pra-vendor-account-expiration-not-enforced" in finding_ids:
        paragraph += (
            "Vendor account lifecycle controls did not automatically "
            "expire third-party access. "
        )

    if "pra-network-restrictions-not-configured" in finding_ids:
        paragraph += (
            "Administrative and remote access interfaces were not "
            "restricted to approved source networks. "
        )

    paragraph += (
        "These observations may increase the likelihood of excessive "
        "access and reduce assurance that remote access permissions "
        "remain aligned to business requirements."
    )

    return paragraph


def _build_admin_security_commentary(
        findings:list,
) -> str:

    finding_ids = {f.finding_id for f in findings}

    observations = []

    if "pra-credential-injection-not-used" in finding_ids:
        observations.append(
            "privileged credentials were disclosed directly to users rather "
            "than protected through credential injection controls"
        )

    if "pra-vault-password-rotation-not-enforced" in finding_ids:
        observations.append(
            "privileged credentials were not rotated automatically"
        )

    if "pra-session-context-not-required" in finding_ids:
        observations.append(
            "privileged sessions could be initiated without requiring business "
            "justification"
        )

    if "pra-simultaneous-vault-checkout-allowed" in finding_ids:
        observations.append(
            "multiple users could simultaneously check out privileged "
            "credentials"
        )

    if "pra-file-transfer-malware-scanning-not-enabled" in finding_ids:
        observations.append(
            "file transfers were not inspected using integrated malware "
            "scanning controls"
        )

    if not observations:
        return ""

    paragraph = (
        "The review identified weaknesses affecting privileged access "
        "governance and administrative security controls. "
    )

    paragraph += (
        observations[0].capitalize()
        if len(observations) == 1
        else ", ".join(observations[:-1]) + f", and {observations[-1]}"
    )

    paragraph += (
        ". As a result, the risk of credential disclosure, inappropriate "
        "credential use, unauthorised access, and long-term compromise may be "
        "increased. Strengthening privileged credential management controls "
        "would improve assurance that administrative access is appropriately "
        "governed and protected."
    )

    return paragraph


def _build_platform_commentary(
        findings: list,
) -> str:

    finding_ids = {f.finding_id for f in findings}

    paragraph = (
        "A number of observations were made regarding the "
        "management and operation of the remote access platform. "
    )

    if "pra-update-management-not-defined" in finding_ids:
        paragraph += (
            "Appliance updates were not governed by a defined update process. "
        )

    if "aovpn-prelogon-connectivity-disabled" in finding_ids:
        paragraph += (
            "In addition, pre-logon VPN connectivity was not available. "
        )

    paragraph += (
        "These observations may reduce the effectiveness, resilience, or "
        "manageability of the remote access service."
    )

    return paragraph


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
    builders = {
        "Platform Configuration": _build_platform_commentary,
        "Authentication": _build_authentication_commentary,
        "Cryptography": _build_cryptography_commentary,
        "Access Control": _build_access_control_commentary,
        "Monitoring and Detection": _build_monitoring_commentary,
        "Administrative Security": _build_admin_security_commentary,
    }

    grouped_findings = _group_findings(results.findings)

    for theme in THEMES:

        findings = grouped_findings.get(theme)

        if not findings:
            continue

        builder = builders.get(theme)

        if builder:
            lines.append(builder(findings))
            lines.append("")

    # Positive Observations
    if results.positives:

        lines.append("## Positive Observations")
        lines.append("")

        for positive in results.positives:
            lines.append(f"- {positive.text}")

        lines.append("")

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

        recommendations = []

        for finding in results.findings:

            solution = finding.solution.strip()

            if solution not in recommendations:
                recommendations.append(solution)

        for recommendation in recommendations:
            lines.append(f"- {recommendation}")

        lines.append("")

    lines.append("### References")
    lines.append("")

    for title, url in REFERENCES["Generic"].items():
        lines.append(f"- [{url}]({url})")

    platform = results.context.remote_access_solution.value

    if platform in REFERENCES:
        for title, url in REFERENCES[platform].items():
            lines.append(f"- [{url}]({url})")


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