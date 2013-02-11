from petri.common.data.names.male import NAMES as male_names
from petri.common.data.names.female import NAMES as female_names

def guess_gender(name):
  mscore = None
  fscore = None
  
  if name is None:
    return None

  name = name.upper()
  
  try:
    mscore = male_names.index(name)
  except ValueError:
    pass

  try:
    fscore = female_names.index(name)
  except ValueError:
    pass
  
  if mscore is None and fscore is None:
    return None
  
  if mscore is None or fscore is None:
    return 'f' if mscore is None else 'm'
  return 'm' if mscore <= fscore else 'f'
