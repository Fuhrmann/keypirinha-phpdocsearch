class Suggestion():
    label = None
    desc = None
    url = None
    section_type = None

    def __init__(self, label, desc, url, section_type):
        self.label = label
        self.desc = desc
        self.url = url
        self.section_type = section_type

    @classmethod
    def has_section_type(cls, section_type):
        return True