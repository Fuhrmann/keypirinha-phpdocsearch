import keypirinha as kp
from .Suggestion import Suggestion

class ClassSuggestion(Suggestion):
    ITEMCAT = kp.ItemCategory.USER_BASE + 2

    @classmethod
    def has_section_type(cls, section_type):
        return section_type in ["phpdoc:classref", "phpdoc:exceptionref"]