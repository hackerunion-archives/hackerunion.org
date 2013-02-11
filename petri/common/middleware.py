import pprint
import traceback

from django.db import connection
from django.conf import settings
from django.http import HttpResponseServerError

from django.core.mail import send_mail

from petri.common.utils.debug import debug

class PrintExceptionMiddleware(object):
  def process_exception(self, request, exception):
    debug(traceback.format_exc())
    return None


class EmailExceptionMiddleware(object):
  def process_exception(self, request, exception):
    debug(traceback.format_exc())
    # send_mail('[petri] Exception: %s' % exception, traceback.format_exc(), settings.DEFAULT_EMAIL, settings.ERROR_EMAILS, fail_silently=True)
    return None


class FascistMiddleware(object):
  def process_exception(self, request, exception):
    return HttpResponseServerError(traceback.format_exc(), content_type="text/plain")


class DatabaseDebugMiddleware(object):
  def process_response(self, request, response):
    if response['Content-Type'].lower().find('text/html') != -1:
      response.write("\n\n<!-- begin hideous query debugging code --><hr/><style type='text/css'>#dbDebug td { font-size: 0.9em; border: 1px dotted #ccc; padding: 4px; }</style><table id='dbDebug'><thead><tr><td><b>Query</b></td><td><b>Time</b></td></tr></thead><tbody>")
      
      for record in connection.queries:
        response.write("<tr><td><code>%s</code></td><td>%s</td></tr><!-- end hideous query debugging code -->" % (record['sql'], record['time']))

      response.write("</tbody></table>")
    return response
