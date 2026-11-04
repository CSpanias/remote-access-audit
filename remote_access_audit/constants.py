"""
Reporting and categorisation constants.
"""

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


# Grouped Findings
THEMES = [
    "Platform Configuration",
    "Authentication",
    "Cryptography",
    "Access Control",
    "Monitoring and Detection",
    "Administrative Security",
]