from urllib.request import urlopen
from shutil import copyfileobj
from pathlib import Path
import re
from bs4 import BeautifulSoup
import os
import shelve
from datetime import date, datetime

today = date.today()
today_as_string = datetime.strftime(today, '%Y%m%d')
rightmove_prefix = 'rm'  # for folder names
page_url_template = r'https://www.rightmove.co.uk/properties/{id_}#/'
floorplan_url_endpoint = r'floorplan?activePlan=1'
project_folder = r'c:\dev\code\projects\estateagents'
image_folder = os.path.join(project_folder, 'images')
rightmove_filename = os.path.join(project_folder, 'rightmove')


def create_dict(ids):
    empty_details_dict = {
        'photo_urls': [],
        'floorplan_url': None,
        'photo_filenames': [],
        'floorplan_image_filename': None,
        'property_text': None,
    }
    return {id_: empty_details_dict for id_ in ids}


def find_photos(id_):
    photo_urls = []
    page_url = page_url_template.format(id_=id_)

    with urlopen(page_url) as response:
        html_doc = response.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    tags = soup.head.find_all('meta')
    for tag in tags:
        if tag.attrs.get('property') == 'og:image':
            photo_urls.append(tag['content'])

    return photo_urls


def find_floorplan(_id):
    page_url = page_url_template.format(id_=id_)
    properties_dict[id_]['floorplan_url'] = page_url + floorplan_url_endpoint

    with urlopen(properties_dict[id_]['floorplan_url']) as response:
        html_doc = response.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    [tag] = soup.body.find_all(alt='Floorplan')
    floorplan_image_url = tag['src']

    # remove the image size control _max_296x197.jpeg
    pattern = r'_max_\d+x\d+'
    replace = ''
    floorplan_image_url = re.sub(pattern, replace, floorplan_image_url)
    return floorplan_image_url


# ======================================================================================================================
# get text description and price and things

def save_floorplan(id_, properties_dict):
    # setup folder, path and filenames
    folder_name = rightmove_prefix + str(id_)
    this_property_image_folder = os.path.join(image_folder, folder_name)
    filename = properties_dict[id_]['floorplan_url'].split('/')[-1]
    this_property_image_folder_and_filename = os.path.join(this_property_image_folder, filename)

    # create folder if it doesnt exist
    Path(this_property_image_folder).mkdir(parents=True, exist_ok=True)

    # open the url and save the image
    with urlopen(properties_dict[id_]['floorplan_url']) as in_stream, open(this_property_image_folder_and_filename, 'wb') as out_file:
        copyfileobj(in_stream, out_file)


if __name__ == '__main__':
    ids = [104647769, 110103536]
    properties_dict = create_dict(ids)
    for id_ in ids:
        properties_dict[id_]['photo_urls'] = find_photos(id_)
        properties_dict[id_]['floorplan_url'] = find_floorplan(id_)
        save_floorplan(id_, properties_dict)

version = today_as_string
with shelve.open(rightmove_filename) as db:
    db[version] = properties_dict
