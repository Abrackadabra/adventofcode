from __future__ import annotations

import dataclasses
import numpy as np
import itertools


@dataclasses.dataclass(eq=True, frozen=True)
class Point:
  x: int
  y: int

  
  def __add__(self, o: Point):
    return Point(self.x + o.x, self.y + o.y)

  
  def __sub__(self, o: Point):
    return Point(self.x - o.x, self.y - o.y)
  
  
  def __mul__(self, o: int):
    return Point(self.x * o, self.y * o)

  
  def __hash__(self):
    return hash((self.x, self.y))
  
  
  def __repr__(self):
    return f'[{self.x:+d}, {self.y:+d}]'
  
  
  def __matmul__(self, f):
    return Point(f(self.x), f(self.y))
  
  
  def __pos__(self):
    return self
  
  
  def __neg__(self):
    return self * -1
  
  
  def sign(self):
    return self @ np.sign
  
  
  def a(self):
    return np.array([self.x, self.y])

  
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


ORIGIN = Point(0, 0)

NORTH = Point(0, +1)
SOUTH = Point(0, -1)
WEST = Point(-1, 0)
EAST = Point(+1, 0)

POINTS_NORTH = {
  'N': NORTH,
  'S': SOUTH,
  'W': WEST,
  'E': EAST,
}

UP = NORTH
DOWN = SOUTH
LEFT = WEST
RIGHT = EAST

POINTS_UP = {
  'U': UP,
  'D': DOWN,
  'L': LEFT,
  'R': RIGHT,
}

NORTHEAST = NORTH+EAST
NORTHWEST = NORTH+WEST
SOUTHEAST = SOUTH+EAST
SOUTHWEST = SOUTH+WEST

POINTS_2L = {
  'N': NORTH,
  'S': SOUTH,
  'W': WEST,
  'E': EAST,
  
  'NE': NORTHEAST,
  'NW': NORTHWEST,
  'SE': SOUTHEAST,
  'SW': SOUTHWEST,
}

DIRS4 = [
    RIGHT, UP, LEFT, DOWN,
]

DIRS8 = [
    EAST, NORTHEAST, NORTH, NORTHWEST, WEST, SOUTHWEST, SOUTH, SOUTHEAST,
]

DIRS9 = DIRS8 + [ORIGIN]

DIRS_DIAG = [
    NORTHEAST, NORTHWEST, SOUTHWEST, SOUTHEAST,
]

ALL_NEG = Point(-1, -1)
ALL_POS = Point(1, 1)
