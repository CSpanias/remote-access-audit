# BeyondTrust Privilege Remote Access (PRA)

## Overview

This assessment framework is designed to support reviews of BeyondTrust Privileged Remote Access (PRA) deployments.

The goal of the assessment is to assess whether the platform has been configured and governed in a manner that aligns with organisational security requirements and industry good practice. The framework guides assessors through a series of focused questions covering platform configuration, authentication, access control, privileged access governance, cryptographic protections, monitoring, and auditing. The outcome is a set of findings and positive observations that can be used to understand the security posture of the deployment and identify opportunities for improvement.

This document serves two purposes. Firstly, it provides background information for consultants performing assessments using the tool. Secondly, it acts as a high-level introduction to BeyondTrust PRA for assessors who may not have prior experience with PRA platforms.

## What is Privileged Remote Access?

Traditional VPN solutions provide users with network connectivity into an organisation's environment. Once connected, users typically gain access to a range of internal services depending on their permissions and network routing configuration.

PRA platforms take a different approach. Rather than granting users broad network-level access, a PRA platform brokers access to approved systems and sessions. The user authenticates to the PRA platform, selects an authorised asset, and the platform establishes and controls the remote session on the user's behalf.

This model allows organisations to apply additional controls that are difficult or impossible to enforce consistently through traditional remote access technologies. Examples include session recording, credential vaulting, credential injection, approval workflows, access reviews, session monitoring, and detailed auditing. As a result, PRA solutions are commonly used to manage administrative access, privileged operations, vendor access, contractor access, and access to sensitive systems.

## What is BeyondTrust PRA?

[BeyondTrust PRA](https://docs.beyondtrust.com/pra/docs/welcome-to-privileged-remote-access) is a platform designed to provide secure remote access to systems, applications, and infrastructure while maintaining visibility and control over privileged activities. The platform supports both internal and external users and provides a range of capabilities intended to strengthen governance over remote access activities.

Key platform capabilities include controlled remote access, integration with enterprise identity providers, session monitoring and recording, privileged credential management, granular access policy enforcement, and support for third-party access management. Throughout this assessment, many of the controls reviewed relate to how effectively these capabilities are configured and governed.

## Assessment Methodology

The assessment is divided into six areas.

1. **Platform Configuration** focuses on how the platform is deployed and maintained.
2. **Authentication** examines how users prove their identity prior to gaining access.
3. **Administrative Security** focuses on privileged access controls and credential governance.
4. **Cryptography** reviews the protections applied to communications and authentication mechanisms.
5. **Access Control** examines how permissions are assigned, reviewed, and restricted.
6. **Monitoring and Detection** focuses on visibility, auditability, and the organisation's ability to investigate activity performed through the platform.

Each section below provides background information to help assessors understand the purpose of the controls being reviewed and the security objectives they are intended to achieve. Associated assessment controls are listed under each section for ease of reference.

### Platform Configuration

> - `product_version` ([status](https://docs.beyondtrust.com/pra/docs/pf-status))
> - `pra-update-management-not-defined` ([updates](https://docs.beyondtrust.com/pra/docs/pf-updates))

Platform Configuration focuses on how the platform is deployed, maintained, and operated.

An assessor should first understand how the PRA environment has been implemented. BeyondTrust PRA may be deployed as a cloud-hosted service, as a customer-managed appliance, or through a hybrid deployment model that combines elements of both.

Understanding the deployment model is important because security responsibilities differ significantly between deployment types. For example, cloud-hosted environments may have infrastructure maintenance responsibilities split between the customer and BeyondTrust, whereas on-premises deployments generally require the customer to manage platform updates, infrastructure security, backup arrangements, and disaster recovery processes.

In addition to understanding the deployment model, assessors should identify the deployed product version. This information provides useful context when validating feature availability, reviewing vendor documentation, and understanding potential lifecycle considerations.

A key objective within this area is determining whether platform updates are managed through a defined maintenance process. Organisations should be able to demonstrate how updates are identified, tested, approved, scheduled, and deployed. An effective update process helps ensure security fixes and platform improvements are applied in a controlled and consistent manner.

### Authentication

> - `identity_provider` ([identity provider](https://docs.beyondtrust.com/pra/docs/identity-providers))
> - `user-mfa-not-enforced`, `admin-mfa-not-enforced` ([group policy settings](https://docs.beyondtrust.com/pra/docs/pf-group-policies#group-policy-settings))
> - `pra-vendor-authentication-not-secure` ([vendor authentication](https://docs.beyondtrust.com/pra/docs/pf-security#vendor-authentication))
> - `shared-accounts-permitted`
> - `local-accounts-enabled` ([security providers](https://docs.beyondtrust.com/pra/docs/pf-security-providers))

Authentication controls determine how users prove their identity before remote access is granted. Strong authentication controls are fundamental to the security of both VPN and PRA platforms. Because PRA deployments often provide access to highly privileged systems, compromise of an account can have significant consequences.

The assessment should begin by understanding where user identities originate. Most organisations integrate BeyondTrust PRA with a central identity provider such as Microsoft Entra ID, Active Directory, LDAP, SAML, or OpenID Connect. Centralised authentication simplifies account lifecycle management, access governance, auditing, and enforcement of security controls.

The review should then consider Multi-Factor Authentication (MFA). MFA significantly reduces the risk associated with password compromise by requiring users to present more than one form of authentication. Particular attention should be paid to privileged and administrative accounts, as compromise of these accounts may grant extensive control over the platform.

Vendor authentication is another important area of review. BeyondTrust PRA is frequently used to facilitate access for third-party users such as suppliers, support providers, and managed service providers. Vendor authentication settings should therefore be reviewed separately to ensure they meet organisational requirements and provide sufficient protection against unauthorised access.

Finally, assessors should verify that individual users are assigned unique accounts. Shared accounts reduce accountability and make it significantly more difficult to attribute actions to specific individuals during investigations or audits.

### Administrative Security

> - `pra-credential-injection-not-used` ([desktop credential injection](https://docs.beyondtrust.com/pra/docs/desktop-credential-injection))
> - `pra-vault-password-rotation-not-enforced` ([account policies](https://docs.beyondtrust.com/pra/docs/pf-account-policies), [scheduled password rotation rules](https://docs.beyondtrust.com/pra/docs/pf-vault-options#scheduled-password-rotation-rules))
> - `pra-session-context-not-required` ([context requirement](https://docs.beyondtrust.com/pra/docs/pf-jump-policies#context-requirement))
> - `pra-simultaneous-vault-checkout-allowed` ([account-groups](https://docs.beyondtrust.com/pra/docs/pf-account-groups), [allow simultaneous checkout rules](https://docs.beyondtrust.com/pra/docs/pf-vault-options#allow-simultaneous-checkout-rules))
> - `pra-file-transfer-malware-scanning-not-enabled` ([icap configuration](https://docs.beyondtrust.com/pra/docs/pf-security#icap-configuration))

Administrative Security focuses on the governance of privileged access and the protection of privileged credentials. One of the primary security advantages of PRA platforms is their ability to control how privileged credentials are used. Rather than disclosing passwords to users, BeyondTrust PRA can inject credentials directly into approved sessions. This allows users to perform administrative tasks without ever viewing or handling the underlying password.

The assessment should determine whether credential injection is being used wherever practical. Where credentials are disclosed directly to users, the organisation loses many of the governance benefits associated with privileged access management.

Privileged credentials should also be rotated automatically. Regular credential rotation reduces the risk associated with compromise, password reuse, and long-lived privileged accounts. Assessors should review the configuration of Vault Account Policies and confirm that automated password rotation is being enforced where supported.

The review should also consider whether users are required to provide operational context before initiating privileged sessions. Requiring a ticket reference, change reference, or business justification improves accountability and helps demonstrate that access activities are connected to legitimate business requirements.

Credential governance should extend to credential checkout controls. Allowing multiple users to check out the same privileged credential simultaneously may reduce accountability and make it more difficult to attribute privileged activity accurately.

Finally, organisations may choose to integrate file transfer workflows with malware inspection technologies. While not typically considered a baseline security requirement, malware scanning can provide an additional layer of defence in environments with enhanced security or compliance requirements.

### Cryptography

> - `weak-cryptography` ([tls configuration](https://docs.beyondtrust.com/pra/docs/pf-tls-configuration))

Cryptographic controls protect communications between users, managed systems, and the PRA platform.

Assessors should review the SSL/TLS configuration and confirm that communications are protected using supported protocol versions and cryptographic algorithms. Deprecated protocols, weak ciphers, and insecure cryptographic configurations may reduce the confidentiality and integrity of remote access communications.

Within current versions of BeyondTrust PRA, TLS 1.2 and TLS 1.3 are enabled by default and cannot be disabled through the appliance interface. As a result, the assessment should focus primarily on cipher suite configuration, certificate management, and alignment with current vendor guidance rather than TLS protocol version selection.

The assessment should seek to determine whether the deployment aligns with current vendor recommendations and accepted security practice.

### Access Control

> - `user-access-not-reviewed`
> - `pra-jump-clients-not-restricted` ([jump clients](https://docs.beyondtrust.com/pra/docs/jump-clients-1))
> - `pra-vendor-account-expiration-not-enforced` ([vendors](https://docs.beyondtrust.com/pra/docs/pf-vendors))
> - `pra-network-restrictions-not-configured` ([network restrictions](https://docs.beyondtrust.com/pra/docs/pf-security#network-restrictions))

Access Control focuses on ensuring users receive appropriate access and that permissions remain aligned with operational requirements over time. The assessment should examine how permissions are granted, reviewed, and removed throughout the user lifecycle. 

Periodic access reviews are particularly important. Even well-designed permission models can become ineffective when access accumulates over time or remains assigned after responsibilities change. Regular reviews help ensure permissions remain appropriate and reflect current business needs.

Where Jump Clients are used, their deployment should be carefully governed. Jump Clients provide persistent remote access capabilities and may therefore introduce unmanaged access paths if deployment is not controlled appropriately.

Third-party access should also be reviewed. Vendor accounts should be subject to lifecycle controls that automatically expire access when it is no longer required. Long-lived third-party accounts create unnecessary risk and often persist beyond the original business requirement.

Organisations may also choose to restrict access to administrative interfaces, APIs, consoles, or management functions based on source network location. While not appropriate in every environment, network restrictions can provide valuable defence-in-depth protections where trusted administration networks exist.

### Monitoring and Detection

> - `insufficient-logging` ([reports](https://docs.beyondtrust.com/pra/docs/pf-reports))
> - `admin-activity-not-retained-or-reviewed` ([reports](https://docs.beyondtrust.com/pra/docs/pf-reports), [application administration](https://docs.beyondtrust.com/pra/docs/pf-appliance-administration))
> - `pra-session-recording-disabled` ([configuration](https://docs.beyondtrust.com/pra/docs/pf-configuration))
> - `pra-session-recording-can-be-disabled` ([disable recordings](https://docs.beyondtrust.com/pra/docs/pf-jump-policies#disable-recordings))
> - `pra-session-inactivity-timeout-not-configured` ([group policies](https://docs.beyondtrust.com/pra/docs/pf-group-policies), [log out idle user after](https://docs.beyondtrust.com/pra/docs/pf-security#log-out-idle-user-after), [remove user from session after inactivity](https://docs.beyondtrust.com/pra/docs/pf-security#remove-user-from-session-after-inactivity))

Monitoring and Detection controls help organisations maintain visibility of activity occurring within the platform and support incident investigation when required.

The assessment should determine whether security-relevant events are logged and retained appropriately. This includes authentication activity, session activity, administrative actions, and other events that may be useful for investigations or security monitoring.

Administrative activity deserves particular attention. Changes to security settings, user management functions, platform configuration, and privileged access controls should be attributable to individual users through appropriate audit logging.

Session recording is one of the most significant security capabilities provided by BeyondTrust PRA. Session recordings create an auditable record of privileged activity and can be invaluable when investigating suspected misuse, policy violations, or security incidents. Assessors should verify not only that session recording is enabled, but also that policy configurations do not permit individual sessions to bypass recording requirements.

Finally, organisations should ensure that inactive sessions are terminated automatically after a suitable period of inactivity. Idle privileged sessions represent unnecessary risk and may be susceptible to misuse if workstations are left unattended.