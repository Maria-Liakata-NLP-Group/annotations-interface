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


class SubLabelsA(Enum):
    """Enum for psychotherapy annotation label A"""

    sublabel1 = "subcategory1"
    sublabel2 = "subcategory2"
    sublabel3 = "subcategory3"
    sublabel4 = "subcategory4"
    sublabel5 = "subcategory5"


class SubLabelsB(Enum):
    """Enum for psychotherapy annotation label B"""

    sublabel1 = "subcategory1"
    sublabel2 = "subcategory2"
    sublabel3 = "subcategory3"
    sublabel4 = "subcategory4"
    sublabel5 = "subcategory5"


class SubLabelsC(Enum):
    """Enum for psychotherapy annotation label C"""

    sublabel1 = "subcategory1"
    sublabel2 = "subcategory2"
    sublabel3 = "subcategory3"
    sublabel4 = "subcategory4"
    sublabel5 = "subcategory5"


class SubLabelsD(Enum):
    """Enum for psychotherapy annotation label D"""

    sublabel1 = "subcategory1"
    sublabel2 = "subcategory2"
    sublabel3 = "subcategory3"
    sublabel4 = "subcategory4"
    sublabel5 = "subcategory5"


class SubLabelsE(Enum):
    """Enum for psychotherapy annotation label E"""

    sublabel1 = "subcategory1"
    sublabel2 = "subcategory2"
    sublabel3 = "subcategory3"
    sublabel4 = "subcategory4"
    sublabel5 = "subcategory5"


class LabelStrength(Enum):
    """Psychotherapy annotation label strength"""

    high = "high"
    medium = "medium"
    low = "low"


class Speaker(Enum):
    """Speaker in a psychotherapy session"""

    client = "client"
    therapist = "therapist"
