from manimlib import *

class Example(Scene):
    def construct(self):
        c = Circle()
        t = Triangle()
        self.play(AnimationGroup(
            Write(c),
            Write(t),
            lag_ratio=1
        ))