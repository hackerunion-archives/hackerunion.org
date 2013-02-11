from itertools import imap
from itertools import groupby

from operator import itemgetter

from petri.common.utils.helpers import remap

def iremap(iterable, keys, inplace=True):
  for d in iterable:
    yield remap(d, keys, inplace=inplace)


def iblocks(iterable, blocksize=None, leftovers=True):
  block = []

  for i in iterable:
    block.append(i)

    if len(block) == blocksize:
      yield block
      block = []
   
  # return leftovers
  if leftovers and len(block) > 0:
    yield block


def unique_justseen(iterable, keyfunc=None):
  "List unique elements, preserving order. Remember only the element just seen."
  return imap(lambda i: i.next(), imap(itemgetter(1), groupby(iterable, keyfunc)))


def unique_overall(iterable, keyfunc=None):
  "List unique elements, prioritizing earliest. Less efficient than above, but doesn't require sorting."
  seen = set()

  for i in iterable:
    key = i if keyfunc is None else keyfunc(i)

    if key not in seen:
      seen.add(key)
      yield i
