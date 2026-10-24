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


from remote_access_audit.constants import INITIAL_CONTEXT_FIELDS
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
) -> dict:
    """
    Collect assessment context information.
    """

    responses = {}
    context_notes = {}

    for field in fields:

        console.print()

        if field.type == "choice" and field.options:

            console.print(f"\n[bold]{field.label}[/bold]")

            for index, option in enumerate(
                field.options,
                start=1,
            ):
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

            platform = responses.get("remote_access_solution")

            if field.hints:

                common_hint = field.hints.get("common")

                if common_hint:
                    console.print()
                    console.print(f"[bold blue]Hint[/bold blue]\n{common_hint}")

                if platform:
                    platform_hint = field.hints.get(platform)

                    if platform_hint:
                        console.print(
                            f"[bold yellow]Location[/bold yellow]\n"
                            f"{platform_hint}"
                        )

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
        platform_hint = question.hints.get(platform.value)

    console.print()
    console.print(
        f"[bold cyan]Question {current}/{total}:[/bold cyan] "
        f"[bold]{question.question}[/bold]"
    )
    console.print()

    if common_hint:
        console.print(f"[bold blue]Evidence[/bold blue]\n{common_hint}")

    if platform_hint:
        console.print(f"[bold yellow]Location[/bold yellow]\n{platform_hint}")

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

    for current, question in enumerate(
        questions,
        start=1,
    ):
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
        question = questions_by_id[response.finding_id]

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
        question = questions_by_id[response.finding_id]

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
    Execute a complete remote access assessment.
    """

    all_fields = load_context_fields()

    initial_fields = [
        field
        for field in all_fields
        if field.id in INITIAL_CONTEXT_FIELDS
    ]

    initial_responses = collect_context(initial_fields)

    platform = RemoteAccessPlatform(initial_responses["remote_access_solution"])

    solution_type = platform.solution_type

    remaining_fields = [
        field
        for field in all_fields
        if field.id not in INITIAL_CONTEXT_FIELDS
    ]

    remaining_responses = collect_context(
        get_applicable_context_fields(remaining_fields, solution_type)
    )

    context_notes = {
        **initial_responses.pop("_context_notes", {}),
        **remaining_responses.pop("_context_notes", {}),
    }

    responses = {
        **initial_responses,
        **remaining_responses,
        "context_notes": context_notes,
    }

    context = ReviewContext(**responses)

    questions = get_applicable_questions(
        load_questions(),
        context.remote_access_solution,
        solution_type,
    )

    responses = conduct_review(
        questions,
        context.remote_access_solution,
    )

    return build_assessment_results(
        context=context,
        questions=questions,
        responses=responses,
    )