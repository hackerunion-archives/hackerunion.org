import math
import time
import datetime
import itertools

# always returns diff in seconds
def epoch_to_datetime(epoch):
  return datetime.datetime.utcfromtimestamp(epoch)


def unixtime(dt, mili=False):
  return time.mktime(dt.timetuple())


# always returns diff in seconds
def timedelta_to_seconds(td):
  return int(td.days * 86400.00 + td.seconds)


def datetime_truncate(dt, unittype):
  units = ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']
  
  try:
    return dt.replace(**dict(itertools.imap(lambda u: (u, 1 if u in ('month', 'day') else 0), units[units.index(unittype)+1:])))
  except:
    raise ValueError('"%s" is not a recognized datetime unit.' % unittype)


def datetime_delta_list(dts):
  return reduce(lambda l, dt: l + [timedelta_to_seconds(dt - dts[len(l)-1]) + l[-1]], dts[1:], [0])


def datetime_izip(dts, vals, unittype, fromseconds, default=0, last=None):
  cnt = 0

  for dt, val in itertools.izip(dts, vals):
    if last is not None:
      for off in range(1, math.floor(fromseconds(timedelta_to_seconds(dt - last)))):
        yield (last + datetime.timedelta(**{ unittype: off }), default)
    
    last = dt
    yield (dt, val)
