"""
Reporting and categorisation constants.
"""

INITIAL_CONTEXT_FIELDS = {
    "client_name",
    "remote_access_solution",
    "platform_version",
}

FINDING_THEMES = {
    "Authentication": {
        "vpn-mfa-not-enforced",
        "vpn-shared-accounts-permitted",
        "vpn-local-accounts-enabled",
        "vpn-certificate-authentication-disabled",
        "vpn-weak-authentication-methods",
        "vpn-admin-mfa-not-enforced",
    },

    "Access Control": {
        "vpn-excessive-network-access",
        "vpn-unrestricted-split-tunnelling",
        "vpn-device-compliance-not-enforced",
        "vpn-unmanaged-devices-allowed",
        "vpn-privileged-access-not-restricted",
        "vpn-third-party-access-not-controlled",
        "vpn-user-access-not-reviewed",
        "vpn-account-deprovisioning-not-timely",
    },

    "Cryptography": {
        "vpn-insecure-protocol-enabled",
        "vpn-weak-tls-configuration",
        "vpn-weak-cryptography",
    },

    "Monitoring and Detection": {
        "vpn-insufficient-logging",
        "vpn-logs-not-centralised",
        "vpn-authentication-failure-alerting-missing",
        "vpn-anomalous-login-alerting-missing",
        "vpn-dormant-accounts-not-reviewed",
    },

    "Administrative Security": {
        "vpn-excessive-admin-privileges",
        "vpn-admin-activity-not-logged",
    },

    "Client Security": {
        "vpn-client-versions-unmanaged",
        "vpn-client-updates-not-enforced",
        "vpn-always-on-vpn-disabled",
        "vpn-kill-switch-disabled",
    },

    "Resilience and Availability": {
        "vpn-configuration-backups-missing",
        "vpn-no-high-availability",
        "vpn-failover-not-tested",
    },
}


COMMENTARY_GROUPS = {
    "Authentication": {
        "vpn-mfa-not-enforced",
        "vpn-shared-accounts-permitted",
        "vpn-local-accounts-enabled",
        "vpn-certificate-authentication-disabled",
        "vpn-weak-authentication-methods",
        "vpn-admin-mfa-not-enforced",
    },

    "Access Control": {
        "vpn-excessive-network-access",
        "vpn-unrestricted-split-tunnelling",
        "vpn-device-compliance-not-enforced",
        "vpn-unmanaged-devices-allowed",
        "vpn-privileged-access-not-restricted",
        "vpn-third-party-access-not-controlled",
        "vpn-user-access-not-reviewed",
        "vpn-account-deprovisioning-not-timely",
    },

    "Cryptography": {
        "vpn-insecure-protocol-enabled",
        "vpn-weak-tls-configuration",
        "vpn-weak-cryptography",
    },

    "Monitoring and Detection": {
        "vpn-insufficient-logging",
        "vpn-logs-not-centralised",
        "vpn-authentication-failure-alerting-missing",
        "vpn-anomalous-login-alerting-missing",
        "vpn-dormant-accounts-not-reviewed",
    },

    "Administrative Security": {
        "vpn-excessive-admin-privileges",
        "vpn-admin-activity-not-logged",
    },

    "Client Security": {
        "vpn-client-versions-unmanaged",
        "vpn-client-updates-not-enforced",
        "vpn-always-on-vpn-disabled",
        "vpn-kill-switch-disabled",
    },

    "Resilience and Availability": {
        "vpn-configuration-backups-missing",
        "vpn-no-high-availability",
        "vpn-failover-not-tested",
    },
}


REFERENCES = {
    "Generic": {
        "NCSC VPN Security Guidance":
            "https://www.ncsc.gov.uk/collection/device-security-guidance/virtual-private-networks",
        "NIST Remote Access Guidance":
            "https://csrc.nist.gov/projects/zero-trust-architecture",
    },

    "Cisco Secure Client": {
        "Cisco Secure Client Documentation":
            "https://www.cisco.com/c/en/us/support/security/secure-client/products-installation-and-configuration-guides-list.html",
    },

    "Palo Alto GlobalProtect": {
        "GlobalProtect Administration Guide":
            "https://docs.paloaltonetworks.com/globalprotect",
    },

    "Fortinet FortiClient": {
        "FortiClient Administration Guide":
            "https://docs.fortinet.com/product/forticlient",
    },

    "Check Point Remote Access VPN": {
        "Check Point Remote Access VPN Guide":
            "https://sc1.checkpoint.com/documents",
    },

    "Microsoft Always On VPN": {
        "Always On VPN Deployment Guide":
            "https://learn.microsoft.com/windows-server/remote/remote-access/vpn/always-on-vpn/",
    },

    "OpenVPN": {
        "OpenVPN Documentation":
            "https://openvpn.net/community-resources/",
    },

    "WireGuard": {
        "WireGuard Documentation":
            "https://www.wireguard.com/",
    },
}