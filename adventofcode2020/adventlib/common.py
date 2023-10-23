from tqdm import tqdm_notebook as tqdm
import requests
import pickle
import re
import itertools
import functools
import collections
import string
from bs4 import BeautifulSoup

import numpy as np

with open('session.pickle', 'rb') as file:
  session = pickle.load(file)


def get_input(year, day):
  response = session.get(f'https://adventofcode.com/{year}/day/{day}/input')
  assert response.status_code == 200, response.text

  return response.text


SUBMITTED_ANSWERS = {}


def submit(year, day, level, ans):
  key = (year, day, level, ans)
  if key in SUBMITTED_ANSWERS:
    print(f'Already submitted {key}: {SUBMITTED_ANSWERS[key]}')
    return SUBMITTED_ANSWERS[key]
  
  response = session.post(
      f'https://adventofcode.com/{year}/day/{day}/answer',
      data=dict(
          answer=ans,
          level=level,
      ))
  assert response.status_code == 200, response.text
  
  if 'You gave an answer too recently' in response.text:
    print(BeautifulSoup(response.text).select('main>article>p'))
    assert False

  if 'That\'s the right answer!' in response.text:
    SUBMITTED_ANSWERS[key] = True
    return True

  print(BeautifulSoup(response.text).select('main>article>p'))
  SUBMITTED_ANSWERS[key] = False
  assert False


amap = lambda *args, **kwargs: np.array(list(map(*args)), **kwargs)


def å(a, *fs):
  for f in fs:
    a = amap(f, a)

  return a


def linesplit(s, verbose=False):
  lines = s.split('\n')
  if lines and not lines[-1]:
    lines = lines[:-1]

  groups = []
  t = []
  for line in lines:
    if line:
      t.append(line)
    else:
      groups.append(t)
      t = []
  if t:
    groups.append(t)

  if verbose:
    print(f'{len(lines)} lines')
    print(f'{len(groups)} groups')
    print('>>>')
    for i in lines[:3]:
      print(i[:100], '...' if len(i) > 100 else '', sep='')
    if len(lines) > 3:
      print('...')

  return lines, groups


def lines_as_matrix(lines):
  assert len(set(map(len, lines))) == 1
  return np.array(list(map(list, lines)), dtype='<U1')


def generate_submits(year, day):
  submit1 = lambda ans: submit(year=year, day=day, level=1, ans=ans)
  submit2 = lambda ans: submit(year=year, day=day, level=2, ans=ans)

  return submit1, submit2
