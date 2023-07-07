from threading import Thread
import time
class Effect:
  def __init__(self, duration=1000, start=0, end=None) -> None:
    if end is None and start is not None and duration is not None:
      end = start + duration
    self.duration = duration
    self.start = start
    self.end = end

  def apply(proportion: float):
    pass

class AtAnimation:
  """
  Basic Animation class
  """
  def __init__(self, effect: Effect) -> None:
    self.effect = effect
    self.current_time = effect.start
    self.cbs = []

  def on_tick(self, cb):
    self.cbs.append(cb)

  def play(self, blocking=False):
    thr = Thread(target=self._anim_thread)
    thr.start()
    if blocking:
      thr.join()

  def seek(self, current):
    proportion = current/self.effect.duration
    self.current_time = self.effect.start + current
    self.effect.apply(proportion)

  def _anim_thread(self):
    time_resolution = 1e-2
    start = time.time() * 1e3
    offset = (self.current_time - self.effect.start)
    current = start + offset
    while current-start < self.effect.duration:
      delta = (current-start)
      self.current_time = self.effect.start + delta
      proportion = delta/self.effect.duration # 0 to 1
      self.effect.apply(proportion)
      for cb in self.cbs:
        cb(self)
      time.sleep(time_resolution)
      current = time.time() * 1e3 + offset
    self.current_time = self.effect.end
    self.effect.apply(1)
    for cb in self.cbs:
      cb(self)

class FadeIn(Effect):
  def __init__(self, atobject, opacity_start=None, opacity_end=None, **kwargs) -> None:
    super().__init__(**kwargs)
    self.atobject = atobject
    self.opacity_start = self.atobject.opacity if opacity_start is None else opacity_start
    self.opacity_end = 1 if opacity_end is None else opacity_end

  def apply(self, proportion: float):
    self.atobject.opacity = self.opacity_start + (self.opacity_end-self.opacity_start)*proportion