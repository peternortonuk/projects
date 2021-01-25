"""
https://developers.google.com/maps/documentation/maps-static/overview

https://docs.python.org/3/howto/urllib2.html#urllib-howto
"""

import urllib.parse
import urllib.request
from constants import raw_url
from credentials import api_key

params_dict = {'center': 'Brooklyn+Bridge,New+York,NY',
               'zoom': 13,
               'size': '600x300',
               'maptype': 'roadmap',
               }

params_dict['key'] = api_key


data = urllib.parse.urlencode(params_dict)
data = data.encode('ascii')  # data should be bytes
req = urllib.request.Request(raw_url, data)
with urllib.request.urlopen(req) as response:
   the_page = response.read()
   pass
