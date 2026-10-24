"""
Reporting and categorisation constants.
"""

# Contextual Information
INITIAL_CONTEXT_FIELDS = {
    "client_name",
    "remote_access_solution",
}


# Grouped Findings
THEMES = [
    "Authentication",
    "Cryptography",
    "Access Control",
    "Monitoring and Detection",
    "Administrative Security",
    "Platform Configuration",
]


# Executive Summary Stock Text
COMMENTARIES = {

    "Authentication": (
        "Weaknesses affecting authentication controls were observed, "
        "reducing assurance that remote access is restricted to authorised "
        "users and trusted devices."
    ),

    "Cryptography": (
        "Several opportunities existed to strengthen the "
        "cryptographic controls protecting remote access communications."
    ),

    "Access Control": (
        "Access control measures could be further refined to align "
        "permissions with business requirements and least-privilege "
        "principles."
    ),

    "Monitoring and Detection": (
        "Logging and monitoring capabilities could be enhanced to "
        "improve visibility of security-relevant activity."
    ),

    "Administrative Security": (
        "Opportunities were noted to strengthen the governance of "
        "privileged access and administrative functions."
    ),

    "Platform Configuration": (
        "Platform configuration and lifecycle management practices could "
        "be improved to further strengthen the resilience of the remote "
        "access environment."
    ),
}


GROUP_INTROS = {

    "Authentication":
        "Weaknesses were noted in the controls used to verify the "
        "identity of remote access users and devices:",

    "Cryptography":
        "Several cryptographic weaknesses were identified that may reduce "
        "the confidentiality and integrity of remote access communications:",

    "Access Control":
        "The assessment highlighted opportunities to strengthen the controls "
        "used to govern access to organisational resources:",

    "Monitoring and Detection":
        "Visibility of remote access activity could be improved through "
        "enhanced logging, monitoring, and audit capabilities:",

    "Administrative Security":
        "Several observations related to the management of privileged "
        "accounts and administrative permissions:",

    "Platform Configuration":
        "The review found opportunities to improve the configuration "
        "and maintenance of the remote access platform and supporting "
        "infrastructure:",
}


# References Used in the Remediation Section
REFERENCES = {
    "Generic": {
        "NCSC VPN Security Guidance":
            "https://www.ncsc.gov.uk/collection/device-security-guidance/virtual-private-networks",
        "NIST Remote Access Guidance":
            "https://csrc.nist.gov/projects/zero-trust-architecture",
    },
    "Microsoft Always On VPN": {
        "Always On VPN Deployment Guide":
            "https://learn.microsoft.com/windows-server/remote/remote-access/vpn/always-on-vpn/",
    },
    "BeyondTrust PRA": {
        "BeyondTrust PRA Documentation":
            "https://www.beyondtrust.com/docs/remote-support"
    }
}