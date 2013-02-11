def force(f, default=None):
  try:
    return f()
  except:
    return default


def safe_int(raw):
  return force(lambda: int(raw), 0)


def ensure_tuple(val):
  return val if type(val) is tuple else (val,)


def simplify_tuple(tup):
  return tup[0] if len(tup) == 1 else tup


def kwargs_safe(kwargs):
  return dict((str(k), v) for k, v in kwargs.iteritems())


def lookup_safe(key, data, default=None):
  cur = data

  for k in key.split("."):
    if k not in cur:
      return default

    cur = cur[k]

  return cur


def remap(d, keys, inplace=True):
  if inplace:
    for k, v in keys.iteritems():
      if k not in d:
        continue

      d[v] = d[k]
      del d[k]

    return d
  
  nxt = {}

  for k, v in d.iteritems():
    if k in keys:
      nxt[keys[k]] = v
    else:
      nxt[k] = v
  
  return nxt


def setattr_safe(obj, attr, val):
  if val is not None:
    setattr(obj, attr, val)
