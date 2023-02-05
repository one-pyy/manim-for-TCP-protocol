from __future__ import annotations
from manimlib import *
from typing import Optional
from threading import Thread

FONT = "FiraCode"

class Window:
  @classmethod
  def init(cls, num=10, side_length=1, stroke_color=WHITE, stroke_width=2, window_size=3, tag=""):
    window = VGroup(*list(
      Square(side_length).set_stroke(stroke_color, stroke_width) for _ in range(num)
    )).arrange(RIGHT, buff=0)
    return cls(window, window_size, tag)
  
  def __init__(self, window: VGroup, window_size=3, tag=""):
    self._w_size = window_size
    self.w = window
    self.vg = VGroup(window)
    self._gen_color()._gen_num()._gen_tag(tag)._gen_brace()
  
  def copy(self, tag=None):
    return Window(self.w.copy(), self._w_size, tag or self._tag.text)
  
  def _gen_num(self):
    self._nums = VGroup()
    for index, each in enumerate(self.w):
      self._nums.add(Text(str(index)).scale(0.5).move_to(each))
    self.vg.add(self._nums)
    return self
  
  def _gen_tag(self, tag):
    self._tag= Text(tag, font=FONT, font_size=24).next_to(self.w, LEFT)
    self.vg.add(self._tag)
    return self
  
  def _gen_color(self):
    completed_color, active_color, pending_color, opacity = GREEN, YELLOW, GREY_E, 0.3
    side_len = self.side_len = self.w[0].get_height()
    
    self._w_completed = Rectangle(0.001, side_len).set_stroke(width=0).set_fill(completed_color, opacity).align_to(self.w[0], UP+LEFT)
    self._w_active = Rectangle(self._w_size, side_len).set_stroke(width=0).set_fill(active_color, opacity).align_to(self.w[0], UP)
    self._w_pending = Rectangle(7, side_len).set_stroke(width=0).set_fill(pending_color, opacity).align_to(self.w[0], UP)
    
    self._w_completed.add_updater(
      lambda m: m.align_to(self.w[0], LEFT))
    self._w_active.add_updater(
      lambda m: m.next_to(self._w_completed, RIGHT, buff=0))
    last_width = lambda: side_len*len(self.w) - self._w_completed.get_width() - self._w_active.get_width()
    self._w_pending.add_updater(
      lambda m: m.set_width(last_width(), True).next_to(self._w_active, RIGHT, buff=0))
    
    self._w_vg = VGroup(self._w_completed, self._w_active, self._w_pending) # window color
    self.vg.add(self._w_vg)
    return self
  
  def _gen_brace(self):
    self._b_vg = VGroup()
    def get_brace(window, tag):
      brace = always_redraw(BraceText, window, tag, UP, font_size=30, buff=0)
      
      self._b_vg.add(brace)
      return brace

    self._b_completed = get_brace(self._w_completed, "已完成")
    self._b_active = get_brace(self._w_active, "窗口")
    self._b_pending = get_brace(self._w_pending, "未完成")
    self.vg.add(self._b_vg)
    return self
  
  def r_shift(self, step=1):
    distance = self.side_len*step
    return self._w_completed.animate.set_width(self._w_completed.get_width() + distance, True)
  
  def anim(self, run_time=3):
    return AnimationGroup(
      Write(self.w),
      AnimationGroup(
        Write(self._nums),
        Write(self._tag)
      ),
      AnimationGroup(
        FadeIn(self._w_vg),
        FadeIn(self._b_vgit@github.com:one-pyy/manim-for-TCP-protocol.gitg),
      ),
      lag_ratio=1, run_time=run_time
    )

class SlideWindow:
  def __init__(self, sender: Window, reciever: Window, buff=2, center: Optional[list[float]]=None):
    center = center or [0, -0.5, 0]
    


def get_lines(sentence: str, font = FONT, font_size = 36, color = None, stroke_width = 0, buff = 0.2, t2c = None):
  lines = [line.strip() for line in sentence.strip().splitlines() if line.strip()]
  
  longest_line = max(lines, key = lambda line: len(line))
  longest_line_no = lines.index(longest_line)
  
  group = VGroup(*list(
    Text(line, font = font, font_size = font_size, color = color, stroke_width = stroke_width, t2c = t2c) 
    for line in lines
  )).arrange(DOWN, buff = buff)
  
  for each in group:
    each.align_to(group[longest_line_no], LEFT)
  
  return group


class T(Scene):
  def write_VGroup(self, group: VGroup, run_time=2, wait=1):
    for submob in group:
      self.play(Write(submob, run_time=run_time))
      self.wait(wait)
  
  def introduce_stop_wait_protocol(self):
    introduction = get_lines("""
      TCP停等协议是一种网络传输控制协议。
      其中，发送方等待接收方的确认后再发送下一个数据报文。
      如果发送方发现丢失了某个数据报文，它会重新发送该数据。
      接收方收到数据后会发送确认，告诉发送方该数据已经成功接收。
    """, t2c={"TCP停等协议": RED, "发送方": BLUE, "接收方": BLUE, "确认": YELLOW, "报文": GREEN, "数据": GREEN})
    self.write_VGroup(introduction)
    
    title = introduction[0][:7].copy()
    self.play(title.animate.move_to([0, 3.3, 0]).set_color(WHITE).set_height(0.7), 
              FadeOut(introduction))
    
  def show_stop_wait_protocol(self):
    s = SlideWindow(get_window(), center=[0, -1, 0], sender_window_size=2, receiver_window_size=2)
    s.show(self)
  
  
  # def 介绍滑动窗口(self):
  #   group = VGroup(
  #     Text("")
  #   )
  
  def construct(self):
    pass
    # self.introduce_stop_wait_protocol()
    # self.show_stop_wait_protocol()