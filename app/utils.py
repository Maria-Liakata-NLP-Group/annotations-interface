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


class SubLabelsAClient(Enum):
    """Enum for psychotherapy annotation label A for the client"""

    attachment = "attachment"
    identity = "identity"
    security = "security"
    excitement = "excitement/interest/joy"
    other = "other"


class SubLabelsATherapist(Enum):
    """Enum for psychotherapy annotation label A for the therapist"""

    emotional = "emotional empathy, encouragement, warmth"
    cognitive = "cognitive empathy (empathic accuracy)"
    respect = "respect, appreciation"
    calming = "calming, down-regulating"
    other = "other"


class SubLabelsBClient(Enum):
    """Enum for psychotherapy annotation label B for the client"""

    attachment = "other's response to attachment needs"
    identity = "other's response to identity needs"
    security = "other's response to security needs"
    excitement = "other's response to excitement needs"
    other = "other"


class SubLabelsBTherapist(Enum):
    """Enum for psychotherapy annotation label B for the therapist"""

    interpretation = "interpretation"
    reframing = "reframing"
    reflection = "reflection"
    transference = "transference"
    other = "other"


class SubLabelsCClient(Enum):
    """Enum for psychotherapy annotation label C for the client"""

    acceptance = "self acceptance, care and compassion"
    esteem = "self esteem"
    fight = "fight"
    flight = "flight"
    other = "other"


class SubLabelsCTherapist(Enum):
    """Enum for psychotherapy annotation label C for the therapist"""

    questions = "questions"
    exploration = "exploration and expansion"
    upregulation = "upregulation of emotion"
    other = "other"


class SubLabelsDClient(Enum):
    """Enum for psychotherapy annotation label D for the client"""

    hard_negative = "hard negative"
    soft_negative = "soft negative"
    neutral = "neutral"
    positive = "positive"


class SubLabelsDTherapist(Enum):
    """Enum for psychotherapy annotation label D for the therapist"""

    restructuring = "cognitive restructuring"
    suggest_change = "suggests change in behavior or behavioral activation"
    encouragement = "encourages the patient to think or do things they are afraid of"
    advice = "provides advice, sets an agenda"
    other = "other"


class SubLabelsEClient(Enum):
    """Enum for psychotherapy annotation label E for the client"""

    insight = "insight"


class SubLabelsETherapist(Enum):
    """Enum for psychotherapy annotation label E for the therapist"""

    general_helpfulness = "general helpfulness"


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

    label_a_client = "Need"
    label_a_therapist = "Supportive"
    label_b_client = "Response of Other"
    label_b_therapist = "Expressive"
    label_c_client = "Response of Self"
    label_c_therapist = "Exploratory"
    label_d_client = "Emotional experience and regulation"
    label_d_therapist = "Directive"
    label_e_client = "Insight"
    label_e_therapist = "General helpfulness"
    label_e = "label E"
