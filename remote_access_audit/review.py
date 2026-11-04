"""
Assessment workflow engine for remote access reviews.

This module contains the core assessment workflow logic and is responsible for:

- Collecting assessment context
- Selecting applicable audit questions
- Filtering controls by platform and solution
- Coordinating the assessment workflow

The review engine is intentionally separated from reporting and export 
functionality to ensure the assessment logic remains independent from output 
formats.
"""


from rich.panel import Panel

from remote_access_audit.models import (
    AssessmentResults,
    AuditAnswer,
    ContextField,
    Finding,
    PositiveObservation,
    Question,
    QuestionResponse,
    ReviewContext,
    RemoteAccessPlatform,
    SolutionType,
)
from remote_access_audit.loader import (
    load_context_fields,
    load_questions,
)
from remote_access_audit.ui import console


def get_fields_by_phase(
    fields: list[ContextField],
    phase: str,
) -> list[ContextField]:
    """
    Return context fields belonging to the specified phase.
    """

    return [
        field
        for field in fields
        if field.phase == phase
    ]


def get_applicable_context_fields(
    fields: list[ContextField],
    solution_type: SolutionType,
) -> list[ContextField]:
    """
    Return all configured context fields.
    """

    return [
        field
        for field in fields
        if solution_type in field.solution_types
    ]


def get_applicable_questions(
    questions: list[Question],
    platform: RemoteAccessPlatform,
    solution_type: SolutionType,
) -> list[Question]:
    """
    Return all questions applicable to the selected platform and solution type.
    """

    applicable_questions = []

    for question in questions:

        if solution_type not in question.solution_types:
            continue

        if any(
            platform_name.lower() == "all"
            for platform_name in question.vendors
        ):
            applicable_questions.append(question)

        elif platform.value in question.vendors:
            applicable_questions.append(question)

    return applicable_questions


def collect_context(
    fields: list[ContextField],
    responses: dict | None = None,
    start: int = 1,
    overall_total: int | None = None,
) -> dict:
    """
    Collect assessment context information.
    """

    responses = responses or {}
    context_notes = responses.pop("_context_notes", {})

    overall_total = overall_total or len(fields)

    for current, field in enumerate(fields, start=start):

        progress = max(1, int((current / overall_total) * 20))
        
        bar = (
            f"[green]{'█' * progress}[/green]"
            f"[dim]{'░' * (20 - progress)}[/dim]"
        )

        console.print(
            f"[bold cyan][CONTEXT {current}/{overall_total}][/bold cyan] "
            f"{bar} "
            f"[bold]{field.label}[/bold]"
        )

        console.print()

        if field.type == "choice" and field.options:

            for index, option in enumerate(
                field.options,
                start=1,
            ):
                console.print(f"[cyan]{index}.[/cyan] {option}")

            while True:

                choice = console.input("> ").strip()

                try:
                    value = field.options[int(choice) - 1]
                    break

                except (ValueError, IndexError):
                    console.print("[red]Invalid selection.[/red]")

        else:

            platform = responses.get("remote_access_solution")

            if field.hints:

                common_hint = field.hints.get("common")

                if common_hint:
                    console.print()
                    console.print(
                        Panel.fit(
                            common_hint.strip(),
                            title="Evidence",
                            border_style="blue",
                        )
                    )

                if platform:
                    platform_hint = field.hints.get(platform)

                    if platform_hint:
                        console.print(
                            Panel.fit(
                                platform_hint.strip(),
                                title="Location",
                                border_style="yellow",
                            )
                        )

            value = console.input("> ").strip()

        if field.required:

            while not value:

                console.print("[red]This field is required.[/red]")

                value = console.input("> ").strip()

        if field.type == "integer":

            while True:

                try:

                    value = int(value)

                    if value < 0:
                        raise ValueError

                    break

                except ValueError:

                    value = console.input("> ").strip()

        console.print()
        console.print("[dim]Notes (optional)[/dim]")

        notes = console.input("> ").strip() or None
        console.print()

        if notes:
            context_notes[field.id] = notes

        responses[field.id] = value

    responses["_context_notes"] = context_notes

    return responses


def ask_question(
    question: Question,
    platform: RemoteAccessPlatform,
    current: int,
    total: int,
) -> QuestionResponse:
    """
    Present a question to the assessor and record the response.
    """

    common_hint = None
    platform_hint = None

    if question.hints:
        common_hint = question.hints.get("common")

        if common_hint:
            common_hint = common_hint.strip()

        platform_hint = question.hints.get(platform.value)

    console.print()
    progress = max(1, int((current / total) * 20))

    bar = (
        f"[green]{'█' * progress}[/green]"
        f"[dim]{'░' * (20 - progress)}[/dim]"
    )

    console.print(
        f"[bold cyan][QUESTION {current}/{total}][/bold cyan] "
        f"{bar} "
        f"[bold]{question.question}[/bold]"
    )
    console.print()

    hint = platform_hint or common_hint

    if hint:
        console.print(
            Panel.fit(
                hint.strip(),
                title="Evidence",
                border_style="blue",
            )
        )

    console.print(
        Panel.fit(
            question.expected_value.strip(),
            title="Expected Value",
            border_style="green",
        )
    )

    console.print("1. Compliant")
    console.print("2. Non-Compliant")
    console.print("3. Not Applicable")
    console.print("4. Unknown")

    while True:
        choice = console.input("> ").strip()

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
                console.print("[red]Invalid selection.[/red]")

    console.print()
    console.print("[dim]Notes (optional)[/dim]")
    notes = console.input("> ").strip() or None

    return QuestionResponse(
        finding_id=question.finding_id,
        answer=answer,
        notes=notes,
    )


def conduct_review(
    questions: list[Question],
    platform: RemoteAccessPlatform,
) -> list[QuestionResponse]:
    """
    Execute the assessment question set.
    """

    responses = []

    total = len(questions)

    for current, question in enumerate(questions, start=1):
        response = ask_question(
            question,
            platform,
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
        question.finding_id: question
        for question in questions
    }

    for response in responses:
        question = questions_by_id.get(response.finding_id)

        if not question:
            continue

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
                    theme=question.theme,
                    description=question.description.strip(),
                    commentary=question.commentary.strip(),
                    solution=question.solution.strip(),
                    expected_value=question.expected_value.strip(),
                    references=question.references,
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
        question.finding_id: question
        for question in questions
    }

    for response in responses:
        question = questions_by_id.get(response.finding_id)

        if not question:
            continue

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

    findings = generate_findings(questions, responses)

    positives = generate_positive_observations(questions, responses)

    return AssessmentResults(
        context=context,
        findings=findings,
        positives=positives,
        responses=responses,
    )


def run_assessment() -> AssessmentResults:
    """
    Execute a complete remote access assessment.

    The assessment workflow consists of:

    - Collecting setup information required to determine the
      remote access solution under review.
    - Collecting solution-specific context fields applicable
      to the selected deployment type.
    - Executing the assessment questionnaire.
    - Generating findings and positive observations.

    The completed assessment results are returned for
    reporting and export.
    """

    all_fields = load_context_fields()

    setup_fields = get_fields_by_phase(all_fields, "setup")

    setup_responses = collect_context(setup_fields)

    platform = RemoteAccessPlatform(
        setup_responses["remote_access_solution"]
    )

    solution_type = platform.solution_type

    context_fields = get_fields_by_phase(all_fields, "context")

    applicable_context_fields = get_applicable_context_fields(
        context_fields,
        solution_type,
    )

    context_responses = collect_context(
        applicable_context_fields,
        setup_responses,
    )

    context_notes = context_responses.pop(
        "_context_notes",
        {},
    )

    responses = {**context_responses, "context_notes": context_notes}

    context = ReviewContext(**responses)

    questions = get_applicable_questions(
        load_questions(),
        context.remote_access_solution,
        solution_type,
    )

    question_responses = conduct_review(
        questions,
        context.remote_access_solution,
    )

    return build_assessment_results(
        context=context,
        questions=questions,
        responses=question_responses,
    )