import time

class Scheduler:
    def __init__(self):
        self._events = []

    def schedule(self, action, delay):
        onset = time.time() + delay
        self._events.append((onset, action))

    def run_scheduled_events(self):
        now = time.time()
        while True:
            some_event_fired = False
            for index, event in enumerate(self._events):
                onset, action = event
                if now >= onset:
                    action()
                    some_event_fired = True
                    self._events.pop(index)
                    break
            if not some_event_fired:
                return
