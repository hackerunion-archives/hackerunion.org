import json
import socket
import urllib
import urllib2
import decimal

from django.conf import settings

from petri.common.utils.helpers import force

class IPInfoDBException(Exception):
  pass


def _clean_response(raw):
  if type(raw) is not dict:
    raise IPInfoDBException()
  
  if raw.get('Status', None) != 'OK':
    raise IPInfoDBException()
  
  try:
    return { 'latitude': force(lambda: decimal.Decimal(None if raw['Latitude'] == '0' else raw['Latitude'])),
             'longitude': force(lambda: decimal.Decimal(None if raw['Longitude'] == '0' else raw['Longitude'])),
             'city': raw.get('City', None),
             'state': raw.get('RegionName', None),
             'region': raw.get('RegionName', None),
             'postal': raw.get('ZipPostalCode', None),
             'countryCode': raw.get('CountryCode', None),
             'country': raw.get('CountryName', None),
             'tz': raw.get('TimezoneName', None),
             'tzOff': force(lambda: int(raw['Gmtoffset']), default=0),
             'dstOff': force(lambda: int(raw['Dstoffset']), default=0),
             'dstActive': bool(raw.get('Isdst', False)) }
  
  except Location.DoesNotExist:
    raise IPInfoDBException()


class IPInfo():
  def __init__(self, apikey):
    self.apikey = apikey

  def GetIPInfo(self, baseurl, ip=None, timezone=False):
    """Same as GetCity and GetCountry, but a baseurl is required. This is for if you want to use a different server that uses the the php scripts on ipinfodb.com."""
    passdict = { "output":"json", "key":self.apikey }

    if ip:
      try:
        passdict["ip"] = socket.gethostbyaddr(ip)[2][0]
      except:
        passdict["ip"] = ip

    if timezone:
      passdict["timezone"] = "true"
    else:
      passdict["timezone"] = "false"

    urldata = urllib.urlencode(passdict)
    url = baseurl + "?" + urldata
    urlobj = urllib2.urlopen(url)
    data = urlobj.read()

    urlobj.close()

    datadict = json.loads(data)

    return datadict

  def GetCity(self, ip=None, timezone=False):
    """Gets the location with the context of the city of the given IP. If no IP is given, then the location of the client is given. The timezone option defaults to False, to spare the server some queries."""
    baseurl = "http://api.ipinfodb.com/v2/ip_query.php"
    return self.GetIPInfo(baseurl, ip, timezone)

  def GetCountry(self, ip=None, timezone=False):
    """Gets the location with the context of the country of the given IP. If no IP is given, then the location of the client is given. The timezone option defaults to False, to spare the server some queries."""
    baseurl = "http://api.ipinfodb.com/v2/ip_query_country.php"
    return self.GetIPInfo(baseurl, ip, timezone)


def get_client():
  return IPInfo(settings.IPINFODB_API_KEY)


def get_ip_city(ip=None, timezone=False, safe=True):
  try:
    return _clean_response(get_client().GetCity(ip=ip, timezone=timezone))
  except:
    if safe:
      return None

    raise IPInfoDBException()


def get_ip_country(ip=None, timezone=False, safe=True):
  try:
    return _clean_response(get_client().GetCountry(ip=ip, timezone=timezone))
  except:
    if safe:
      return None

    raise IPInfoDBException()
