from urllib.request import urlopen
from shutil import copyfileobj
from pathlib import Path
import re
from bs4 import BeautifulSoup
import os
import shelve
from datetime import date, datetime
import copy
from pprint import pprint as pp


class Properties:

    def __init__(self):
        today = date.today()
        self.today_as_string = datetime.strftime(today, '%Y%m%d')
        self.rightmove_prefix = 'rm'  # for folder names
        self.property_url_template = r'https://www.rightmove.co.uk/properties/{id_}#/'
        self.floorplan_url_endpoint = r'floorplan?activePlan=1'
        self.project_folder = r'c:\dev\code\projects\estateagents'
        self.image_folder_stub = os.path.join(self.project_folder, 'images')
        self.rightmove_filename = os.path.join(self.project_folder, 'rightmove')


class Scraper(Properties):

    def __init__(self, ids, image_scrape=True):
        self.ids = ids
        self.image_scrape = image_scrape
        super().__init__()
        empty_details_dict = {
            'property_url': None,
            'floorplan': None,
            'photos': [],
            'property_details': {},
        }
        self.properties_dict = {id_: copy.deepcopy(empty_details_dict) for id_ in self.ids}

        self.floorplan_url = ''
        self.photo_urls = []

    def property_url(self, id_):
        return self.property_url_template.format(id_=id_)

    def _get_soup(self, id_):
        with urlopen(self.property_url(id_)) as response:
            html_doc = response.read()

        self.soup = BeautifulSoup(html_doc, 'html.parser')

    def _find_description(self, id_):
        tags = self.soup.body.find('div', id='root')

        # heading tags
        h2 = tags.find_all('h2')

        key_features_string = 'Key features'
        [key_features_tag] = [t for t in h2 if t.string == key_features_string]
        key_features = [str(c.string) for c in key_features_tag.next_sibling.contents]

        property_description_string = 'Property description'
        [property_description_tag] = [t for t in h2 if t.string == property_description_string]
        property_description = [str(c.string) for c in list(property_description_tag.next_siblings)[1].contents[0].contents
                                if c.string != None]
        property_description = '\n'.join(property_description)

        # paragraph tags
        p = tags.find_all('p')
        tenure_string = 'Tenure:'
        [tenure] = [t.contents[1].string.strip() for t in p if t.contents[0].string == tenure_string]

        # price
        price_pattern = r'£\d{3},\d{3}'
        price = tags.find(string=re.compile(price_pattern))
        price = int(price[1:].replace(',', ''))

        # save into the dict
        self.properties_dict[id_]['property_details']['Tenure'] = tenure
        self.properties_dict[id_]['property_details']['Property Description'] = property_description
        self.properties_dict[id_]['property_details']['Price'] = price
        self.properties_dict[id_]['property_details']['Key Features'] = key_features

    def _find_photos(self, id_):
        tags = self.soup.head.find_all('meta')
        for tag in tags:
            if tag.attrs.get('property') == 'og:image':
                self.photo_urls.append(tag['content'])

    def _find_floorplan(self, id_):
        floorplan_page_url = self.property_url(id_) + self.floorplan_url_endpoint

        with urlopen(floorplan_page_url) as response:
            html_doc = response.read()

        soup = BeautifulSoup(html_doc, 'html.parser')

        [tag] = soup.body.find_all(alt='Floorplan')
        floorplan_url = tag['src']

        # remove the image size control _max_296x197.jpeg
        pattern = r'_max_\d+x\d+'
        replace = ''
        self.floorplan_url = re.sub(pattern, replace, floorplan_url)

    def _map_url_to_local_file(self, id_):
        folder_name = self.rightmove_prefix + str(id_)
        self.image_folder = os.path.join(self.image_folder_stub, folder_name)

        # create list of tuple pairs for photos
        for photo_url in self.photo_urls:
            filename = photo_url.split('/')[-1]
            filename = os.path.join(self.image_folder, filename)
            self.properties_dict[id_]['photos'].append(tuple([photo_url, filename]))

        # create single tuple pair for floorplan
        filename = self.floorplan_url.split('/')[-1]
        filename = os.path.join(self.image_folder, filename)
        self.properties_dict[id_]['floorplan'] = (self.floorplan_url, filename)

    def _create_folder_on_local_drive(self, id_):
        # create folder if it doesnt exist
        Path(self.image_folder).mkdir(parents=True, exist_ok=True)

    def _save_photos(self, id_):
        for photo_url, filename in self.properties_dict[id_]['photos']:
            # open the url and save the image
            with urlopen(photo_url) as in_stream, open(filename, 'wb') as out_file:
                copyfileobj(in_stream, out_file)

    def _save_floorplan(self, id_):
        floorplan_url, filename = self.properties_dict[id_]['floorplan']
        # open the url and save the image
        with urlopen(floorplan_url) as in_stream, open(filename, 'wb') as out_file:
            copyfileobj(in_stream, out_file)

    def collect_and_save(self):
        for id_ in self.ids:
            self.properties_dict[id_]['property_url'] = self.property_url(id_)
            self._get_soup(id_)
            self._find_description(id_)
            self._find_photos(id_)
            self._find_floorplan(id_)
            self._map_url_to_local_file(id_)
            if self.image_scrape:
                self._create_folder_on_local_drive(id_)
                self._save_photos(id_)
                self._save_floorplan(id_)

        version = self.today_as_string
        with shelve.open(self.rightmove_filename) as db:
            db[version] = self.properties_dict


class Viewer(Properties):

    def __init__(self):
        super().__init__()
        with shelve.open(self.rightmove_filename) as db:
            keys = sorted(list(db.keys()))
            self.properties_dict = db[keys[-1]]


if __name__ == '__main__':

    ids = [104647769, 110103536]
    scrape = False
    view = not scrape

    if scrape:
        s = Scraper(ids, image_scrape=False)
        s.collect_and_save()
        pp(s.properties_dict)

    if view:
        v = Viewer()
        pp(v.properties_dict)

