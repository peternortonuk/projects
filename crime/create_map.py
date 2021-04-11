"""
https://developers.google.com/maps/documentation/maps-static/overview

https://docs.python.org/3/howto/urllib2.html#urllib-howto
http://www.compciv.org/guides/python/how-tos/creating-proper-url-query-strings/

"""

import urllib.parse
from crime.credentials import api_key

center = r'Oxford,UK'
width = 600
height = 600
size = f'{width}x{height}'

map_dict = {'center': center, 'zoom': 13, 'size': size, 'maptype': 'roadmap'}
key_dict = {'key': api_key}

map_params = urllib.parse.urlencode(map_dict)
key_params = urllib.parse.urlencode(key_dict)
