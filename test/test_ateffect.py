import unittest
from atobject import Circle
from effect import FadeIn, AtAnimation
old_time = 5000
import time

class TestAtEffect(unittest.TestCase):
  def test_fadein(self):
    circle = Circle(radius=1)
    fadein = FadeIn(circle)
    self.assertEqual(fadein.duration, 1000)
    self.assertEqual(fadein.start, 0)
    self.assertEqual(fadein.end, 1000)

    fadein = FadeIn(circle, duration=2000, start=5000)
    self.assertEqual(fadein.duration, 2000)
    self.assertEqual(fadein.start, 5000)
    self.assertEqual(fadein.end, 7000)

    fadeinAnim = AtAnimation(fadein)
    self.assertEqual(fadeinAnim.current_time, fadein.start)

    # fadeinAnim.on_tick(self.on_tick) # Not working
    # fadeinAnim.play(blocking=True)

    fadeinAnim.seek(1000) # Go to 1000 (half animation, since duration=2000)
    self.assertEqual(circle.opacity, 0.5)


  # Not working
  # def on_tick(self, current_time):
  #   global old_time
  #   self.assertLess(current_time, old_time)
  #   old_time = current_time
  #   print("oi")


if __name__ == "__main__":
  circle = Circle(radius=1, opacity=0)
  fadein = FadeIn(circle)
  fadein = FadeIn(circle, duration=2000, start=5000)
  def on_tick(animation: AtAnimation):
    global old_time
    old_time = animation.current_time
    print(animation.current_time, circle.opacity)

  fadeinAnim = AtAnimation(fadein)
  fadeinAnim.on_tick(on_tick)
  fadeinAnim.seek(1000)
  fadeinAnim.play(blocking=True)
  print("FIRST ANIMATION DONE----------------")
  fadeinAnim.seek(0)
  fadeinAnim.play(blocking=True)