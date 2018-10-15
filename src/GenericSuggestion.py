import keypirinha as kp
from .Suggestion import Suggestion

class GenericSuggestion(Suggestion):
    ITEMCAT = kp.ItemCategory.USER_BASE + 4

    @classmethod
    def has_section_type(cls, section_type):
        return section_type not in ["phpdoc:classref", "phpdoc:exceptionref", "refentry"]