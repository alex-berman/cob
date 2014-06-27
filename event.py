class Event:
    CONTROLABLES = "CONTROLABLES"
    SET_TRACK_PARAM = "SET_TRACK_PARAM"
    SET_GLOBAL_PARAM = "SET_GLOBAL_PARAM"
    SAVE_PARAMS = "SAVE_PARAMS"
    LOAD_PARAMS = "LOAD_PARAMS"
    PARAMS = "PARAMS"
    CALIBRATE_COLOUR = "CALIBRATE_COLOUR"

    def __init__(self, type_, content=None):
        self.type = type_
        self.content = content

    def __str__(self):
        return "Event(%r, %r)" % (self.type, self.content)
