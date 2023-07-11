import unittest
from atobject import Circle
from effect import FadeIn, FadeOut, AtAnimation, Timeline
old_time = 5000
import time

class TestAtEffect(unittest.TestCase):
  def test_fadein(self):
    circle = Circle(radius=1, opacity=0)
    fadein = FadeIn(circle)
    self.assertEqual(fadein.duration, 1000)
    self.assertIsNone(fadein.start)
    self.assertIsNone(fadein.end)
    self.assertEqual(fadein.opacity_start, 0)
    self.assertEqual(fadein.opacity_end, 1)

    fadein = FadeIn(circle, duration=2000, start=5000, opacity_end=0.9, opacity_start=0.1)
    self.assertEqual(fadein.duration, 2000)
    self.assertEqual(fadein.start, 5000)
    self.assertEqual(fadein.end, 7000)
    self.assertEqual(fadein.opacity_start, 0.1)
    self.assertEqual(fadein.opacity_end, 0.9)


    fadeinAnim = AtAnimation(fadein)
    self.assertEqual(fadeinAnim.current_time, fadein.start)

    # fadeinAnim.on_tick(self.on_tick) # Not working
    # fadeinAnim.play(blocking=True)

    fadeinAnim.seek(1000) # Go to 1000 (half animation, since duration=2000)
    self.assertEqual(circle.opacity, (0.9+0.1)/2)

  def test_fadeout(self):
    circle = Circle(radius=1)
    fadeout = FadeOut(circle)
    self.assertEqual(fadeout.duration, 1000)
    self.assertIsNone(fadeout.start)
    self.assertIsNone(fadeout.end)
    self.assertEqual(fadeout.opacity_start, 1)
    self.assertEqual(fadeout.opacity_end, 0)

    fadeout = FadeOut(circle, duration=2000, start=5000, opacity_end=0.01, opacity_start=0.9)
    self.assertEqual(fadeout.duration, 2000)
    self.assertEqual(fadeout.start, 5000)
    self.assertEqual(fadeout.end, 7000)
    self.assertEqual(fadeout.opacity_start, 0.9)
    self.assertEqual(fadeout.opacity_end, 0.01)


    fadeinAnim = AtAnimation(fadeout)
    self.assertEqual(fadeinAnim.current_time, fadeout.start)

    # fadeinAnim.on_tick(self.on_tick) # Not working
    # fadeinAnim.play(blocking=True)

    fadeinAnim.seek(1000) # Go to 1000 (half animation, since duration=2000)
    self.assertEqual(circle.opacity, (0.9+0.01)/2)


  # Not working
  # def on_tick(self, current_time):
  #   global old_time
  #   self.assertLess(current_time, old_time)
  #   old_time = current_time
  #   print("oi")

  def test_timeline_add(self):
    circle = Circle(opacity=0)
    tl = Timeline()
    self.assertFalse(tl.playing)
    fadein = FadeIn(circle)
    fadeout = FadeOut(circle)
    tl.add(fadein)
    tl.add(fadeout)
    self.assertEqual(fadein.start, 0)
    self.assertEqual(fadein.end, 1000)
    self.assertEqual(fadeout.start, 1000)
    self.assertEqual(fadeout.end, 2000)
    self.assertTupleEqual(tl.effect_layer[fadein], (0,0))
    self.assertTupleEqual(tl.effect_layer[fadeout],(0,1))
    self.assertListEqual(tl.effects_sorted_by_start, [fadein, fadeout])
    self.assertListEqual(tl.effects_sorted_by_end, [fadein, fadeout])
    self.assertListEqual(tl.times, [0, 1000, 2000])

    fadeout2 = FadeOut(circle, start=500)
    tl.add(fadeout2)
    self.assertEqual(fadeout2.start, 500)
    self.assertEqual(fadeout2.end, 1500)
    self.assertTupleEqual(tl.effect_layer[fadeout2],(1,0))
    self.assertListEqual(tl.effects_sorted_by_start, [fadein, fadeout2, fadeout])
    self.assertListEqual(tl.effects_sorted_by_end, [fadein, fadeout2, fadeout])
    self.assertListEqual(tl.times, [0, 500, 1000, 1500, 2000])

    fadeout3 = FadeOut(circle, duration=500, start=0)
    tl.add(fadeout3, layer_idx=1)
    self.assertEqual(fadeout3.start, 0)
    self.assertEqual(fadeout3.end, 500)
    self.assertTupleEqual(tl.effect_layer[fadeout3],(1,0))
    self.assertTupleEqual(tl.effect_layer[fadeout2],(1,1))
    self.assertListEqual(tl.effects_sorted_by_start, [fadein, fadeout3, fadeout2, fadeout])
    self.assertListEqual(tl.effects_sorted_by_end, [fadeout3, fadein, fadeout2, fadeout])
    self.assertListEqual(tl.times, [0, 500, 1000, 1500, 2000])

    fadeout_error = FadeOut(circle, duration=1000, start=0)
    self.assertRaises(LookupError, tl.add, fadeout_error, layer_idx=1)

  def test_timeline_seek(self):
    circle = Circle(opacity=0)
    tl = Timeline()
    fadein = FadeIn(circle)
    fadeout = FadeOut(circle)
    tl.add(fadein)
    tl.add(fadeout, 1)

    tl.seek(500)
    self.assertEqual(tl.current_time, 500)
    self.assertTrue(fadein.active)
    self.assertFalse(fadeout.active)
    self.assertEqual(circle.opacity, 0.5)

    tl.seek(1500)
    self.assertEqual(tl.current_time, 1500)
    self.assertFalse(fadein.active)
    self.assertTrue(fadeout.active)
    self.assertEqual(circle.opacity, 0.5)

    tl.seek(250)
    self.assertEqual(tl.current_time, 250)
    self.assertTrue(fadein.active)
    self.assertFalse(fadeout.active)
    self.assertEqual(circle.opacity, 0.25)


def demo_timeline():
  circle = Circle(opacity=0)
  tl = Timeline()
  fadein = FadeIn(circle)
  fadeout = FadeOut(circle)
  tl.add(fadein)
  tl.add(fadeout, layer_idx=1, start=fadein.end)
  def on_pause(tl:Timeline):
    print("paused ", tl.current_time)
  def on_play(tl:Timeline):
    print("playing ", tl.current_time)
  def on_frame(tl:Timeline):
    print(f"{tl.frame_index:03}", circle.opacity, tl.current_time)
    if tl.current_time >= 1000:
      tl.pause()
  tl.on_frame(on_frame)
  tl.on_playing(on_play)
  tl.on_paused(on_pause)
  tl.play(frame_rate=60, blocking=True, frame_index=0)

def demo_atanimation():
  circle = Circle(radius=1, opacity=0)
  fadein = FadeIn(circle, duration=1000, start=5000)
  fadeout = FadeOut(circle, duration=2000, start=5000, opacity_start=1)
  def on_tick(animation: AtAnimation):
    global old_time
    old_time = animation.current_time
    print(animation.current_time, circle.opacity)

  fadeinAnim = AtAnimation(fadeout)
  fadeinAnim.on_tick(on_tick)
  fadeinAnim.seek(1000)
  fadeinAnim.play(blocking=True)
  print("FIRST ANIMATION DONE----------------")
  fadeinAnim.seek(0)
  fadeinAnim.play(blocking=True)

if __name__ == "__main__":
  demo_timeline()
  #demo_atanimation()