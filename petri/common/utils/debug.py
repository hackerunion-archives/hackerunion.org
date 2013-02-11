import os
import datetime
import itertools

from django.conf import settings

def debug(*args, **kwargs):
  try:
    f = open('/tmp/%s' % (settings.DEBUG_FILENAME.replace("?", str(os.getpid()))), 'a')

    try:
      msg = '%s\t[%s] [%s] %s\n' % (str(datetime.datetime.now()), str(kwargs.get('level', '*')), kwargs.get('system', 'general'), ' '.join(itertools.imap(lambda x: str(x), args)))

      print msg
      f.write(msg)

    except:
      pass
    finally:
      f.close()
  except:
    pass
