from enum import StrEnum


class TaskType(StrEnum):
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    NUMBER = "number"
    SHORT_TEXT = "short_text"
    MATCH = "match"

