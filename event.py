class Event:
    SOUNDS = "SOUNDS"

    def __init__(self, type_, content):
        self.type = type_
        self.content = content

    def __str__(self):
        return "Event(%r, %r)" % (self.type, self.content)
