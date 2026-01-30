from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from apps.tasks.domain.enums import TaskType


@dataclass(frozen=True)
class CheckResult:
    is_correct: bool
    score: Decimal
    max_score: Decimal
    applied_scoring_policy: dict


def check_task_answer(task, answer_payload: dict) -> CheckResult:
    """
    Проверяет ответ пользователя для конкретного задания и возвращает результат проверки.

    Пример:
        result = check_task_answer(task, {"value": "масса"})
        # result.is_correct -> True/False
        # result.score -> Decimal("1")
    """
    task_type = task.task_type
    answer_key = task.answer_key or {}

    if task_type == TaskType.SHORT_TEXT.value:
        is_correct = _check_short_text(answer_key, answer_payload)
    elif task_type == TaskType.NUMBER.value:
        is_correct = _check_number(answer_key, answer_payload)
    elif task_type == TaskType.SINGLE_CHOICE.value:
        is_correct = _check_single_choice(answer_key, answer_payload)
    elif task_type == TaskType.MULTI_CHOICE.value:
        is_correct = _check_multi_choice(answer_key, answer_payload)
    elif task_type == TaskType.MATCH.value:
        is_correct = _check_match(answer_key, answer_payload)
    else:
        is_correct = False

    max_score = Decimal(str(answer_key.get("max_score", 1)))
    score = max_score if is_correct else Decimal("0")

    return CheckResult(
        is_correct=is_correct,
        score=score,
        max_score=max_score,
        applied_scoring_policy={"mode": "binary"},
    )


def _check_short_text(answer_key: dict, answer_payload: dict) -> bool:
    """
    Проверка короткого текста: сравнивает ответ с набором допустимых значений.

    Пример:
        answer_key = {"correct": ["масса", "вес"], "case_sensitive": False}
        answer_payload = {"value": "МаСса"}
        # вернет True
    """
    correct_values = answer_key.get("correct") or []
    if isinstance(correct_values, str):
        correct_values = [correct_values]

    answer_value = _extract_value(answer_payload)
    if answer_value is None:
        return False

    case_sensitive = bool(answer_key.get("case_sensitive", False))
    strip_value = bool(answer_key.get("strip", True))

    answer_value = _normalize_text(answer_value, case_sensitive=case_sensitive, strip_value=strip_value)
    for candidate in correct_values:
        candidate = _normalize_text(candidate, case_sensitive=case_sensitive, strip_value=strip_value)
        if answer_value == candidate:
            return True
    return False


def _check_number(answer_key: dict, answer_payload: dict) -> bool:
    """
    Проверка числового ответа с допустимой погрешностью.

    Пример:
        answer_key = {"correct": [3.14], "tolerance": 0.01}
        answer_payload = {"value": "3.141"}
        # вернет True
    """
    correct_values = answer_key.get("correct")
    tolerance = Decimal(str(answer_key.get("tolerance", 0)))

    if correct_values is None:
        return False

    if not isinstance(correct_values, (list, tuple)):
        correct_values = [correct_values]

    answer_value = _extract_value(answer_payload)
    if answer_value is None:
        return False

    answer_number = _to_decimal(answer_value)
    if answer_number is None:
        return False

    for candidate in correct_values:
        candidate_number = _to_decimal(candidate)
        if candidate_number is None:
            continue
        if abs(answer_number - candidate_number) <= tolerance:
            return True
    return False


def _check_single_choice(answer_key: dict, answer_payload: dict) -> bool:
    """
    Проверка single-choice: сравнивает выбранный вариант с правильным.

    Пример:
        answer_key = {"correct": "B"}
        answer_payload = {"value": "B"}
        # вернет True
    """
    correct_value = answer_key.get("correct")
    if correct_value is None:
        return False

    answer_value = _extract_choice_value(answer_payload)
    if answer_value is None:
        return False

    return str(answer_value) == str(correct_value)


def _check_multi_choice(answer_key: dict, answer_payload: dict) -> bool:
    """
    Проверка multi-choice: множество выбранных вариантов должно совпасть с правильным.

    Пример:
        answer_key = {"correct": ["A", "C"]}
        answer_payload = {"values": ["C", "A"]}
        # вернет True
    """
    correct_values = answer_key.get("correct")
    if correct_values is None:
        return False
    if not isinstance(correct_values, (list, tuple, set)):
        correct_values = [correct_values]

    answer_values = _extract_choice_values(answer_payload)
    if answer_values is None:
        return False

    return set(map(str, answer_values)) == set(map(str, correct_values))


def _check_match(answer_key: dict, answer_payload: dict) -> bool:
    """
    Проверка сопоставления: сравнивает пары слева/справа.

    Пример:
        answer_key = {"correct": {"1": "A", "2": "B"}}
        answer_payload = {"pairs": {"1": "A", "2": "B"}}
        # вернет True
    """
    correct_pairs = answer_key.get("correct")
    if not isinstance(correct_pairs, dict):
        return False

    answer_pairs = _extract_pairs(answer_payload)
    if answer_pairs is None:
        return False

    return {str(k): str(v) for k, v in answer_pairs.items()} == {
        str(k): str(v) for k, v in correct_pairs.items()
    }


def _extract_value(answer_payload) -> str | None:
    """
    Достает строковое значение из payload.

    Пример:
        _extract_value({"value": 42}) -> "42"
        _extract_value("abc") -> "abc"
    """
    if isinstance(answer_payload, dict):
        value = answer_payload.get("value")
    else:
        value = answer_payload
    if value is None:
        return None
    return str(value)


def _extract_choice_value(answer_payload) -> str | None:
    """
    Достает значение выбранного варианта (value/choice/id).

    Пример:
        _extract_choice_value({"choice": "B"}) -> "B"
    """
    if not isinstance(answer_payload, dict):
        return None
    value = answer_payload.get("value")
    if value is None:
        value = answer_payload.get("choice")
    if value is None:
        value = answer_payload.get("id")
    if value is None:
        return None
    return str(value)


def _extract_choice_values(answer_payload) -> list[str] | None:
    """
    Достает список выбранных вариантов (values или value).

    Пример:
        _extract_choice_values({"values": ["A", "C"]}) -> ["A", "C"]
    """
    if not isinstance(answer_payload, dict):
        return None
    values = answer_payload.get("values")
    if values is None:
        values = answer_payload.get("value")
    if values is None:
        return None
    if isinstance(values, (list, tuple, set)):
        return [str(v) for v in values]
    return [str(values)]


def _extract_pairs(answer_payload) -> dict | None:
    """
    Достает пары для сопоставления из dict или списка объектов.

    Пример:
        _extract_pairs({"pairs": [{"left": 1, "right": "A"}]}) -> {"1": "A"}
    """
    if not isinstance(answer_payload, dict):
        return None
    pairs = answer_payload.get("pairs")
    if isinstance(pairs, dict):
        return pairs
    if isinstance(pairs, list):
        result = {}
        for item in pairs:
            if not isinstance(item, dict):
                continue
            left = item.get("left") or item.get("left_id")
            right = item.get("right") or item.get("right_id")
            if left is not None and right is not None:
                result[str(left)] = str(right)
        return result if result else None
    return None


def _normalize_text(value: str, *, case_sensitive: bool, strip_value: bool) -> str:
    """
    Нормализует текст: опционально обрезает пробелы и приводит к нижнему регистру.

    Пример:
        _normalize_text("  МаСса ", case_sensitive=False, strip_value=True) -> "масса"
    """
    normalized = value.strip() if strip_value else value
    return normalized if case_sensitive else normalized.lower()


def _to_decimal(value) -> Decimal | None:
    """
    Пытается привести значение к Decimal (поддерживает запятую как разделитель).

    Пример:
        _to_decimal("3,14") -> Decimal("3.14")
    """
    if value is None:
        return None
    if isinstance(value, str):
        value = value.replace(",", ".").strip()
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
