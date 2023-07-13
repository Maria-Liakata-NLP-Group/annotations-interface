"""
Utility classes for models.py
"""
from enum import Enum


class SubcategoriesA(Enum):
    """Subcategories for label A"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class SubcategoriesB(Enum):
    """Subcategories for label B"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class SubcategoriesC(Enum):
    """Subcategories for label C"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class SubcategoriesD(Enum):
    """Subcategories for label D"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class SubcategoriesE(Enum):
    """Subcategories for label E"""

    subcategory1 = "subcategory1"
    subcategory2 = "subcategory2"
    subcategory3 = "subcategory3"
    subcategory4 = "subcategory4"
    subcategory5 = "subcategory5"


class LabelStrength(Enum):
    """Label strength"""

    high = "high"
    medium = "medium"
    low = "low"


class Speaker(Enum):
    """Speaker in a psychotherapy session"""

    client = "client"
    therapist = "therapist"
