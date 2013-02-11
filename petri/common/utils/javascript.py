from django.conf import settings

from petri.common.lib.jsmin import jsmin
from petri.common.lib.jspacker import JavaScriptPacker

def shrinkjs(script, minify_only=False):
  "Determine and execute optimal means of shrinking javascript."
  if settings.DEBUG:
    return script
 
  # packing only makes sense for longer scripts
  if minify_only or len(script) < 1024:
    return jsmin(script)
  
  return JavaScriptPacker().pack(jsmin(script), compaction=True, encoding=62, fastDecode=True)
