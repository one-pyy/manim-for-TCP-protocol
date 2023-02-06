from manimlib import *
from threading import Thread

class Example(Scene):
    def construct(self):
        c = Circle()
        c.generate_target()
        c.target.set_fill(GREEN, opacity=0.5)
        c.target.generate_target()
        c.target.
        self.play(
            AnimationGroup(
                c.animate.set_fill(GREEN, opacity=0.5),
                c.animate.move_to(LEFT),
                lag_ratio=0.5
            )
        )
        c.animate.set_fill(GREEN, opacity=0.5).move_to(LEFT)