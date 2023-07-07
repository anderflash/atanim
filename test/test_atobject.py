import unittest
from atobject import Circle
import numpy as np
class TestCircle(unittest.TestCase):
  def test_radius(self):
    circle = Circle(radius=2)
    self.assertEqual (circle.radius, 2)

  def test_area_perimeter(self):
    circle = Circle(radius=2)
    self.assertEqual (circle.area     , circle.radius**2 * np.pi)
    self.assertEqual (circle.perimeter, circle.radius*2  * np.pi)

  def test_local_translation(self):
    circle = Circle(radius=2)
    np.testing.assert_allclose(circle.translation, np.zeros(2),rtol=1e-5, atol=0)
    #self.assertEqual (circle.translation, np.zeros(2))

    circle.translate([2,3])
    np.testing.assert_allclose(circle.translation, np.asarray([2,3]))
    circle.translate([4,6])
    np.testing.assert_allclose(circle.translation, np.asarray([6,9]))

  def test_local_rotation(self):
    circle = Circle(radius=2)
    self.assertEqual(circle.rotation, 0.0)
    np.testing.assert_allclose(circle.transform[:2,:2].flatten(), [1,0,0,1])

    circle.rotate(1)
    self.assertEqual(circle.rotation, 1.0)
    c,s=np.cos(1),np.sin(1)
    np.testing.assert_allclose(circle.transform[:2,:2].flatten(), [c,-s,s,c])

    circle.rotate(4)
    self.assertEqual(circle.rotation, 5.0)
    c,s=np.cos(5),np.sin(5)
    np.testing.assert_allclose(circle.transform[:2,:2].flatten(), [c,-s,s,c])

  def test_local_scale(self):
    circle = Circle(radius=2)
    self.assertEqual(circle._scale_factor, 1)
    np.testing.assert_allclose(circle.transform[:2,:2].flatten(), [1,0,0,1])

    circle.scale(2)
    self.assertEqual(circle._scale_factor, 2)
    np.testing.assert_allclose(circle.transform[:2,:2].flatten(), [2,0,0,2])

    circle.scale(2)
    self.assertEqual(circle._scale_factor, 4)
    np.testing.assert_allclose(circle.transform[:2,:2].flatten(), [4,0,0,4])

    circle.scale(0.25)
    circle.rotate(2)
    circle.scale(2)

    c,s=np.cos(2),np.sin(2)
    np.testing.assert_allclose(circle.transform[:2,:2].flatten(), [2*c,-2*s,2*s,2*c])
    self.assertEqual(circle._scale_factor, 2)


  #   # by default the background is black and the objects have white stroke

  #   circle.appearance