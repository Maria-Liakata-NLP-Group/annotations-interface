"""
Utility classes for models.py
"""
from enum import Enum


class SMAnnotationType(Enum):
    """Enum for social media annotation types"""

    escalation = "Escalation"
    switch = "Switch"


class DatasetType(Enum):
    """Enum for dataset types"""

    sm_thread = "Social Media Thread"
    psychotherapy = "Psychotherapy Session"


class Permission:
    """Permissions for roles"""

    READ = 1  # read datasets
    WRITE = 2  # annotate datasets
    ADMIN = 4  # admin


class SubcategoriesA(Enum):
    """Enum for psychotherapy annotation label A"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class SubcategoriesB(Enum):
    """Enum for psychotherapy annotation label B"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class SubcategoriesC(Enum):
    """Enum for psychotherapy annotation label C"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class SubcategoriesD(Enum):
    """Enum for psychotherapy annotation label D"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class SubcategoriesE(Enum):
    """Enum for psychotherapy annotation label E"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class LabelStrength(Enum):
    """Psychotherapy annotation label strength"""

    high = "high"
    medium = "medium"
    low = "low"


class Speaker(Enum):
    """Speaker in a psychotherapy session"""

    client = "client"
    therapist = "therapist"
