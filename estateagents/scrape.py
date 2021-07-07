import urllib.request
import re
from bs4 import BeautifulSoup

ids = [104647769]
id = ids[0]

page_url_template = r'https://www.rightmove.co.uk/properties/{id}#/'
floorplan_url_endpoint = r'floorplan?activePlan=1'

# find photos
page_url = page_url_template.format(id=id)

with urllib.request.urlopen(page_url) as response:
    html_doc = response.read()

soup = BeautifulSoup(html_doc, 'html.parser')

photo_urls = []
tags = soup.head.find_all('meta')
for tag in tags:
    if tag.attrs.get('property') == 'og:image':
        photo_urls.append(tag['content'])

# find floorplan
floorplan_url = page_url + floorplan_url_endpoint

with urllib.request.urlopen(floorplan_url) as response:
    html_doc = response.read()

soup = BeautifulSoup(html_doc, 'html.parser')

[tag] = soup.body.find_all(alt='Floorplan')
floorplan_image_url = tag['src']

# remove the image size control _max_296x197.jpeg
pattern = r'_max_\d+x\d+'
replace = ''
floorplan_image_url = re.sub(pattern, replace, floorplan_image_url)


pass
