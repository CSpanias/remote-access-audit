
"""
Core data models used throughout the Remote Access Audit application.

This module defines the strongly-typed data structures that represent:

- Assessment questions
- Review context collected from the client
- Assessor responses
- Audit findings
- Positive observations
- Final assessment results

The models are implemented using Pydantic and provide validation for
data loaded from YAML files and generated during the audit workflow.

These models form the contract between the review engine and all
exporters, ensuring a consistent and predictable data structure
throughout the application.
"""

from enum import Enum

from pydantic import BaseModel, Field



class SolutionType(str, Enum):
    """
    Supported remote access solution categories.

    VPN:
        Traditional remote network access solutions which
        provide connectivity to internal networks and services.

    PRA:
        Privileged Remote Access solutions which broker,
        control, and monitor access to individual systems
        and resources.
    """

    VPN = "vpn"
    PRA = "pra"


class RemoteAccessPlatform(str, Enum):
    """
    Supported remote access platforms.

    Used for displaying solution-specific navigation hints
    throughout the assessment process.
    """

    ALWAYS_ON_VPN = "Microsoft Always On VPN"
    BEYONDTRUST_PRA = "BeyondTrust PRA"
    OTHER = "Other"

    @property
    def solution_type(self) -> SolutionType:

        if self is RemoteAccessPlatform.ALWAYS_ON_VPN:
            return SolutionType.VPN

        if self is RemoteAccessPlatform.BEYONDTRUST_PRA:
            return SolutionType.PRA

        if self is RemoteAccessPlatform.OTHER:
            return SolutionType.VPN

        raise ValueError(f"No solution type defined for {self}")


class AuditAnswer(str, Enum):
    """
    Possible assessment outcomes recorded by the assessor.

    COMPLIANT:
        The control is implemented as expected.

    NON_COMPLIANT:
        The control is missing, disabled, or implemented
        incorrectly.

    NOT_APPLICABLE:
        The control does not apply to the assessed
        environment.

    UNKNOWN:
        The assessor was unable to determine the status
        of the control during the review.
    """
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class ContextField(BaseModel):
    """
    Defines a contextual information field collected before
    the assessment begins.
    """

    id: str

    label: str
    type: str

    required: bool = True

    solution_types: list[SolutionType] = Field(
        default_factory=lambda: [
            SolutionType.VPN,
            SolutionType.PRA,
        ]
    )

    options: list[str] | None = None

    hints: dict[str, str] | None = None


class ReviewContext(BaseModel):
    """
    Stores environment information gathered during the
    assessment context collection phase.
    """

    client_name: str

    remote_access_solution: RemoteAccessPlatform

    identity_provider: str | None = None

    vpn_authentication_method: str | None = None

    pra_authentication_source: str | None = None

    tunnel_type: str | None = None

    certificate_authority: str | None = None

    split_tunnel_mode: str | None = None

    context_notes: dict[str, str] = Field(default_factory=dict)


class QuestionResponse(BaseModel):
    """
    Represents the assessor's response to a single question.
    """

    finding_id: str

    answer: AuditAnswer

    notes: str | None = None


class Question(BaseModel):
    """
    Represents a single audit question loaded from questions.yaml.

    Each question contains:
    - The review question presented to the assessor
    - Expected compliance state
    - Vulnerability mapping
    - Positive observation text
    - Remediation guidance
    - Vendor-specific navigation hints

    Questions are data-driven and should be maintained
    exclusively within the YAML configuration rather than
    hard-coded within the application.
    """

    finding_id: str
    finding_title: str
    theme: str

    expected_answer: AuditAnswer

    question: str

    solution_types: list[SolutionType] = Field(
        default_factory=lambda: [
            SolutionType.VPN,
            SolutionType.PRA,
        ]
    )

    description: str
    commentary: str
    solution: str
    positive: str

    good_value: str
    bad_value: str

    hints: dict[str, str] | None = None

    vendors: list[str] = Field(default_factory=lambda: ["all"])


class Finding(BaseModel):
    """
    Represents a non-compliant control identified during
    the assessment.
    """

    finding_id: str
    title: str
    theme: str

    description: str
    commentary: str
    solution: str

    notes: str | None = None


class PositiveObservation(BaseModel):
    """
    Represents a successfully implemented security control.
    """

    finding_id: str
    text: str
    notes: str | None = None


class AssessmentResults(BaseModel):
    """
    Represents the complete outcome of a remote access assessment.

    This model acts as the central object exchanged between
    the review engine and exporters.

    It contains:

    - Review context
    - Recorded responses
    - Findings
    - Positive observations

    Exporters should consume this model instead of directly
    accessing the review engine or raw YAML data.
    """

    context: ReviewContext

    findings: list[Finding] = Field(default_factory=list)

    positives: list[PositiveObservation] = Field(default_factory=list)

    responses: list[QuestionResponse] = Field(default_factory=list)