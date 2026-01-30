from enum import StrEnum


class TaskType(StrEnum):
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    NUMBER = "number"
    SHORT_TEXT = "short_text"
    MATCH = "match"

    def label(self) -> str:
        return {
            TaskType.SINGLE_CHOICE: "Один вариант",
            TaskType.MULTI_CHOICE: "Несколько вариантов",
            TaskType.NUMBER: "Число",
            TaskType.SHORT_TEXT: "Короткий ответ",
            TaskType.MATCH: "Сопоставление",
        }[self]

    @classmethod
    def label_for(cls, value: str) -> str:
        try:
            return cls(value).label()
        except ValueError:
            return value
