import re

SEARCH_SPECIAL_RE = re.compile(r'[\|&\-!@\[\]~/<=\^\$,\\]', re.IGNORECASE)
SEARCH_AND_RE = re.compile(r'\bAND\b')
SEARCH_OR_RE = re.compile(r'\bOR\b')
SEARCH_NOT_RE = re.compile(r'\bNOT\b')

def formalize_query(query, strip=False, quorum=0):
  # leave empty queries intact (special case -- browse)
  if not query:
    return query
  
  # first, strip special characters
  query = SEARCH_SPECIAL_RE.sub('', query)

  if strip:
    return query

  # next, convert googley boolean operators to symbolic form
  query = SEARCH_AND_RE.sub('&', query)
  query = SEARCH_OR_RE.sub('|', query)
  query = SEARCH_NOT_RE.sub('-', query)
  
  if quorum is not None:
    query = "\"%s\"/%d" % (query, max(1, round(len(query.split()) * quorum)))

  return query
