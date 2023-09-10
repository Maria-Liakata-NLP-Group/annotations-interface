"""
Utility classes for models.py
"""
from enum import Enum


class DatasetType(Enum):
    """Enum for dataset types"""

    sm_thread = "Social Media Thread"
    psychotherapy = "Psychotherapy Session"


class Permission:
    """Permissions for user roles"""

    READ = 1  # read datasets
    WRITE = 2  # annotate datasets
    ADMIN = 4  # admin


### SOCIAL MEDIA ANNOTATIONS ###


class SMAnnotationType(Enum):
    """Enum for social media annotation types"""

    escalation = "Escalation"
    switch = "Switch"


### PSYCHOTHERAPY ANNOTATIONS ###


# Sublabels for Client/Patient
class SubLabelsAClient(Enum):
    """Enum for psychotherapy annotation label A for the client"""

    attachment = "attachment"
    identity = "identity"
    security = "security"
    excitement = "excitement/interest/joy"
    other = "other"


class SubLabelsBClient(Enum):
    """Enum for psychotherapy annotation label B for the client"""

    attachment = "other's response to attachment needs"
    identity = "other's response to identity needs"
    security = "other's response to security needs"
    excitement = "other's response to excitement needs"
    other = "other"


class SubLabelsCClient(Enum):
    """Enum for psychotherapy annotation label C for the client"""

    acceptance = "self acceptance, care and compassion"
    esteem = "self esteem"
    fight = "fight"
    flight = "flight"
    other = "other"


class SubLabelsDClient(Enum):
    """Enum for psychotherapy annotation label D for the client"""

    hard_negative = "hard negative"
    soft_negative = "soft negative"
    neutral = "neutral"
    positive = "positive"


class SubLabelsEClient(Enum):
    """Enum for psychotherapy annotation label E for the client"""

    insight = "insight"


# Sublabels for Therapist


class SubLabelsATherapist(Enum):
    """Enum for psychotherapy annotation label A for the therapist"""

    emotional = "emotional empathy, encouragement, warmth"
    cognitive = "cognitive empathy (empathic accuracy)"
    respect = "respect, appreciation"
    calming = "calming, down-regulating"
    other = "other"


class SubLabelsBTherapist(Enum):
    """Enum for psychotherapy annotation label B for the therapist"""

    interpretation = "interpretation"
    reframing = "reframing"
    reflection = "reflection"
    transference = "transference"
    other = "other"


class SubLabelsCTherapist(Enum):
    """Enum for psychotherapy annotation label C for the therapist"""

    questions = "questions"
    exploration = "exploration and expansion"
    upregulation = "upregulation of emotion"
    other = "other"


class SubLabelsDTherapist(Enum):
    """Enum for psychotherapy annotation label D for the therapist"""

    restructuring = "cognitive restructuring"
    suggest_change = "suggests change in behavior or behavioral activation"
    encouragement = "encourages the patient to think or do things they are afraid of"
    advice = "provides advice, sets an agenda"
    other = "other"


class SubLabelsETherapist(Enum):
    """Enum for psychotherapy annotation label E for the therapist"""

    general_helpfulness = "general helpfulness"


# Sublabels for Dyad
class SubLabelsADyad(Enum):
    """Enum for psychotherapy annotation label A for the dyad"""

    bond = "bond"
    tasks_goals = "tasks and goals"


class SubLabelsBDyad(Enum):
    """Enum for psychotherapy annotation label B for the dyad"""

    confrontational = "confrontational rupture"
    withdrawal = "withdrawal rupture"
    other = "other"


# Label strengths for Client/Patient
class LabelStrengthAClient(Enum):
    """Enum for psychotherapy annotation label A strength for the client"""

    highly_maladaptive = "1. highly maladaptive"
    very_maladaptive = "2. very maladaptive"
    moderately_adaptive = "3. moderately adaptive/maladaptive"
    very_adaptive = "4. very adaptive"
    highly_adaptive = "5. highly adaptive"


class LabelStrengthBClient(Enum):
    """Enum for psychotherapy annotation label B strength for the client"""

    highly_maladaptive = "1. highly maladaptive"
    very_maladaptive = "2. very maladaptive"
    moderately_adaptive = "3. moderately adaptive/maladaptive"
    very_adaptive = "4. very adaptive"
    highly_adaptive = "5. highly adaptive"


class LabelStrengthCClient(Enum):
    """Enum for psychotherapy annotation label C strength for the client"""

    highly_maladaptive = "1. highly maladaptive"
    very_maladaptive = "2. very maladaptive"
    moderately_adaptive = "3. moderately adaptive/maladaptive"
    very_adaptive = "4. very adaptive"
    highly_adaptive = "5. highly adaptive"


class LabelStrengthDClient(Enum):
    """Enum for psychotherapy annotation label D strength for the client"""

    highly_maladaptive = "1. highly maladaptive"
    very_maladaptive = "2. very maladaptive"
    moderately_adaptive = "3. moderately adaptive/maladaptive"
    very_adaptive = "4. very adaptive"
    highly_adaptive = "5. highly adaptive"


class LabelStrengthEClient(Enum):
    """Enum for psychotherapy annotation label E strength for the client"""

    no_recognition = "1. no recognition"
    low_recognition = "2. low recognition"
    moderate_recognition = "3. moderate recognition"
    good_recognition = "4. good recognition"
    excellent_recognition = "5. excellent recognition (Aha! moment)"


# Label strengths for Therapist
class LabelStrengthATherapist(Enum):
    """Enum for psychotherapy annotation label A strength for the therapist"""

    low = "1. low quality"
    medium = "3. medium quality"
    high = "5. high quality"


class LabelStrengthBTherapist(Enum):
    """Enum for psychotherapy annotation label B strength for the therapist"""

    low = "1. low quality"
    medium = "3. medium quality"
    high = "5. high quality"


class LabelStrengthCTherapist(Enum):
    """Enum for psychotherapy annotation label C strength for the therapist"""

    low = "1. low quality"
    medium = "3. medium quality"
    high = "5. high quality"


class LabelStrengthDTherapist(Enum):
    """Enum for psychotherapy annotation label D strength for the therapist"""

    low = "1. low quality"
    medium = "3. medium quality"
    high = "5. high quality"


class LabelStrengthETherapist(Enum):
    """Enum for psychotherapy annotation label E strength for the therapist"""

    low = "1. low quality"
    medium = "3. medium quality"
    high = "5. high quality"


# Label strengths for Dyad
class LabelStrengthADyad(Enum):
    """Enum for psychotherapy annotation label A strength for the dyad"""

    low = "1. low alliance/collaboration/reciprocity"
    medium = "3. moderate alliance/collaboration/reciprocity"
    high = "5. high alliance/collaboration/reciprocity"


class LabelStrengthBDyad(Enum):
    """Enum for psychotherapy annotation label B strength for the dyad"""

    high = "1. tension is high"
    medium = "3. tension is moderate"
    low = "5. tension is low"


# Speaker types
class Speaker(Enum):
    """Speaker in a psychotherapy session"""

    client = "client"
    therapist = "therapist"
    dyad = "dyad"


# Label names
class LabelNames(Enum):
    """Enum for psychotherapy annotation label names"""

    label_a_client = "Need"
    label_a_therapist = "Supportive"
    label_a_dyad = "Alliance/Reciprocity"
    label_b_dyad = "Tension"
    label_b_client = "Response of Other"
    label_b_therapist = "Expressive"
    label_c_client = "Response of Self"
    label_c_therapist = "Exploratory"
    label_d_client = "Emotional experience and regulation"
    label_d_therapist = "Directive"
    label_e_client = "Insight"
    label_e_therapist = "General helpfulness"
