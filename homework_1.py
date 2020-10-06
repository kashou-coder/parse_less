from typing import List, Dict, Union
import datetime as dt
import copy
import os
from pathlib import Path
import json
import time
import requests


class Catalog5Ka:
    __urls = {
        'categories': 'https://5ka.ru/api/v2/categories/',
        'products': 'https://5ka.ru/api/v2/special_offers/'
    }

    __params = {
        'records_per_page': 50,
    }

    __headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
    }

    __replaces = (',', '-', '/', '\\', '.', '"', "'", '*', '#',)

    def __init__(self, folder_name='data'):
        self.folder_data = Path(os.path.dirname(__file__)).joinpath(folder_name)

    def __get_categories(self) -> List[Dict[str, str]]:
        response = requests.get(self.__urls['categories'])
        return response.json()

    def parse(self):
        for category in self.__get_categories():
            self.get_products(category)

    def get_response_data(self, url, params) -> Dict[str, Union[str, list]]:
        while True:
            response = requests.get(url, params=params, headers=self.__headers)
            if response.status_code != 200:
                time.sleep(0.5)
                continue
            return response.json()

    def get_products(self, category: Dict[str, Union[str, list]]):
        url = self.__urls['products']
        params = copy.copy(self.__params)
        params['categories'] = category['parent_group_code']

        while url:
            data = self.get_response_data(url, params)
            url = data['next']
            params = {}
            time.sleep(0.2)

            if category.get('products'):
                category['products'].extend(data['results'])
            else:
                category['products'] = data['results']

        category['parse_date'] = dt.datetime.now().timestamp()
        self.save_to_file(category)

    def save_to_file(self, category):
        name = category['parent_group_name']
        for itm in self.__replaces:
            name = name.replace(itm, '')
        name = '_'.join(name.split()).lower()

        file_path = os.path.join(self.folder_data, f'{name}.json')

        with open(file_path, 'w', encoding='UTF-8') as file:
            json.dump(category, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Catalog5Ka()
    parser.parse()
    print(1)