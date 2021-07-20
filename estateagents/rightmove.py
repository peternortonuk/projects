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

    today = date.today()
    today_as_string = datetime.strftime(today, '%Y%m%d')
    rightmove_prefix = 'rm'  # for folder names
    property_url_template = r'https://www.rightmove.co.uk/properties/{id_}#/'
    floorplan_url_endpoint = r'floorplan?activePlan=1'
    project_folder = r'c:\dev\code\projects\estateagents'
    image_folder_stub = os.path.join(project_folder, 'images')
    rightmove_filename = os.path.join(project_folder, 'rightmove')

    empty_details_dict = {
        'property_url': None,
        'floorplan': None,
        'photos': [],
        'property_details': {},
    }


class Scraper(Properties):

    def __init__(self, id_, image_scrape=False):
        self.id = id_
        self.image_scrape = image_scrape
        self.property_dict = {self.id: copy.deepcopy(Properties.empty_details_dict)}
        self.floorplan_url = ''
        self.photo_urls = []

    def _get_property_url(self):
        self.property_url = self.property_url_template.format(id_=self.id)
        self.property_dict[self.id]['property_url'] = self.property_url

    def _get_soup(self):
        with urlopen(self.property_url) as response:
            html_doc = response.read()

        self.soup = BeautifulSoup(html_doc, 'html.parser')

    def _find_description(self):
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

        # more heading tags
        street_address = tags.find('h1', itemprop='streetAddress').string
        street_address = str(street_address)

        # paragraph tags
        p = tags.find_all('p')
        tenure_string = 'Tenure:'
        [tenure] = [t.contents[1].string.strip() for t in p if t.contents[0].string == tenure_string]

        # price
        price_pattern = r'£\d{3},\d{3}'
        price = tags.find(string=re.compile(price_pattern))
        price = int(price[1:].replace(',', ''))

        # property added date
        added_date_pattern = r'\d{2}/\d{2}/\d{4}'
        added_date_full_pattern = r'Added on ' + added_date_pattern
        added_date = tags.find(string=re.compile(added_date_full_pattern))
        added_date = re.search(added_date_pattern, added_date).group()
        added_date = datetime.strptime(added_date, '%d/%m/%Y')

        # save into the dict
        self.property_dict[self.id]['property_details']['Tenure'] = tenure
        self.property_dict[self.id]['property_details']['Property Description'] = property_description
        self.property_dict[self.id]['property_details']['Price'] = price
        self.property_dict[self.id]['property_details']['Key Features'] = key_features
        self.property_dict[self.id]['property_details']['Added Date'] = added_date
        self.property_dict[self.id]['property_details']['Street Address'] = street_address

    def _find_photos(self):
        tags = self.soup.head.find_all('meta')
        for tag in tags:
            if tag.attrs.get('property') == 'og:image':
                self.photo_urls.append(tag['content'])

    def _find_floorplan(self):
        floorplan_page_url = self.property_url + self.floorplan_url_endpoint

        with urlopen(floorplan_page_url) as response:
            html_doc = response.read()

        soup = BeautifulSoup(html_doc, 'html.parser')

        [tag] = soup.body.find_all(alt='Floorplan')
        floorplan_url = tag['src']

        # remove the image size control _max_296x197.jpeg
        pattern = r'_max_\d+x\d+'
        replace = ''
        self.floorplan_url = re.sub(pattern, replace, floorplan_url)

    def _map_url_to_local_file(self):
        folder_name = self.rightmove_prefix + str(self.id)
        self.image_folder = os.path.join(self.image_folder_stub, folder_name)

        # create list of tuple pairs for photos
        for photo_url in self.photo_urls:
            filename = photo_url.split('/')[-1]
            filename = os.path.join(self.image_folder, filename)
            self.property_dict[self.id]['photos'].append(tuple([photo_url, filename]))

        # create single tuple pair for floorplan
        filename = self.floorplan_url.split('/')[-1]
        filename = os.path.join(self.image_folder, filename)
        self.property_dict[self.id]['floorplan'] = (self.floorplan_url, filename)

    def _create_folder_on_local_drive(self):
        # create folder if it doesnt exist
        Path(self.image_folder).mkdir(parents=True, exist_ok=True)

    def _save_photos(self):
        for photo_url, filename in self.property_dict[self.id]['photos']:
            # open the url and save the image
            with urlopen(photo_url) as in_stream, open(filename, 'wb') as out_file:
                copyfileobj(in_stream, out_file)

    def _save_floorplan(self):
        floorplan_url, filename = self.property_dict[self.id]['floorplan']
        # open the url and save the image
        with urlopen(floorplan_url) as in_stream, open(filename, 'wb') as out_file:
            copyfileobj(in_stream, out_file)

    def collect_a_property(self):
        self._get_property_url()
        self._get_soup()
        self._find_description()
        self._find_photos()
        self._find_floorplan()
        self._map_url_to_local_file()
        if self.image_scrape:
            self._create_folder_on_local_drive()
            self._save_photos()
            self._save_floorplan()
        return self.property_dict


class Viewer:

    def __init__(self, key=None):
        with shelve.open(Properties.rightmove_filename) as db:
            if key:
                self.key = key
            else:
                keys = sorted(list(db.keys()))
                self.key = keys[-1]
            self.properties_dict = db[self.key]

    def save(self):
        with shelve.open(Properties.rightmove_filename) as db:
            db[self.key] = self.properties_dict


class Enrich(Viewer):
    enrich_dict = {110103536: {'enriched_details': {
        'what3words': 'plank.barks.stick',
        'street_address': '44 Cavell Rd, Oxford OX4 4AS',
        'sale_status': 'sold STC',
        'offer_accepted_date': '18-07-2021',
        'offer_level': 'over 550k'}},
        104647769: {'enriched_details': {
            'street_address': '9 Temple St, Oxford OX4 1JS', }}
    }

    def __init__(self):
        super().__init__()

    def enrich(self):
        for key in self.properties_dict.keys():
            self.properties_dict[key].update(Enrich.enrich_dict[key])
        self.save()


def collect_many_properties(ids, properties_dict={}, image_scrape=False):
    for id_ in ids:
        d = Scraper(id_, image_scrape=image_scrape).collect_a_property()
        properties_dict.update(d)
    return properties_dict


def save_all_data_as_new_file(properties_dict):
    key = Properties.today_as_string
    with shelve.open(Properties.rightmove_filename) as db:
        db[key] = properties_dict


def update_latest_data_with_single_property(id_, image_scrape=True):
    d = Scraper(id_, image_scrape=image_scrape).collect_a_property()
    with shelve.open(Properties.rightmove_filename) as db:
        keys = sorted(list(db.keys()))
        key = keys[-1]
        db[key][id_] = d


if __name__ == '__main__':

    ids = [104647769, 110103536]
    id_ = 107624576
    scrape = True
    view = False
    enrich = False
    add_one = False

    if scrape:
        dd = collect_many_properties(ids)
        save_all_data_as_new_file(dd)
        pp(dd)

    if view:
        v = Viewer()
        pp(v.properties_dict)

    if enrich:
        e = Enrich()
        e.enrich()
        pp(e.properties_dict)

    if add_one:
        update_latest_data_with_single_property(id_=107624576, image_scrape=False)

