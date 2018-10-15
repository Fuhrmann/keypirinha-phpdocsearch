import keypirinha as kp
from .Suggestion import Suggestion

class FunctionSuggestion(Suggestion):
    ITEMCAT = kp.ItemCategory.USER_BASE + 3

    @classmethod
    def has_section_type(cls, section_type):
        return section_type == "refentry"