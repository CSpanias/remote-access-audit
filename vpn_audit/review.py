"""
Assessment workflow engine for VPN reviews.

This module contains the core assessment workflow logic and is
responsible for:

- Collecting assessment context
- Selecting applicable audit questions
- Filtering controls by VPN vendor
- Coordinating the assessment workflow

The review engine is intentionally separated from reporting and
export functionality to ensure the assessment logic remains
independent from output formats.
"""

from vpn_audit.models import (
    AssessmentResults,
    AuditAnswer,
    ContextField,
    Finding,
    PositiveObservation,
    Question,
    QuestionResponse,
    ReviewContext,
    VPNVendor,
)
from vpn_audit.loader import (
    load_context_fields,
    load_questions,
)
from vpn_audit.ui import console


def get_applicable_context_fields(
    fields: list[ContextField],
) -> list[ContextField]:
    """
    Return all configured context fields.
    """

    return sorted(
        fields,
        key=lambda field: field.order,
    )


def get_applicable_questions(
    questions: list[Question],
    vendor: VPNVendor,
) -> list[Question]:
    """
    Return all questions applicable to the selected VPN vendor.
    """

    applicable_questions = []

    for question in questions:

        if any(
            vendor_name.lower() == "all"
            for vendor_name in question.vendors
        ):
            applicable_questions.append(question)

        elif vendor.value in question.vendors:
            applicable_questions.append(question)

    return sorted(
        applicable_questions,
        key=lambda q: q.id,
    )


def collect_context(
    fields: list[ContextField],
) -> ReviewContext:
    """
    Collect assessment context information.
    """

    responses = {}
    context_notes = {}

    for field in fields:

        console.print()

        if field.type == "choice" and field.options:
            console.print(f"\n[bold]{field.label}[/bold]")

            for index, option in enumerate(field.options, start=1):
                console.print(f"[cyan]{index}.[/cyan] {option}")

            while True:
                choice = input("> ").strip()

                try:
                    value = field.options[int(choice) - 1]
                    break
                except (ValueError, IndexError):
                    console.print("[red]Invalid selection.[/red]")

        else:
            console.print(f"[bold]{field.label}[/bold]")

            vendor = responses.get("vpn_vendor")
                            
            if field.hints and vendor:
    
                hint = field.hints.get(vendor)
    
                if hint:
                    console.print(f"[bold yellow]Location[/bold yellow]\n{hint}")

            value = input("> ").strip()

        if field.required:

            while not value:

                console.print("[red]This field is required.[/red]")
                value = input("> ").strip()

        if field.type == "integer":
            while True:
                try:
                    value = int(value)

                    if value < 0:
                        raise ValueError

                    break
                
                except ValueError:
                    value = input(f"{field.label} (enter a number): ")

        console.print("[bold]Notes (optional):[/bold]")
        notes = input("> ").strip() or None

        if notes:
            context_notes[field.id] = notes
            
        responses[field.id] = value

    responses["context_notes"] = context_notes

    return ReviewContext(**responses)


def ask_question(
    question: Question,
    vendor: VPNVendor,
    current: int,
    total: int,
) -> QuestionResponse:
    """
    Present a question to the assessor and record the response.
    """

    common_hint = None
    vendor_hint = None

    if question.hints:
        common_hint = question.hints.get("common")
        vendor_hint = question.hints.get(vendor.value)

    console.print()
    console.print(
        f"[bold cyan]Question {current}/{total}:[/bold cyan] "
        f"[bold]{question.question}[/bold]"
    )
    console.print()

    if common_hint:
        console.print(f"[bold blue]Evidence[/bold blue]\n{common_hint}")

    if vendor_hint:
        console.print(f"[bold yellow]Location[/bold yellow]\n{vendor_hint}")

    console.print(
        f"[green]✓ {question.good_value}[/green]"
        f"[red]✗ {question.bad_value}[/red]"
    )

    console.print("1. Compliant")
    console.print("2. Non-Compliant")
    console.print("3. Not Applicable")
    console.print("4. Unknown")

    while True:
        choice = input("> ").strip()

        match choice:
            case "1":
                answer = AuditAnswer.COMPLIANT
                break

            case "2":
                answer = AuditAnswer.NON_COMPLIANT
                break

            case "3":
                answer = AuditAnswer.NOT_APPLICABLE
                break

            case "4":
                answer = AuditAnswer.UNKNOWN
                break

            case _:
                console.print(
                    "[red]Invalid selection.[/red]"
                )

    console.print("[bold]Notes (optional):[/bold]")
    notes = input("> ").strip() or None

    return QuestionResponse(
        question_id=question.id,
        answer=answer,
        notes=notes,
    )


def conduct_review(
    questions: list[Question],
    vendor: VPNVendor,
) -> list[QuestionResponse]:
    """
    Execute the assessment question set.
    """

    responses = []

    total = len(questions)

    for current, question in enumerate(
        questions,
        start=1,
    ):
        response = ask_question(
            question,
            vendor,
            current,
            total,
        )

        responses.append(response)

    return responses


def generate_findings(
    questions: list[Question],
    responses: list[QuestionResponse],
) -> list[Finding]:
    """
    Generate finding records for non-compliant controls.
    """

    findings = []

    questions_by_id = {
        question.id: question
        for question in questions
    }

    for response in responses:
        question = questions_by_id[response.question_id]

        if response.answer in (
            AuditAnswer.NOT_APPLICABLE,
            AuditAnswer.UNKNOWN,
        ):
            continue

        if response.answer != question.expected_answer:
            findings.append(
                Finding(
                    finding_id=question.finding_id,
                    title=question.finding_title,
                    description=question.description.strip(),
                    commentary=question.commentary.strip(),
                    solution=question.solution.strip(),
                    notes=response.notes,
                )
            )

    return findings


def generate_positive_observations(
    questions: list[Question],
    responses: list[QuestionResponse],
) -> list[PositiveObservation]:
    """
    Generate positive observations for compliant controls.
    """

    positives = []

    questions_by_id = {
        question.id: question
        for question in questions
    }

    for response in responses:
        question = questions_by_id[response.question_id]

        if response.answer in (
            AuditAnswer.NOT_APPLICABLE,
            AuditAnswer.UNKNOWN,
        ):
            continue

        if response.answer == question.expected_answer:
            positives.append(
                PositiveObservation(
                    finding_id=question.finding_id,
                    text=question.positive,
                    notes=response.notes,
                )
            )

    return positives


def build_assessment_results(
    context: ReviewContext,
    questions: list[Question],
    responses: list[QuestionResponse],
) -> AssessmentResults:
    """
    Build the final assessment results object.
    """

    findings = generate_findings(
        questions,
        responses,
    )

    positives = generate_positive_observations(
        questions,
        responses,
    )

    return AssessmentResults(
        context=context,
        findings=findings,
        positives=positives,
        responses=responses,
    )


def run_assessment() -> AssessmentResults:
    """
    Execute a complete VPN assessment.
    """

    context_fields = get_applicable_context_fields(
        load_context_fields(),
    )

    context = collect_context(
        context_fields,
    )

    questions = get_applicable_questions(
        load_questions(),
        context.vpn_vendor,
    )

    responses = conduct_review(
        questions,
        context.vpn_vendor,
    )

    return build_assessment_results(
        context=context,
        questions=questions,
        responses=responses,
    )