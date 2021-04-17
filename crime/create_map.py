"""
https://developers.google.com/maps/documentation/maps-static/overview

https://docs.python.org/3/howto/urllib2.html#urllib-howto
http://www.compciv.org/guides/python/how-tos/creating-proper-url-query-strings/

"""

from crime.credentials import api_key

# Oxford,UK
latitude = 51.7520
longitude = -1.2577
center = f'{latitude},{longitude}'

width = 600
height = 600
size = f'{width}x{height}'

map_dict = {'center': center, 'zoom': 12, 'size': size, 'maptype': 'roadmap'}
key_dict = {'key': api_key}

