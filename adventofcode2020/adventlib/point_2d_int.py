from __future__ import annotations

import dataclasses


@dataclasses.dataclass(eq=True, frozen=True)
class Point:
  x: int
  y: int

  def __add__(self, o: Point):
    return Point(self.x + o.x, self.y + o.y)

  def __sub__(self, o: Point):
    return Point(self.x - o.x, self.y - o.y)

  def __hash__(self):
    return hash((self.x, self.y))


ORIGIN = Point(0, 0)
UP = Point(-1, 0)
DOWN = Point(+1, 0)
LEFT = Point(0, -1)
RIGHT = Point(0, +1)

dirs = [
    RIGHT, DOWN, LEFT, UP
]