import unittest
from atobject import Circle
from effect import FadeIn, FadeOut, AtAnimation
old_time = 5000
import time

class TestAtEffect(unittest.TestCase):
  def test_fadein(self):
    circle = Circle(radius=1, opacity=0)
    fadein = FadeIn(circle)
    self.assertEqual(fadein.duration, 1000)
    self.assertEqual(fadein.start, 0)
    self.assertEqual(fadein.end, 1000)
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
    self.assertEqual(fadeout.start, 0)
    self.assertEqual(fadeout.end, 1000)
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


if __name__ == "__main__":
  circle = Circle(radius=1, opacity=0)
  fadein = FadeIn(circle, duration=2000, start=5000)
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