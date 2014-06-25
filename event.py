class Event:
    CONTROLABLES = "CONTROLABLES"
    SET_PARAM = "SET_PARAM"

    def __init__(self, type_, content):
        self.type = type_
        self.content = content

    def __str__(self):
        return "Event(%r, %r)" % (self.type, self.content)
