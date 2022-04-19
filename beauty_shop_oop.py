import json
import os
from os import path
import pickle
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

BASE_URL = 'https://sisters.co.ua'


@dataclass
class Product:
    name: str
    category: str
    price: int
    brand: str
    img_link: str
    link_to_product: str
    img_path: str

    id: int = 0
    volume: str = ''
    origin: str = ''
    gender: str = ''


class ProductList:
    def __init__(self):
        self.product_list = []
        self.i = 0

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.product_list:
            if self.i <= len(self.product_list) - 1:
                self.i += 1
                return self.product_list[self.i - 1]
        raise StopIteration

    def write_to_file(self):
        with open('products', 'wb') as file_object:
            pickle.dump(self, file_object)

    @classmethod
    def load_from_file(cls):
        try:
            with open('products', 'rb') as file_object:
                print('loaded')
                return pickle.load(file_object)
        except FileNotFoundError:
            return cls

    def data_from_web(self):
        self.product_list = self.collect_main_data()

    def pars_main(self, url: str) -> list:
        res = requests.get(url)
        bs = BeautifulSoup(res.text, 'lxml')
        cards_on_page = bs.find_all('div', class_='card')
        product_list = []
        for card in cards_on_page:
            link = BASE_URL + card.find('a').attrs['href']
            name = card.find('div', class_='card-inner').text.strip()
            category = card.find('div', class_='card-category').text.strip().strip('#')
            try:
                price = int(re.sub("[^0-9]", "", card.find('div', class_='card-price').find_all('p')[-1].text.strip()))
            except:
                price = None
                # print(link)
            img_link = BASE_URL + card.find('div', class_='card-image').find('img').attrs['src']
            brand = card.find('div', class_='card-brand').text.strip()
            img_path = img_link.split('/')[-1]
            product_list.append(Product(name, category, price, brand, img_link, link, img_path))
        return product_list

    def pars_extra(self, product: Product):
        res = requests.get(product.link_to_product)
        bs = BeautifulSoup(res.text, 'lxml')

        table = bs.find_all('tr')
        try:
            product.id = bs.find('meta', itemprop='mpn').attrs['content']
        except:
            product.id = None
            print(f'{product.link_to_product} нет id')
        for elem in table:
            if elem.find('th').text == 'Об\'єм':
                product.volume = elem.find('td').text.strip()
            elif elem.find('th').text == 'Країна':
                product.origin = elem.find('td').text.strip()
            elif elem.find('th').text == 'Стать':
                product.gender = elem.find('td').text.strip()
        out_list = []
        out_list.append(product)
        self.save_image(product)
        return out_list

    def pages_in_category(self, url: str) -> int:
        session = requests.Session()
        res = session.get(url)
        bs = BeautifulSoup(res.text, 'lxml')
        pag = bs.find_all('li', class_='next')
        return int(pag[-1].find('a').attrs['data-page']) + 1

    def grabber(self, links: list, parser):
        with ThreadPoolExecutor(10) as executor:
            elements = []
            threads = []
            for page in links:
                threads.append(executor.submit(parser, page))
            for page in as_completed(threads):
                elements += page.result()
        print(elements)
        return elements

    def collect_main_data(self):
        base_category_url = 'https://sisters.co.ua/kosmetyka-dlya-volossa/'
        pages_in_cat = self.pages_in_category(base_category_url)
        links_list = []
        for page in range(90, 91):
            # for page in range(1, pages_in_cat + 1):
            links_list.append(base_category_url + 'page/' + str(page))
        products = self.grabber(links_list, self.pars_main)
        full_products = self.grabber(products, self.pars_extra)
        return full_products

    def to_json(self):
        general_list = []
        for item in self.product_list:
            general_list.append(item.__dict__)
        with open('products.json', 'w') as file:
            json.dump(general_list, file, indent=4, ensure_ascii=False)

    def save_image(self, product: Product):
        path_to_img_dir = path.join(path.dirname(__file__), 'img_dir')
        if not os.path.exists(path_to_img_dir):
            os.mkdir(path_to_img_dir)
        path_to_img = path.join(path_to_img_dir, f"{product.id}.jpg")
        with open(path_to_img, "wb") as photo:
            photo.write(requests.get(product.img_link).content)


pl = ProductList()
pl.data_from_web()
# pl.to_json()
# pl.write_to_file()
# pl_2 = ProductList.load_from_file()
# pl_2.to_json()
# pl_2.save_image()
# for product in pl_2:
#     print(product.name)
#     pl_2.save_image(product)
