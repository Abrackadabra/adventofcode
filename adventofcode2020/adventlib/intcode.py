from __future__ import annotations

import collections
import dataclasses
import enum
import itertools
from typing import Callable
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import Iterator
from typing import List

import numpy as np

from adventlib.common import amap


class ParamType(enum.Enum):
  REFERENCE = 0
  IMMEDIATE = 1
  RELATIVE = 2


@dataclasses.dataclass
class RelBase:
  val: int


@dataclasses.dataclass
class Param:
  type: ParamType
  val: int
  mem: Dict[int, int]
  rel_base: RelBase

  def get(self) -> int:
    if self.type == ParamType.IMMEDIATE:
      return self.val
    elif self.type == ParamType.REFERENCE:
      return self.mem[self.val]
    elif self.type == ParamType.RELATIVE:
      return self.mem[self.rel_base.val + self.val]
    else:
      assert False

  def set(self, val: int):
    if self.type == ParamType.REFERENCE:
      self.mem[self.val] = val
    elif self.type == ParamType.RELATIVE:
      self.mem[self.rel_base.val + self.val] = val
    else:
      assert False


@dataclasses.dataclass
class Op:
  code: int
  n_params: int
  f: Callable = None

  def __call__(self, f) -> Op:
    self.f = f
    return self


@dataclasses.dataclass
class ExecEnv:
  # read
  op: Op
  pos: int
  params: List[Param]
  # private
  _input: Iterator[int]
  _output: List[int]
  _verbose: bool
  # set
  halt: bool = False
  jump_to: int = None
  adjust_rel_base: int = None

  def input(self) -> int:
    return next(self._input)

  def output(self, val):
    if self._verbose:
      print(f'> {val}')
    self._output.append(val)


class Runtime:
  p: Program

  inputs: List[Iterable[int]]
  combined_input_iterator: Iterator[int]
  mem: Dict[int, int]
  rel_base: RelBase
  pos: int
  verbose: bool

  _halted: bool = False

  def __init__(self, p: Program, verbose: bool):
    self.p = p

    self.inputs = []
    self.combined_input_iterator = itertools.chain()

    self.mem = collections.defaultdict(int, dict(enumerate(p.mem_template)))
    self.rel_base = RelBase(0)
    self.pos = 0

    self.verbose = verbose

  def add_input(self, input_iter: Iterator[int]):
    self.inputs.append(input_iter)
    self.combined_input_iterator = itertools.chain(*self.inputs)
    return self

  def set_mem(self, d: Dict[int, int]):
    self.mem.update(d)
    return self

  def single_iteration(self) -> Generator[int]:
    if self._halted:
      raise Exception('Already halted')

    op_spec = self.mem[self.pos]
    op_code = op_spec % 100
    params_spec = op_spec // 100

    op = self.p.opcode_table[op_code]

    params = []

    for i in range(op.n_params):
      mode = params_spec % 10
      params.append(
          Param(ParamType(mode), self.mem[self.pos + i + 1], self.mem,
                self.rel_base))
      params_spec //= 10

    output = []
    env = ExecEnv(
        op=op,
        pos=self.pos,
        params=params,
        _input=self.combined_input_iterator,
        _output=output,
        _verbose=self.verbose)

    op.f(self.p, env)

    if env.halt is not None and env.halt:
      self._halted = True

    if env.adjust_rel_base is not None:
      self.rel_base.val += env.adjust_rel_base

    if env.jump_to is not None:
      self.pos = env.jump_to
    else:
      self.pos = self.pos + op.n_params + 1

    yield from output

  def __iter__(self):
    while not self._halted:
      yield from self.single_iteration()


class Program:
  mem_template: np.ndarray
  opcode_table: Dict[int, Op] = {}

  def __new__(cls, s: str):
    """Find declared operations"""
    for key in dir(cls):
      attr = getattr(cls, key, None)
      if attr and isinstance(attr, Op):
        cls.opcode_table[attr.code] = attr

    return super().__new__(cls)

  def __init__(self, s: str):
    self.mem_template = amap(int, s.strip().replace('\n', '').split(','))

  def run(self, verbose=True):
    return Runtime(self, verbose=verbose)

  def execute(self, input_list: List[int]) -> int:
    return next(iter(self.run().add_input(input_list)))

  @Op(99, 0)
  def op_halt(self, env: ExecEnv):
    env.halt = True

  @Op(1, 3)
  def op_add(self, env: ExecEnv):
    a, b, c = env.params
    c.set(a.get() + b.get())

  @Op(2, 3)
  def op_multiply(self, env: ExecEnv):
    a, b, c = env.params
    c.set(a.get() * b.get())

  @Op(3, 1)
  def op_input(self, env: ExecEnv):
    a, = env.params
    a.set(env.input())

  @Op(4, 1)
  def op_output(self, env: ExecEnv):
    a, = env.params
    env.output(a.get())

  @Op(5, 2)
  def op_jump_if_true(self, env: ExecEnv):
    a, b = env.params
    if a.get() != 0:
      env.jump_to = b.get()

  @Op(6, 2)
  def op_jump_if_false(self, env: ExecEnv):
    a, b = env.params
    if a.get() == 0:
      env.jump_to = b.get()

  @Op(7, 3)
  def op_less_than(self, env: ExecEnv):
    a, b, c = env.params
    c.set(int(a.get() < b.get()))

  @Op(8, 3)
  def op_equals(self, env: ExecEnv):
    a, b, c = env.params
    c.set(int(a.get() == b.get()))

  @Op(9, 1)
  def op_adjust_rel_base(self, env: ExecEnv):
    a, = env.params
    env.adjust_rel_base = a.get()
