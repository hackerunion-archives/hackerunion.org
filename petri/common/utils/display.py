import math

def textcloud_scale(scale, value, minval, maxval, base=0):
  if maxval <= minval:
    return scale * 0.5
  elif value > minval:
    return (scale * (value - minval)) / (maxval - minval)
  return base
