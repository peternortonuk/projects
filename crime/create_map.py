"""
https://developers.google.com/maps/documentation/maps-static/overview

https://docs.python.org/3/howto/urllib2.html#urllib-howto
http://www.compciv.org/guides/python/how-tos/creating-proper-url-query-strings/

"""

import urllib.parse
import webbrowser
from constants import raw_url
from credentials import api_key

center = r'Oxford,UK'
width = 600
height = 600
size = f'{width}x{height}'

params_dict = {'center': center, 'zoom': 13, 'size': size, 'maptype': 'roadmap',
               'key': api_key}

params = urllib.parse.urlencode(params_dict)
url = raw_url + params
webbrowser.open(url)
