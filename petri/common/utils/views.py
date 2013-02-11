import math
from django.conf import settings

def paginate(data, pagesize, page, window=10):
  ld = len(data)
  pages = int(math.ceil(ld / float(pagesize)))
  page = min(max(0, pages - 1), page)
  
  return (data[(page * pagesize):((page + 1) * pagesize)],
          { 'total': ld,
            'total_current': ld % pagesize if page == pages - 1 else pagesize,
            'pages': pages,
            'page': page,
            'window': range(max(0, page - window / 2), min(pages, page + window / 2)),
            'prev': max(0, page - 1),
            'next': min(max(0, pages - 1), page + 1),
            'item_start': page * pagesize + 1,
            'item_end': min(ld, (page + 1) * pagesize)
          })
