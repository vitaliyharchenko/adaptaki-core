from enum import StrEnum


class TestMode(StrEnum):
    SIMPLE = "simple"
    EXAM = "exam"


class AttemptStatus(StrEnum):
    STARTED = "started"
    FINISHED = "finished"
    ABANDONED = "abandoned"

