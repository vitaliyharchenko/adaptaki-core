from enum import StrEnum


class NodeType(StrEnum):
    CONCEPT = "concept"
    SKILL = "skill"
    LAW = "law"
    CASE = "case"


class RelationType(StrEnum):
    PREREQUISITE = "prerequisite"
    PART_OF = "part_of"
    DEPENDS_ON = "depends_on"

