import urllib.request
import re
from bs4 import BeautifulSoup

page_url = r'https://www.rightmove.co.uk/properties/104647769#/'

with urllib.request.urlopen(page_url) as response:
    html_doc = response.read()

soup = BeautifulSoup(html_doc, 'html.parser')

# find photos
photo_urls = []
tags = soup.head.find_all('meta')
for tag in tags:
    if tag.attrs.get('property') == 'og:image':
        photo_urls.append(tag['content'])

# find floorplan
tags = soup.body
tags = tags.find_all(href=re.compile('floorplan'))
for tag in tags:
    cc = list(tag.children)
    for c in cc:
        src = c.attrs.get('src')
        if src:
            floorplan_url = src
pass


pass
