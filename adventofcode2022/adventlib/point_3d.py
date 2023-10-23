from __future__ import annotations

import dataclasses
import numpy as np
import itertools


@dataclasses.dataclass(eq=True, frozen=True)
class Point:
  x: int
  y: int
  z: int

  def __add__(self, o: Point):
    return Point(self.x + o.x, self.y + o.y, self.z + o.z)

  def __sub__(self, o: Point):
    return Point(self.x - o.x, self.y - o.y, self.z - o.z)
  
  def __mul__(self, o: int):
    return Point(self.x * o, self.y * o, self.z * o)

  def __hash__(self):
    return hash((self.x, self.y, self.z))
  
  def __repr__(self):
    return f'[{self.x:+d}, {self.y:+d}, {self.z:+d}]'
  
  def __matmul__(self, f):
    return Point(f(self.x), f(self.y), f(self.z))
  
  def __pos__(self):
    return self
  
  def __neg__(self):
    return self * -1
  
  def sign(self):
    return self @ np.sign
  
  def a(self):
    return np.array([self.x, self.y, self.z])

  def distance(a, b):
    return np.sqrt(np.sum((a - b).a() ** 2))
  
  def __abs__(self):
    return self.distance(ORIGIN)

  def mandistance(a, b):
    return np.sum(((a - b) @ np.abs).a())
  
  
  def within_bounds_incl(self, a, b):
    return np.all(np.logical_and(self.a() >= a.a(), self.a() <= b.a()))
  
  
  def within_bounds_excl(self, a, b):
    return np.all(np.logical_and(self.a() >= a.a(), self.a() < b.a()))


def point_bb(points):
  a = np.array([i.a() for i in points])
  return Point(*(np.min(a, axis=0))), Point(*(np.max(a, axis=0)))


def iter_in_bb(bb_min, bb_max):
  a = np.array([bb_min.a(), bb_max.a()])
  a = a.T
  a[:, -1] += 1
  for xs in itertools.product(*[range(i, j) for i, j in a]):
    yield Point(*xs)


ORIGIN = Point(0, 0, 0)

X_P = Point(+1, 0, 0)
X_N = Point(-1, 0, 0)
Y_P = Point(0, +1, 0)
Y_N = Point(0, -1, 0)
Z_P = Point(0, 0, +1)
Z_N = Point(0, 0, -1)


DIRS6 = [
    X_P, X_N,
    Y_P, Y_N,
    Z_P, Z_N,
]

DIRS26 = [
    X_P, X_N,
    Y_P, Y_N,
    Z_P, Z_N,
]

ALL_NEG = Point(-1, -1, -1)
ALL_POS = Point(1, 1, 1)
