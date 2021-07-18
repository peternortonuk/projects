from urllib.request import urlopen
from shutil import copyfileobj
from pathlib import Path
import re
from bs4 import BeautifulSoup
import os
import shelve
from datetime import date, datetime
from pprint import pprint as pp


class Properties:

    def __init__(self, ids):
        today = date.today()
        self.today_as_string = datetime.strftime(today, '%Y%m%d')
        self.rightmove_prefix = 'rm'  # for folder names
        self.page_url_template = r'https://www.rightmove.co.uk/properties/{id_}#/'
        self.floorplan_url_endpoint = r'floorplan?activePlan=1'
        self.project_folder = r'c:\dev\code\projects\estateagents'
        self.image_folder_stub = os.path.join(self.project_folder, 'images')
        self.rightmove_filename = os.path.join(self.project_folder, 'rightmove')
        self.ids = ids

        empty_details_dict = {
            'photo_urls': [],
            'floorplan_url': None,
            'photo_filenames': [],
            'floorplan_image_filename': None,
            'property_text': None,
        }
        self.properties_dict = {id_: empty_details_dict for id_ in self.ids}


class Scraper(Properties):

    def __init__(self, ids):
        super().__init__(ids)

    def _get_soup(self, id_):
        page_url = self.page_url_template.format(id_=id_)

        with urlopen(page_url) as response:
            html_doc = response.read()

        self.soup = BeautifulSoup(html_doc, 'html.parser')

    def _find_description(self, id_):
        tags = self.soup.body.find('div', id='root')

        # heading tags
        h2 = tags.find_all('h2')

        key_features_string = 'Key features'
        [key_features_tag] = [t for t in h2 if t.string == key_features_string]

        property_description_string = 'Property description'
        [property_description_tag] = [t for t in h2 if t.string == property_description_string]

        # paragraph tags
        p = tags.find_all('p')
        tenure_string = 'Tenure:'
        [tenure] = [t.contents[1].string for t in p if t.contents[0].string == tenure_string]
        tenure = tenure.strip()

    def _find_photos(self, id_):
        tags = self.soup.head.find_all('meta')
        for tag in tags:
            if tag.attrs.get('property') == 'og:image':
                self.properties_dict[id_]['photo_urls'].append(tag['content'])

    def _find_floorplan(self, id_):
        page_url = self.page_url_template.format(id_=id_)
        self.properties_dict[id_]['floorplan_url'] = page_url + self.floorplan_url_endpoint

        with urlopen(self.properties_dict[id_]['floorplan_url']) as response:
            html_doc = response.read()

        soup = BeautifulSoup(html_doc, 'html.parser')

        [tag] = soup.body.find_all(alt='Floorplan')
        floorplan_image_url = tag['src']

        # remove the image size control _max_296x197.jpeg
        pattern = r'_max_\d+x\d+'
        replace = ''
        floorplan_image_url = re.sub(pattern, replace, floorplan_image_url)
        self.properties_dict[id_]['floorplan_url'] = floorplan_image_url

    def _save_photos(self, id_):
        for photo_url in self.properties_dict[id_]['photo_urls']:
            filename = photo_url.split('/')[-1]
            filename = os.path.join(self.image_folder, filename)
            self.properties_dict[id_]['photo_filenames'].append(filename)

            # open the url and save the image
            with urlopen(photo_url) as in_stream, open(filename, 'wb') as out_file:
                copyfileobj(in_stream, out_file)

    def _save_description(self, id_):
        pass

    def _create_folder_on_local_drive(self, id_):
        # create folder name and path
        folder_name = self.rightmove_prefix + str(id_)
        self.image_folder = os.path.join(self.image_folder_stub, folder_name)

        # create folder if it doesnt exist
        Path(self.image_folder).mkdir(parents=True, exist_ok=True)

    def _save_floorplan(self, id_):
        # get the filename from the url and add full path to dict
        filename = self.properties_dict[id_]['floorplan_url'].split('/')[-1]
        self.properties_dict[id_]['floorplan_image_filename'] = os.path.join(self.image_folder, filename)

        # open the url and save the image
        with urlopen(self.properties_dict[id_]['floorplan_url']) as in_stream, open(self.properties_dict[id_]['floorplan_image_filename'], 'wb') as out_file:
            copyfileobj(in_stream, out_file)

    def collect_and_save(self):
        for id_ in self.ids:
            self._get_soup(id_)
            self._find_description(id_)
            self._find_photos(id_)
            self._find_floorplan(id_)
            self._create_folder_on_local_drive(id_)
            self._save_photos(id_)
            self._save_description(id_)
            self._save_floorplan(id_)

        version = self.today_as_string
        with shelve.open(self.rightmove_filename) as db:
            db[version] = self.properties_dict


if __name__ == '__main__':
    ids = [104647769, 110103536]
    s = Scraper(ids)
    s.collect_and_save()

    pp(s.properties_dict)
