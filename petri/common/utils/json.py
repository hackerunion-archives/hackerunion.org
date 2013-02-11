__author__ = "Brandon Diamond [brandon.t.diamond@gmail.com]"

def success(expr=None):
  return {'result': 'success', 'value': expr}

def error(expr="Invalid request."):
  return {'result': 'error', 'value': expr}
