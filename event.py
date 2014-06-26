class Event:
    CONTROLABLES = "CONTROLABLES"
    SET_PARAM = "SET_PARAM"
    SAVE_PARAMS = "SAVE_PARAMS"
    LOAD_PARAMS = "LOAD_PARAMS"
    PARAMS = "PARAMS"

    def __init__(self, type_, content=None):
        self.type = type_
        self.content = content

    def __str__(self):
        return "Event(%r, %r)" % (self.type, self.content)
