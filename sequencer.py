from synth_controller import SynthController
import time
import glob
import random
import sched

class Sequencer:
    def __init__(self):
        self._groups = []
        self._is_playing = set()
        self._scheduler = sched.scheduler(time.time, time.sleep)
        SynthController.kill_potential_engine_from_previous_process()
        self._synth = SynthController()
        self._synth.launch_engine()
        self._synth.connect(self._synth.lang_port)

    def play(self, sound, pan=0, fade=None, gain=0, looped=0):
        if fade is None:
            if looped == 0:
                fade = 0
            else:
                fade = 0.1
        self._synth.play(sound, pan, fade, gain, looped)
        self._is_playing.add(sound)
        if looped == 0:
            self._scheduler.enter(
                delay=self._synth.get_duration(sound),
                priority=1,
                action=self._stopped_playing,
                argument=[sound])

    def is_playing(self, sound):
        return sound in self._is_playing

    def _stopped_playing(self, sound):
        self._is_playing.remove(sound)

    def load_sounds(self, pattern):
        for sound in glob.glob(pattern):
            self.load_sound(sound)

    def load_sound(self, *args, **kwargs):
        self._synth.load_sound(*args, **kwargs)

    def add_group(self, pattern):
        group = Group(self)
        for sound in glob.glob(pattern):
            group.add(sound)
        self._groups.append(group)

    def run_main_loop(self):
        while True:
            self._process()
            time.sleep(.1)

    def _process(self):
        self._scheduler.run()
        for group in self._groups:
            group.process()

class Group:
    def __init__(self, sequencer):
        self._sequencer = sequencer
        self._sounds = []
        self._active_sound = None

    def add(self, sound):
        self._sounds.append(sound)

    def process(self):
        if self._active_sound is not None:
            print "is_playing(%s)=%s" % (self._active_sound, self._sequencer.is_playing(self._active_sound))
            if not self._sequencer.is_playing(self._active_sound):
                self._active_sound = None

        if self._active_sound is None:
            self._activate(random.choice(self._sounds))

    def _activate(self, sound):
        self._sequencer.play(sound)
        self._active_sound = sound
