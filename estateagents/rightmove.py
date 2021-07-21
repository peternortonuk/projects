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


class Property:

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


class Scrape(Property):
    """
    This class performs a single scrape it builds a dict of data and saves images to a local drive
    """

    def __init__(self, id_, image_scrape=False):
        self.id = id_
        self.image_scrape = image_scrape
        self.property_dict = {self.id: copy.deepcopy(Property.empty_details_dict)}
        self.floorplan_url = ''
        self.photo_urls = []

    def _get_page_url(self):
        self.page_url = self.property_url_template.format(id_=self.id)
        self.property_dict[self.id]['property_url'] = self.page_url

    def _get_soup(self):
        with urlopen(self.page_url) as response:
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
        floorplan_page_url = self.page_url + self.floorplan_url_endpoint

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
        self._get_page_url()
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


class DAO:
    """
    This class interfaces with the shelve object.
    """

    def __init__(self, key=None):
        self.rightmove_filename = Property.rightmove_filename
        self.properties_dict = {}
        with shelve.open(self.rightmove_filename) as db:
            keys = list(db.keys()) or []
            self.keys = sorted(keys)
            if key in self.keys:
                self.key = key
            else:
                self.key = self.keys[-1]

    def create_new_key(self):
        today = date.today()
        self.key = datetime.strftime(today, '%Y%m%d')

    def load(self):
        with shelve.open(self.rightmove_filename) as db:
            self.properties_dict = db[self.key]

    def save(self):
        if self.properties_dict != {}:
            with shelve.open(self.rightmove_filename) as db:
                db[self.key] = self.properties_dict

    def update(self, single_property_dict):
        with shelve.open(self.rightmove_filename) as db:
            self.properties_dict = db[self.key]
            self.properties_dict.update(single_property_dict)
            db[self.key] = self.properties_dict

    def update_enriched_details(self, id_, enriched_details_dict):
        with shelve.open(self.rightmove_filename) as db:
            self.properties_dict = db[self.key]
            self.properties_dict[id_].update(enriched_details_dict)
            db[self.key] = self.properties_dict

    def delete_version(self, key):
        with shelve.open(self.rightmove_filename) as db:
            keys = list(db.keys()) or []
            if key in keys:
                self.key = key
            del db[key]


class Scrapes(DAO):
    """
    This class inherits from DAO so it can interface with the shelve object
    And uses the Scrape (single property) class to run multiple scrapes where required
    """
    def __init__(self):
        super().__init__()
        self.load()

    def collect_many_properties(self, ids, image_scrape=False):
        for id_ in ids:
            d = Scrape(id_, image_scrape=image_scrape).collect_a_property()
            self.properties_dict.update(d)

    def save_all_data_as_new_file(self):
        self.create_new_key()
        self.save()

    def update_latest_data_with_single_property(self, id_, image_scrape=True):
        single_property_dict = Scrape(id_, image_scrape=image_scrape).collect_a_property()
        self.update(single_property_dict)


class Enrich(DAO):
    enrich_dict = {
        110103536: {'enriched_details':
            {
            'what3words': 'plank.barks.stick',
            'street_address': '44 Cavell Rd, Oxford OX4 4AS',
            'sale_status': 'sold STC',
            'offer_accepted_date': '18-07-2021',
            'offer_level': 'over 550k'}
            },
        104647769: {'enriched_details':
            {
            'street_address': '9 Temple St, Oxford OX4 1JS',
            }
        }
    }

    def __init__(self):
        super().__init__()
        self.load()

    def enrich(self):
        for id_, enriched_details_dict in Enrich.enrich_dict.items():
            self.update_enriched_details(id_, enriched_details_dict)


class Favourites():

    def __init__(self):
        self.page_url = r'https://www.rightmove.co.uk/user/shortlist.html'

    def _get_soup(self):
        with urlopen(self.page_url) as response:
            html_doc = response.read()

        self.soup = BeautifulSoup(html_doc, 'html.parser')

    def _find_favourites(self):
        """
        <a href="/properties/110423867" data-test="saved-property-title"><span class="title">Victor Street, Jericho</span></a>
        :return:
        """
        pattern = r'/properties/\d+'
        tags = self.soup.body.find_all('div', id='content')
        ids = []  # tags.find_all('a', string=re.compile(pattern))
        return ids

    def collect_favourites(self):
        self._get_soup()
        return self._find_favourites()


if __name__ == '__main__':

    ids = [104647769, 110103536]
    id_ = 107624576
    db_version = '20210720'

    scrape = False
    scrapes = False
    view = False
    enrich = False
    add_one = False
    delete_a_key = False
    collect_favourites = False

    if scrape:
        dd = Scrape(id_).collect_a_property()
        pp(dd)

    if scrapes:
        s = Scrapes()
        s.collect_many_properties(ids)
        s.create_new_key()
        s.save()
        pp(s.properties_dict)

    if view:
        v = DAO()
        v.load()
        pp(v.properties_dict)

    if enrich:
        e = Enrich()
        e.enrich()
        pp(e.properties_dict)

    if add_one:
        s = Scrapes()
        s.update_latest_data_with_single_property(id_=107624576, image_scrape=False)
        pp(s.properties_dict)

    if delete_a_key:
        d = DAO()
        d.delete_version(db_version)

    if collect_favourites:
        f = Favourites().collect_favourites()



