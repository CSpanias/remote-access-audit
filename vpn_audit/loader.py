"""
YAML data loading utilities.

This module is responsible for loading and validating
application data stored in YAML files.

Supported data sources:

- questions.yaml
- context_fields.yaml

All loaded data is validated using the Pydantic models
defined in models.py before being returned to the caller.

This ensures invalid configuration is detected early
during application startup and prevents malformed
assessment content from reaching the review engine.
"""
import yaml

from pathlib import Path
from pydantic import ValidationError

from vpn_audit.models import ContextField, Question


DATA_DIR = Path(__file__).parent / "data"


def _load_yaml(path: Path) -> list[dict]:
    """
    Load and parse a YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed YAML content.

    Raises:
        FileNotFoundError:
            If the file does not exist.

        ValueError:
            If the file is empty or invalid.
    """

    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not data:
        raise ValueError(f"YAML file is empty: {path}")

    return data


def load_questions() -> list[Question]:
    """
    Load all assessment questions.

    Returns:
        List of validated Question objects.
    """

    path = DATA_DIR / "questions.yaml"
    data = _load_yaml(path)

    questions = []

    for item in data:
        try:
            questions.append(
                Question.model_validate(item)
            )

        except ValidationError as exc:
            raise ValueError(
                f"Invalid question definition "
                f"(ID {item.get('id')}, "
                f"Finding: {item.get('finding_id')})"
            ) from exc

    return questions


def load_context_fields() -> list[ContextField]:
    """
    Load context collection fields.

    Returns:
        List of validated ContextField objects.
    """

    path = DATA_DIR / "context_fields.yaml"
    data = _load_yaml(path)

    return [ContextField.model_validate(item) for item in data]


if __name__ == "__main__":
    questions = load_questions()
    fields = load_context_fields()

    print(f"Loaded {len(questions)} questions")
    print(f"Loaded {len(fields)} context fields")