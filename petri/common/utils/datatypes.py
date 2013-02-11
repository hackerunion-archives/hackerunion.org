class DictObject(dict):
  def __getattr__(self, attr):
    return self[attr]
