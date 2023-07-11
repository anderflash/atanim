from threading import Thread
import time
from typing import List
from bisect import insort
class Effect:
  def __init__(self, duration=1000, start=None, end=None) -> None:
    if end is None and start is not None and duration is not None:
      end = start + duration
    self.duration = duration
    self.start = start
    self.end = end
    self.active = False

  def apply(self, proportion: float):
    pass

  def update_start(self, properties=None):
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

# How to set it in a more general way (e.g., non-fade effects before/after it)
class Fade(Effect):
  def __init__(self, atobject, opacity_end, opacity_start=None, **kwargs) -> None:
    super().__init__(**kwargs)
    self.atobject = atobject
    self.opacity_start_param = opacity_start # if None, then opacity_start depends on previous effects
    self.opacity_start = opacity_start
    self.opacity_end = opacity_end

  def update_start(self, properties=None):
    if self.opacity_start_param is None:
      self.opacity_start = self.atobject.opacity

  def apply(self, proportion: float):
    proportion = max(min(proportion, 1), 0)
    self.atobject.opacity = self.opacity_start + (self.opacity_end-self.opacity_start)*proportion

class FadeIn(Fade):
  def __init__(self, atobject, opacity_end=1.0, **kwargs) -> None:
    super().__init__(atobject, opacity_end=opacity_end, **kwargs)

class FadeOut(Fade):
  def __init__(self, atobject, opacity_end=0.0, **kwargs) -> None:
    super().__init__(atobject, opacity_end=opacity_end, **kwargs)


from enum import Enum

class TimelineSeekPosition(Enum):
  START=0
  CURRENT=1
  END=2

class Timeline():
  def __init__(self) -> None:
    self.layers:List[List[Effect]] = [[]]
    self.current_time = 0
    self.duration = 0
    self.effect_layer = {}
    self.playing = False
    self.frame_index = 0
    self.times = [] # All start and end times of all effects in a sorted way
    self.effects_sorted_by_start: List[Effect] = [] # list of effects ordered by Effect.start
    self.effects_sorted_by_end: List[Effect] = [] # list of effects ordered by Effect.end
    self._on_frame_handlers = []
    self._on_playing_handlers = []
    self._on_paused_handlers = []

  def find_layer_space_for_effect(self, effect: Effect, layer_idx: int):
    assert layer_idx >= 0 and layer_idx < len(self.layers)
    layer = self.layers[layer_idx]
    leffect_idx = -1
    while leffect_idx + 1 < len(layer) and layer[leffect_idx + 1].end <= effect.start: leffect_idx += 1
    reffect_idx = leffect_idx + 1 # Right effect (just next to left effect)
    start = layer[leffect_idx].end if leffect_idx != -1 else 0
    end = layer[reffect_idx].start if reffect_idx < len(layer) else start + effect.duration
    if end-start >= effect.duration:
      return reffect_idx
    return None

  def find_layer_for_effect(self, effect:Effect):
    for layer_idx, layer in enumerate(self.layers):
      if len(layer) == 0: # Empty layer, 
        return layer, layer_idx, 0
      else:
        reffect_idx = self.find_layer_space_for_effect(effect, layer_idx)
        if reffect_idx is not None:
          return layer, layer_idx, reffect_idx
    return None, None, None

  def _add_to_sorted_lists(self, effect: Effect):
    insort(self.effects_sorted_by_start, effect, key=lambda eff: eff.start)
    insort(self.effects_sorted_by_end,   effect, key=lambda eff: eff.end)
    if effect.start not in self.times:
      insort(self.times, effect.start)
    if effect.end not in self.times:
      insort(self.times, effect.end)

  def add(self, effect: Effect, layer_idx:int=None, start:float=None):
    """
    - User adds effect with no start: append to the end of the timeline
    - User adds effect with start: choose best layer (new layer if can't fit)
    - User also specify layer: try fitting, otherwise generate LookupError
    - User specify layer_idx larger than number of layers: create it (and intermediate ones)
    """
    # Function argument has priority
    if start is not None:
      effect.start = start
    elif effect.start is None:
      effect.start = self.duration
    effect.end = effect.start + effect.duration
    self.duration = max(self.duration, effect.end)

    if layer_idx is not None:
      # User adds effect to a new layer #layer_idx
      # Add intermediate layers if necessary
      if layer_idx >= len(self.layers):
        while len(self.layers) < layer_idx: self.layers.append([])
        self.layers.append([effect])
        self.effect_layer[effect] = (layer_idx, 0)

      # User specified existing layer (just check if it fits)
      else:
        insert_idx = self.find_layer_space_for_effect(effect, layer_idx)
        if insert_idx is None:
          raise LookupError('Cannot fit effect into Layer')
        else:
          layer = self.layers[layer_idx]
          # Fix effect_layer position for all effects after the newly added one
          for effect_idx in range(insert_idx, len(layer)):
            cur_effect = layer[effect_idx]
            effect_info = self.effect_layer[cur_effect]
            self.effect_layer[cur_effect] = (layer_idx, effect_info[1]+1)
          layer.insert(insert_idx, effect)
          self.effect_layer[effect] = (layer_idx, insert_idx)
    else:
      # Try adding it into layer 0, otherwise layer 1, and so on.
      layer, layer_idx, insert_idx = self.find_layer_for_effect(effect)
      if layer is None:
        self.layers.append([effect])
        self.effect_layer[effect] = (len(self.layers)-1, 0)
      else:
        layer.insert(insert_idx, effect)
        self.effect_layer[effect] = (layer_idx, insert_idx)

    # In any success case, add effect to the sorted lists
    self._add_to_sorted_lists(effect)

  def seek(self, time, relative_to: TimelineSeekPosition=TimelineSeekPosition.START):
    """
    Apply all necessary effects to reproduce current state of the animation at the to specified seeking position,
    which is relative to the start (default), current position and end of the timeline.

    Params
    ------
    time:
    relative_to: start, relative to current position or from the end
    """

    # We have to go through the timeline between current time and new_current,
    # get all those events (start and end of active effects), and interpolate
    # them sequentially (forward if current <= new_current or backwards otherwise).

    # get all times between current and new_current
    if relative_to == TimelineSeekPosition.CURRENT:
      time += self.current_time
    elif relative_to == TimelineSeekPosition.END:
      time = self.duration - time
    forward = time >= self.current_time
    start, end = (self.current_time, time) if forward else (time, self.current_time)
    times = [start]+[t for t in self.times if start < t < end]+[end]
    if not forward:
      times.reverse()

    effects_sorted = self.effects_sorted_by_start if forward else self.effects_sorted_by_end

    # for each time, interpolate active effects
    # ieffect_first represents the first active effect (updated when this effect is no more active)
    # ieffect represents the current effect

    ieffect_first = 0 if forward else len(effects_sorted)-1
    for t in times:
      # exclude past effects (future ones if backward)
      compare = lambda effect, t: (effect.end < t if forward else effect.start > t)
      while ieffect_first < len(effects_sorted) and ieffect_first >= 0 and compare(effect:=effects_sorted[ieffect_first], t):
        ieffect_first += 1 if forward else -1
        effect.active = False

      # apply all active effects
      ieffect = ieffect_first
      while ieffect < len(effects_sorted) and ieffect >= 0 and (effect := effects_sorted[ieffect]).start <= t and effect.end >= t:
        if (t == effect.start and forward):
          effect.update_start()
        effect.apply((t-effect.start)/effect.duration)
        effect.active = True
        ieffect += 1 if forward else -1
    self.current_time = max(min(time, self.duration), 0)


  def on_frame(self, callback):
    self._on_frame_handlers.append(callback)

  def on_paused(self, callback):
    self._on_paused_handlers.append(callback)

  def on_playing(self, callback):
    self._on_playing_handlers.append(callback)

  def play(self, frame_rate: float, blocking=False, frame_index:int=None):
    self.frame_rate = frame_rate
    self.frame_duration = 1.0/frame_rate
    if self.frame_index is not None:
      self.frame_index = frame_index
    self.playing = True
    for handler in self._on_playing_handlers:
      handler(self)
    thr = Thread(target=self._anim_thread)
    thr.start()
    if blocking:
      thr.join()

  def _anim_thread(self):
    old_time = time.time()
    while self.playing and self.current_time <= self.duration:
      self.seek(self.frame_duration*1000, TimelineSeekPosition.CURRENT)
      for handler in self._on_frame_handlers:
        handler(self)
      if self.current_time == self.duration:
        break
      self.frame_index += 1
      cur_time = time.time()
      time.sleep(min(self.frame_duration - (cur_time-old_time), 0))
      old_time = cur_time
    for handler in self._on_paused_handlers:
      handler(self)

  def pause(self):
    self.playing = False
