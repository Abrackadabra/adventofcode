import dataclasses

from tqdm import tqdm_notebook as tqdm
import requests
import pickle
import re
import itertools
import functools
import collections
import string
from bs4 import BeautifulSoup

from adventlib import *
from adventlib.intcode import Program

YEAR = 2019
DAY = int('13')

submit1, submit2 = generate_submits(YEAR, DAY)

raw_input = get_input(YEAR, DAY)

# lines = linesplit("""
# 3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99
#
# """.strip())

lines = linesplit(raw_input, verbose=True)

# @dataclasses.dataclass
# class Point:
#   x: int
#   y: int
#
#   def __add__(self, o):
#     return Point(self.x + o.x, self.y + o.y)
#
#   def __hash__(self):
#     return hash((self.x, self.y))
#
#   def __abs__(self):
#     return abs(self.x) + abs(self.y)
#
#
# dirs = [
#     Point(0, +1),
#     Point(+1, 0),
#     Point(0, -1),
#     Point(-1, 0),
# ]
#
# dir_index = 0
# pos = Point(0, 0)
# field = {pos: 1}
# buf = collections.deque()
#
#
# def program_input():
#   while True:
#     if pos not in field:
#       yield 0
#     else:
#       yield field[pos]


program = Program(lines[0])
run = program.run()


def input_getter():
  while True:
    c = input().strip()

    if c == 'a':
      yield -1
    elif c == 's':
      yield 0
    elif c == 'd':
      yield 1
    else:
      raise Exception()

ball_pos = ()
paddle_pos = ()

def bot():
  while True:
    if ball_pos[0] == paddle_pos[0]:
      yield 0
    if ball_pos[0] < paddle_pos[0]:
      yield -1
    if ball_pos[0] > paddle_pos[0]:
      yield 1


# run.add_input(input_getter())
run.add_input(bot())
run.set_mem({0: 2})

d = {}

chars = {
    0: ' ',
    1: '#',
    2: 'b',
    3: '-',
    4: 'o',
}

while True:
  x = next(iter(run))
  y = next(iter(run))
  t = next(iter(run))

  if x == -1 and y == 0:
    print('SCORE', t)
  else:
    d[(x, y)] = t
    if t == 3:
      paddle_pos = (x, y)
    if t == 4:
      ball_pos = (x, y)

    # for i in range(30):
    #   for j in range(50):
    #     t = d.get((j, i), 0)
    #
    #     print(chars[t], end='')
    #   print()
