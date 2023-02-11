from __future__ import annotations
from manimlib import *
from typing import Optional, Mapping, Literal
from threading import Thread
from time import sleep
from functools import partial
import re

FONT = "鍗庢枃妤蜂綋,STKaiti" # 华文楷体
FONT_XK = "鍗庢枃琛屾シ,STXingkai" #华文行楷
scene: 'T' = None # 很不幸, 由于动画组中的mobj不会更新, 所以似乎只能用全局变量把东西先画到画布上了

def cut(obj, sec):
  return [obj[i: i+sec] for i in range(0, len(obj), sec)]

def do_after(func: Callable[[], Any], delay: float=5) -> None:
  aim = scene.get_time() + delay
  def _do_after():
    while scene.get_time() < aim:
      sleep(0.1)
    func()
  
  Thread(target=_do_after, daemon=True).start()

def delete_after(obj: Mobject, delay: float=5) -> None:
  def _delete_after():
    scene.remove(obj)
  
  do_after(_delete_after, delay)

class With:
  @classmethod
  def from_with(cls, *args):
    def func():
      for each in args:
        each.func()
    
    return cls(func)
  
  def __init__(self, run_when_finish: Callable[[], Any]):
    self.func = run_when_finish
  
  def __enter__(self):
    pass
  
  def __exit__(self, *_):
    self.func()

class Subtitle:
  def __init__(self, font=FONT, font_size=30, color=WHITE, position=[0, -3, 0], lsh=0.8, r2c=None):
    # t2c会因为加了换行失效, 不过等用到再改吧
    self.font = font
    self.font_size = font_size
    self.color = color
    self.position = position
    self.lsh = lsh
    self.r2c = r2c or {}
    self.text = Text("")
  
  @staticmethod
  def _r2t(text: Text, r: Mapping[str, Color]):
    for regex, color in r.items():
      for each in re.finditer(regex, text.text.replace("\n", "").replace(" ", "")):
        sp = each.span()
        text[sp[0]: sp[1]].set_color(color)
  
  def clear(self):
    return self.write()
  
  def write(self, text="", tex="", r2c={}):
    last = self.text
    delete_after(last)
    if text:
      r2c = dict(self.r2c, **r2c)
      self.text = Text(text, font=self.font, font_size=self.font_size, color=self.color, lsh=self.lsh).move_to(self.position)
      self._r2t(self.text, r2c)
    else:
      self.text = Tex(tex, font=self.font, font_size=self.font_size, color=self.color).move_to(self.position)
    return AnimationGroup(
      last.animate.set_opacity(-10),
      Write(self.text),
      lag_ratio=0.6
    )
  
  def move(self, position):
    self.position = position
    return self
  
  w = write

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
    self._cp = 0 #completed
    self.vg = VGroup(window)
    self.side_len = self.w[0].get_height()
    self._gen_num()._gen_color()._gen_tag(tag)._gen_brace()
  
  def _flush_window(self):
    distance = self.side_len*self._cp
    return self._w_completed.animate.set_width(distance, True)
  
  def set_completed(self, index, rev=False):
    if self._cp == index or rev and self._cp<=index:
      self._cp=index+1
      return self._flush_window()
    else:
      return AnimationGroup()
  
  def copy(self, tag=None):
    return Window(self.w.copy(), self._w_size, tag or self._tag.text)
  
  def updateing(self):
    def remove_updater():
      self._w_completed.clear_updaters()
      self._w_active.clear_updaters()
      self._w_pending.clear_updaters()
      
    def add_updater():
      self._w_completed.add_updater(
        lambda m: m.align_to(self.w[0], LEFT))
      compute_window_width = lambda now: min(self.side_len*len(self.w) - self._w_completed.get_width(), now)
      self._w_active.add_updater(
        lambda m: m.next_to(self._w_completed, RIGHT, buff=0).set_width(compute_window_width(m.get_width()), True))
      last_width = lambda: self.side_len*len(self.w) - self._w_completed.get_width() - self._w_active.get_width()
      self._w_pending.add_updater(
        lambda m: m.set_width(last_width(), True).next_to(self._w_active, RIGHT, buff=0))
    add_updater()
    # def monitor(func):
    #   last = -1
    #   while True:
    #     now = func()
    #     if now!=last:
    #       last = now
    #       add_updater()
    #     else:
    #       remove_updater()
    # do_after(remove_updater, delay)
  
  def _gen_num(self):
    self._nums = VGroup()
    for index, each in enumerate(self.w):
      self._nums.add(Text(str(index), font_size=int(72*self.side_len)).scale(0.5).move_to(each))
    self.vg.add(self._nums)
    return self
  
  def _gen_tag(self, tag):
    self._tag= Text(tag, font=FONT, font_size=24).next_to(self.w, LEFT)
    self.vg.add(self._tag)
    return self
  
  def _gen_color(self):
    completed_color, active_color, pending_color, opacity = GREEN, YELLOW, GREY_E, 0.5
    side_len = self.side_len
    
    self._w_completed = Rectangle(0.001, side_len).set_stroke(width=0).align_to(self.w[0], UP+LEFT)
    self._w_active = Rectangle(self._w_size*side_len, side_len).set_stroke(width=0).set_fill(active_color, opacity).next_to(self._w_completed, RIGHT, buff=0)
    self._w_pending = Rectangle((len(self.w)-self._w_size)*side_len, side_len).set_stroke(width=0).set_fill(pending_color, opacity).align_to(self.w[0], UP)
    
    #会出现莫名奇妙的自动复制bug, 于是把显示层重新添加一下 FIXIT
    self._w_completed_copy = self._w_completed.copy().set_fill(completed_color, opacity).add_updater(lambda m: m.move_to(self._w_completed).set_width(self._w_completed.get_width(), True))
    
    self.updateing()
    
    self._w_vg = VGroup(self._w_completed, self._w_active, self._w_pending, self._w_completed_copy) # window color
    self.vg.add(self._w_vg)
    return self
  
  def _gen_brace(self):
    self._b_vg = VGroup()
    def get_brace(window: Rectangle, tag, rev=False):
      text = Text(tag, font=FONT, font_size=24, weight="light")
      def create():
        direction = UP
        if rev and window.get_width()<1:
          direction = DOWN
        brace = Brace(window, direction, buff=0).put_at_tip(text)
        return VGroup(brace, text).set_opacity(min(1, window.get_width()))
      
      brace = always_redraw(create)
      # brace = always_redraw(BraceText, window, tag, UP, font_size=30, buff=0)
      
      # f_always(brace.set_opacity, lambda: window.get_width())
      
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
  
  def create(self, run_time=3):
    return AnimationGroup(
      Write(self.w),
      AnimationGroup(
        Write(self._nums),
        Write(self._tag)
      ),
      AnimationGroup(
        FadeIn(self._w_vg),
        FadeIn(self._b_vg),
      ),
      lag_ratio=1, run_time=run_time
    )
  
  def set_window_size(self, size):
    self._w_size = size
    return self._w_active.animate.set_width(self.side_len*size, True)

class SlideWindow:
  def __init__(self, sender: Window, reciever: Window, buff=2, center: Optional[list[float]]=None):
    center = center or [0, -0.5, 0]
    
    self.s, self.r = self._both = sender, reciever
    self.vg = VGroup(sender.vg, reciever.vg).arrange(DOWN, buff=buff).move_to(center)
  
  def create(self, run_time=3):
    return AnimationGroup(
      self.s.create(run_time),
      self.r.create(run_time)
    )
  
  def send(self, which: int, success: Literal["success", "lost", "duplicated"]="success", rev=False, run_time=2):
    s, r =self.s, self.r
    if rev:
      s,r = r,s
    
    rect: Rectangle = s.w[which].copy().set_fill(YELLOW, opacity=0.5)
    if success == 'success':
      return AnimationGroup(
        rect.animate.move_to(r.w[which]).set_fill(GREEN).set_opacity(0),
        r.set_completed(which, rev),
        lag_ratio=0.3, run_time=run_time
      )
    elif success == 'lost':
      return AnimationGroup(
        rect.animate.move_to(r.w[which]).set_fill(RED).set_opacity(-1),
        run_time=run_time
      )
    else:
      rect.move_to((r.w[which].get_center()+s.w[which].get_center())/2)
      return AnimationGroup(
        rect.animate.move_to(r.w[which]).set_fill(RED).set_opacity(0),
        r.set_completed(which, rev),
        run_time=run_time
      )
  
  def batch_send(self, *ss: Literal["success", "lost"], rev=False):
    if rev:
      #只需发送ack
      s = (ss or ["success"])[0]
      return self.send(self.r._cp-1, s, rev=True)
    else:
      s = list(ss)+min(self.s._w_size-len(ss), len(self.s.w)-self.s._cp)*["success"]
      return AnimationGroup(
        *[self.send(i+self.s._cp, sc) for i, sc in enumerate(s)],
        lag_ratio=0.2
      )
    
  bs = batch_send


def get_lines(sentence: str, font = FONT, font_size = 36, color = None, stroke_width = 0, buff = 0.5, t2c = None):
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
  def lower_than(self, obj, another_obj):
    o_index = self.mobjects.index(obj)
    ano_index = self.mobjects.index(another_obj)
    if o_index > ano_index:
      self.mobjects.remove(obj)
      self.mobjects.insert(ano_index, obj)

  def arrange_layer(self, *objs: Mobject):
    positions = [self.mobjects.index(obj) for obj in objs]
    positions = sorted(positions)
    for index, position in enumerate(positions):
      self.mobjects[position] = objs[index]
  
  def bottom_layer(self, *objs: Mobject):
    for obj in objs:
      self.mobjects.remove(obj)
      self.mobjects.insert(1, obj)
  
  def play_one_by_one(self, *animations, run_time=3, wait=1):
    animations = list(a for a in animations if a)
    self.play(*animations, run_time=run_time)
    self.wait(wait)
    return partial(self.play_one_by_one, run_time=run_time, wait=wait)
  
  def write_VGroup(self, group: VGroup, run_time=2, wait=1):
    for submob in group:
      self.play(Write(submob, run_time=run_time))
      self.wait(wait)
  
  def show(self, s, t2c={}):
      vg = get_lines(s, t2c=t2c)
      self.write_VGroup(vg)
      self.wait()
      self.play(FadeOut(vg))
      return vg
  
  def introduce_stop_wait_protocol(self):
    introduction = get_lines("""
      TCP停等协议是一种网络传输控制协议。
      其中，发送方等待接收方的确认后再发送下一个数据报文。
      如果发送方发现丢失了某个数据报文，它会重新发送该数据。
      接收方收到数据后会发送确认，告诉发送方该数据已经成功接收。
      (以下进行演示。演示中, 假设每个包的大小为100, 起始约定的序号为0)
    """, t2c={"TCP停等协议": RED, "发送方": BLUE, "接收方": BLUE, "确认": YELLOW, "报文": GREEN, "数据": GREEN})
    self.write_VGroup(introduction)
    
    self.title = introduction[0][:7].copy()
    self.play(self.title.animate.move_to([0, 3.3, 0]).set_color(WHITE).set_height(0.7), 
              FadeOut(introduction))
    
  def show_stop_wait_protocol(self):
    sw = SlideWindow(
      Window.init(num=5, window_size=1, tag="发送方"),
      Window.init(num=5, window_size=1, tag="接收方"),
      center=[-3, -1, 0]
    )
    st = Subtitle(position=[3.5, -1, 0], font_size=30,
                        r2c={r"\[Seq.*?\]": GREEN, r"\[Ack.*?\]": RED, r"..方": BLUE})
    
    (# 懒得打反斜杠了
      self.play_one_by_one(sw.create())
      (st.w("发送方发送一条数据[Seq=0]"), sw.send(0))
      (st.w("接收方收到数据后发送确认[Ack=100]"), sw.send(0, rev=True))
      (st.w("发送方收到了确认\n发送下一条消息[Seq=100]"), sw.send(1))
      (st.w("接收方收到数据后发送确认\n但是发送方没有收到确认[Ack=200]"), sw.send(1, rev=True, success='lost'))
      (st.w("发送方收到确认超时\n发送方重发数据[Seq=100]"), sw.send(1))
      (st.w("接收方根据Seq判断为已收到的数据\n重新发送确认[Ack=200]"), sw.send(1, rev=True))
      (st.w("这次成功了\n但出现了重复的数据包[Ack=200]"), sw.send(1, rev=True, success='duplicated'))
      (st.w("发送方收到了两条ACK\n它抛弃后者\n随后其发送下一条消息[Seq=200]\n但是接收方没有收到"), sw.send(2, success='lost'))
      (st.w("接收方超时\n发送上一条信息的应答[Ack=200]\n(对于接收方来说:\n无法判断发送方是否收到信息)"), sw.send(1, rev=True))
      (st.w("发送方收到上一条的应答[Ack=200]\n忽略, 然后超时\n重新发送[Seq=200]"), sw.send(2))
    )
    st.move([-3.5, -1, 0])
    self.play(sw.vg.animate.shift(6*RIGHT), st.clear())
    (
      self.play_one_by_one()
      (st.w("在TCP停等协议中\n发送方等待接收方的确认后\n再发送下一个数据报文"), sw.send(2, rev=True))
      (st.w("如果发送方接收Ack超时\n它会重新发送该数据\n如果出现数据包重复\n它会忽略"), sw.send(3))
      (st.w("由于停等协议一次只发一个块\n所以不会出现数据包乱序"), sw.send(3, rev=True))
      (st.w("总结:\n停等协议较为简单\n但对通信信道的利用率较低"), sw.send(4))
      (st.w("原因是:\n停等协议把大部分时间都用于\n数据在链路上的传输\n而不是数据的发送与接收"), sw.send(4, rev=True))
    )
    self.play(FadeOut(sw.vg), st.clear(), FadeOut(self.title), run_time=5)
    self.clear()
  
  
  def introduce_sliding_window(self):
    vg = get_lines('''
      为了充分利用通信信道的带宽
      我们需要将更多的时间用在数据的收发上
      由此, 我们引入滑动窗口协议
      一次性发送多个数据包
      而接收方只需要确认最后的数据包即可
    ''', t2c={"带宽": BLUE, "收发": BLUE, "多个数据包": BLUE, "确认": BLUE, "滑动窗口协议": GOLD})
    self.write_VGroup(vg)
    self.wait()
    self.title = vg[2][7:13].copy()
    self.play(FadeOut(vg), self.title.animate.move_to([0, 3.3, 0]).set_color(WHITE).set_height(0.7))
    self.show('''
      当接收方收到不是当时期望的数据包时
      接收方会直接丢弃该数据包
      同时重申自己需要的包
    ''', t2c={"期望": BLUE, "丢弃": RED})
    self.show("""
      滑动窗口的大小是由接收方告诉发送方的
      并且双方都可以在运行过程中动态调整
      接收方可以通过发送确认报文来控制滑动窗口的大小
      以限制发送方的发送速率
    """, t2c={"滑动窗口的大小": BLUE, "动态调整": BLUE})
    self.show("""
      当发送方出现超时等错误时, 即可缩减滑动窗口的大小(拥塞控制)
      当接收方处理不过来时, 也可以通过ACK报文调整滑动窗口的大小
    """, t2c={"错误": RED, "处理不过来": RED, "拥塞控制": BLUE})
    self.show("以下对无差错的情况进行分析\n窗口大小为3, 总数为10", t2c={"无差错": BLUE})
  
  def show_sliding_window_0(self):
    sw = SlideWindow(
      Window.init(num=10, window_size=3, tag="发送方"),
      Window.init(num=10, window_size=3, tag="接收方"),
      center=[-1, -0.6, 0], buff=2.8
    )
    st = Subtitle(position=[3, -0.6, 0])
    self.play(sw.create())
    (
      self.play_one_by_one()
      (sw.bs(), st.w("发送方发送数据包"))
      (sw.bs(rev=True), st.w("接收方收到数据包"))
      (sw.bs(), st.w("循环往复..."))
      (sw.bs(rev=True))
      (sw.bs(), st.move([-3, -0.6, 0]).w("循环往复..."))
      (sw.bs(rev=True))
      (sw.bs())
      (sw.bs(rev=True), st.w("发送完成"))
    )
    self.play(FadeOut(sw.vg), st.clear())
    self.show('''
      以上是无差错的情况
      我们可以清晰感受到滑动窗口的优势
      那么, 如果出现了差错呢?
    ''')
  
  def show_sliding_window_1(self):
    sw = SlideWindow(
      Window.init(num=10, window_size=3, tag="发送方"),
      Window.init(num=10, window_size=3, tag="接收方"),
      center=[-1, -0.7, 0], buff=2.8
    )
    st = Subtitle(position=[3, -0.7, 0],
                  r2c={r"\[Seq.*?\]": GREEN, r"\[Ack.*?\]": PURPLE, r"..方": BLUE, r'乱序|丢失|重复|丢弃': RED, r"拥塞": GOLD})
    self.play(sw.create())
    (
      self.play_one_by_one()
      (sw.bs(), st.w("发送方发送数据包\n[Seq=0] [Seq=100] [Seq=200]"))
      (sw.bs(rev=True), st.w("接收方收到数据包\n[Ack=300]"))
      (sw.bs('success', 'lost'), st.w("有一个包丢失了\n丢失的是[Seq=400]"))
      (sw.bs(rev=True), st.w("接收方收到两个数据包\n[Seq=300] [Seq=500]\n但窗口只前移了一格\n因为第二个不是它当前想要的"))
      (sw.send(5, 'duplicated'), st.w("出现了一个重复的数据包\n[Seq=500]\n但仍然被丢弃"))
      (sw.send(4, 'duplicated'), st.w("缺失的数据包出现了\n[Seq=400]\n窗口前移了一格\n看来发生了乱序"))
      (sw.bs(rev=True), st.w("接收方发送回应报文\n[Ack=500]"))
      (sw.bs(), st.move([-3, -0.7, 0]).w("发送方收到回应报文\n窗口前移\n然后继续发送"))
      (sw.bs(rev=True), st.w("以上已经出现了\n乱序、丢失、重复\n但是, 滑动窗口仍然能够正常工作"))
      (sw.bs(), st.w("在现实中我们发现\n当出现乱序、丢失、重复时\n滑动窗口的效率会大大降低"))
      (sw.bs(rev=True), st.w("通常来说\n这些错误发生在网络拥塞的情况下\n因此, 我们需要对滑动窗口进行改进\n以适应网络拥塞的情况"))
    )
    title = st.text[13:15].copy()
    title.generate_target().move_to([-0.75, 3.3, 0]).set_color(WHITE).set_height(0.7)
    title2 = Text("控制", font=FONT, height=0.7)
    self.play(FadeOut(self.title))
    self.title = VGroup(title, title2).arrange(RIGHT, buff=0.1)
    
    self.play(FadeOut(sw.vg), st.clear(), MoveToTarget(title))
    self.play(FadeIn(title2))
    self.show('''
      在数据传输开始时
      发送方会以较慢的速率发送数据, 以先测试网络的能力
      如果网络状况良好，接收方能够快速接收并回复确认
      则发送方会逐渐增加发送速率，直到达到最大速率
    ''')
    self.show('''
      发送过程中, 发送方维护一个阈值
      当窗口值超过阈值时, 它增加的速度会变缓慢
      否则, 它将以指数级增加
    ''')
  
  def show_sliding_window_2(self):
    sw = SlideWindow(
      Window.init(num=20, side_length=0.6, window_size=1, tag="发送方"),
      Window.init(num=20, side_length=0.6, window_size=6, tag="接收方"),
      center=[0, -0.7, 0], buff=3
    )
    st = Subtitle(position=[3, -0.7, 0],
                  r2c={r"\[size.*?\]": GREEN, r"..方": BLUE, r'乱序|丢失|重复|错误': RED, r"拥塞": GOLD})
    (
      self.play_one_by_one()
      (sw.create())
      (st.w("我们发现发送方的窗口值为1\n这个窗口值会随时间变化\n但最大不超过接收方窗口数 6\n[size=1]"))
      (sw.bs(), st.w("发送方发送了一个数据包"))
      (sw.bs(rev=True), st.w("接收方收到了数据包\n并且发送回应报文"))
      (sw.s.set_window_size(2), st.w("线路很正常\n发送方将窗口值翻倍\n[size=2]"))
      (sw.bs(), st.w("这次仍然发送成功了"))
      (sw.bs(rev=True), st.w("接收方收到了数据包\n并且发送回应报文"))
      (sw.s.set_window_size(4), st.w("线路很正常\n发送方将窗口值增加到4\n[size=4]"))
      (sw.bs())
      (sw.bs(rev=True), st.w("接收方收到了数据包\n并且发送回应报文"))
      (sw.s.set_window_size(6), st.w("发送方想将窗口值增加到8\n但接收方窗口为6\n于是将窗口值设置为6\n[size=6]"))
      (sw.bs("success", "lost"), st.move([-3, -0.7, 0]).w("发送方继续发送数据包\n但是这次丢失了一个"))
      (sw.bs(rev=True), st.w("接收方丢弃了后四个数据包\n并返回ACK报文"))
      (sw.s.set_window_size(1), st.w("发送方发现出现了错误\n于是将窗口值减为1\n并且将阈值设置为当前的一半 3\n[size=1]"))
      (sw.bs(), st.w("发送方重新发送数据包"))
      (sw.bs(rev=True))
      (sw.s.set_window_size(2), st.w("根据规则\n窗口值翻倍\n[size=2]"))
      (sw.bs())
      (sw.bs(rev=True))
      (sw.s.set_window_size(4), st.w("根据规则\n窗口值翻倍\n注意: 此时已经超过阈值\n[size=4]"))
      (sw.bs())
      (sw.bs(rev=True))
      (sw.s.set_window_size(5), st.w("由于已经超过了阈值\n窗口值增加1"))
      (sw.bs())
      (sw.bs(rev=True), st.w("发送完毕"))
    )
    self.play(FadeOut(sw.vg), st.clear())
    self.clear()
  
  def mark(self):
    m = Text("@pyy", font_size=20).to_corner(UR).set_color("#282828")
    self.add(m)
  
  def clear(self):
    super().clear()
    self.mark()
  
  def construct(self):
    global scene
    scene = self
    self.mark()
    self.introduce_stop_wait_protocol()
    self.show_stop_wait_protocol()
    self.introduce_sliding_window()
    self.show_sliding_window_0()
    self.show_sliding_window_1()
    self.show_sliding_window_2()
    self.embed()