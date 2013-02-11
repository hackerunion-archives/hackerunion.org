import re
import random
import hashlib
import datetime

BASE62_SYMBOLS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
BASE36_SYMBOLS="abcdefghijklmnopqrstuvwxyz0123456789"
BASE26_SYMBOLS="abcdefghijklmnopqrstuvwxyz"

ENCODING_SYMBOLS=BASE36_SYMBOLS

SHRINK_RE = re.compile(r'(?<=\w)[aeiou](?=\w)', re.IGNORECASE)

def key_encode(n, encoding_symbols=ENCODING_SYMBOLS):
  "Convert a number to a minimal-length alphanumeric encoding."
  numsym = len(encoding_symbols)
  s = ""

  if n < 0:
    raise ValueError("Unencoded keys must be positive integers")

  while True:
    s = encoding_symbols[n % numsym] + s
    n = n / numsym - 1

    if n < 0:
      return s


def key_decode(s, encoding_symbols=ENCODING_SYMBOLS):
  "Convert minimal-length alphanumeric string to the corresponding decimal value."
  numsym = len(encoding_symbols)
  
  try:
    n = 0
    ls = len(s) - 1

    for (i, c) in enumerate(s):
      n = numsym * n + encoding_symbols.index(c) + (i < ls and 1 or 0)

    return n

  except ValueError:
    raise ValueError("Invalid symbol found in encoded key")


def key_max(digits, encoding_symbols=ENCODING_SYMBOLS):
  "Return the maximum value encodable in a certain number of symbols."
  numsym = len(encoding_symbols)
  result = 0

  for i in range(digits):
    if i == 0:
      result += numsym - 1
    else:
      result += numsym ** (i + 1)
    
    digits -= 1

  return result


def force_int(s, default=0):
  "Convert a string to an integer; on failure, return 0."
  try:
    return int(s)
  except:
    return default


def none_if_blank(s):
  return None if s is None or len(s) == 0 else s


def smart_title(s):
  return s.title() if len(s) and s[0].isalpha() else s


def random_string(max_length=32):
  return hashlib.md5("%s%s" % (random.randint(0, 100000), datetime.datetime.now())).hexdigest()[:min(max_length, 32)]


def shrink(s, max_length, prefix=False, stupidify=False):
  if len(s) <= max_length:
    return s
  
  if stupidify:
    s = SHRINK_RE.sub('', s)

  return s if len(s) <= max_length else ('...' + s[3:max_length] if prefix else s[:max_length-3] + '...')


def random_pin(*args, **kwargs):
  return str(random.randint(0, 99999)).zfill(5)


def random_code(*args, **kwargs):
  return random_string(max_length=8)


def sanitize_string(s):
  return re.sub(r'[^a-z\s]', '', ' '.join(s.lower().split()))
