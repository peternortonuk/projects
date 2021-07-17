import urllib.request
import re
from bs4 import BeautifulSoup
import os

ids = [104647769]
id = ids[0]
properties_dict = {id:
    {
        'photo_urls': [],
        'floorplan_url': None,
        'photo_filenames': [],
        'floorplan_image_filename': None,
        'property_text': None,
    }
}

page_url_template = r'https://www.rightmove.co.uk/properties/{id}#/'
floorplan_url_endpoint = r'floorplan?activePlan=1'
project_folder = r'c:\dev\code\projects\estateagents'
image_folder = os.path.join(project_folder, 'images')

# find photos
page_url = page_url_template.format(id=id)

with urllib.request.urlopen(page_url) as response:
    html_doc = response.read()

soup = BeautifulSoup(html_doc, 'html.parser')

tags = soup.head.find_all('meta')
for tag in tags:
    if tag.attrs.get('property') == 'og:image':
        properties_dict[id]['photo_urls'].append(tag['content'])

# find floorplan
properties_dict[id]['floorplan_url'] = page_url + floorplan_url_endpoint

with urllib.request.urlopen(properties_dict[id]['floorplan_url']) as response:
    html_doc = response.read()

soup = BeautifulSoup(html_doc, 'html.parser')

[tag] = soup.body.find_all(alt='Floorplan')
floorplan_image_url = tag['src']

# remove the image size control _max_296x197.jpeg
pattern = r'_max_\d+x\d+'
replace = ''
properties_dict[id]['floorplan_url'] = re.sub(pattern, replace, properties_dict[id]['floorplan_url'])

# get text description and price and things
this_property_image_folder = os.path.join(image_folder, str(id))
urllib.urlretrieve(floorplan_image_url, this_property_image_folder)

# get photos

pass
