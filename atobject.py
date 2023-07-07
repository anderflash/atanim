import numpy as np
class AtShape:
  def __init__(self, transform=None, ndim=None, rotation = 0.0, scale_factor=1.0) -> None:
    """
    Params
    ------
    transform: 3x3 or 4x4 matrix
    ndim: dimension of the shape
    """
    if ndim is None:
      if transform is not None:
        ndim = len(transform)
    if transform is None:
      if ndim is not None:
        transform = np.eye(ndim+1)
    else:
      transform = np.asarray(transform)

    self.transform = transform
    self.ndim = ndim
    self._rotation = rotation
    self._scale_factor = scale_factor


class AtGroup(AtShape):
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self.children = []

class Circle(AtShape):
  def __init__(self, radius: float=1.0, **kwargs) -> None:
    super().__init__(ndim=2, **kwargs)
    self.radius = radius

  @property
  def area(self):
    return self.radius**2 * np.pi

  @property
  def perimeter(self):
    return self.radius*2 * np.pi

  @property
  def translation(self):
    return self.transform[:-1, -1]

  @property
  def rotation(self):
    return self._rotation

  def translate(self, translation):
    self.transform[:-1, -1] += translation

  def rotate(self, rotation):
    self._rotation += rotation
    c,s = np.cos(rotation),np.sin(rotation)
    _=np.matmul(self.transform, [[c,-s,0],[s,c,0],[0,0,1]], out=self.transform)

  def scale(self, factor):
    self._scale_factor *= factor
    f = factor
    np.matmul(self.transform, [[f,0,0],[0,f,0],[0,0,1]], out=self.transform)




def circle_generate_points(circle: Circle, npoints:int):
  return np.linspace(0, 2*np.pi, npoints)*circle.radius
