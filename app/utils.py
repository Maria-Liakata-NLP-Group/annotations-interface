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

    attachment = "attachment"
    identity = "identity"
    sublabel3 = "sublabel3"
    sublabel4 = "sublabel4"
    other = "other"


class SubLabelsB(Enum):
    """Enum for psychotherapy annotation label B"""

    sublabel1 = "sublabel1"
    sublabel2 = "sublabel2"
    sublabel3 = "sublabel3"
    sublabel4 = "sublabel4"
    other = "other"


class SubLabelsC(Enum):
    """Enum for psychotherapy annotation label C"""

    sublabel1 = "sublabel1"
    sublabel2 = "sublabel2"
    sublabel3 = "sublabel3"
    sublabel4 = "sublabel4"
    other = "other"


class SubLabelsD(Enum):
    """Enum for psychotherapy annotation label D"""

    sublabel1 = "sublabel1"
    sublabel2 = "sublabel2"
    sublabel3 = "sublabel3"
    sublabel4 = "sublabel4"
    other = "other"


class SubLabelsE(Enum):
    """Enum for psychotherapy annotation label E"""

    sublabel1 = "sublabel1"
    sublabel2 = "sublabel2"
    sublabel3 = "sublabel3"
    sublabel4 = "sublabel4"
    other = "other"


class LabelStrength(Enum):
    """Psychotherapy annotation label strength"""

    high = "high"
    medium = "medium"
    low = "low"


class Speaker(Enum):
    """Speaker in a psychotherapy session"""

    client = "client"
    therapist = "therapist"


class LabelNames(Enum):
    """Enum for psychotherapy annotation label names"""

    label_a = "label A"
    label_b = "label B"
    label_c = "label C"
    label_d = "label D"
    label_e = "label E"
