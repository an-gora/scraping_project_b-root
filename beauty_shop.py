import json
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

    def download_data(self):
        pass


class ProductList:
    def __iter__(self):
        session = requests.Session()
        res = session.get(url)
        bs = BeautifulSoup(res.text, 'lxml')

    def __next__(self):
        pass


# def create_b_soup(url: str)->BeautifulSoup:
#     res = requests.get(url)
#     bs = BeautifulSoup(res.text, 'lxml')


def pars_main(url: str) -> list:
    res = requests.get(url)
    bs = BeautifulSoup(res.text, 'lxml')
    cards_on_page = bs.find_all('div', class_='card')
    # links_list = []
    product_list = []
    for card in cards_on_page:
        link = BASE_URL + card.find('a').attrs['href']
        name = card.find('div', class_='card-inner').text.strip()
        category = card.find('div', class_='card-category').text.strip().strip('#')
        try:
            price = int(re.sub("[^0-9]", "", card.find('div', class_='card-price').text.strip()))
        except:
            price = None
            print(link)
        img_link = BASE_URL + card.find('div', class_='card-image').find('img').attrs['src']
        brand = card.find('div', class_='card-brand').text.strip()
        img_path = img_link.split('/')[-1]
        # id = bs.find('div', class_='card-footer').find('button').attrs['data-id']
        product_list.append(Product(name, category, price, brand, img_link, link, img_path))
    # print(product_list)
    # print(url)
    return product_list


def pars_extra(product: Product):
    res = requests.get(product.link_to_product)
    bs = BeautifulSoup(res.text, 'lxml')

    table = bs.find_all('tr')
    try:
        # product.id = bs.find('meta', itemprop='mpn').attrs['content']
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
    return out_list


def pages_in_category(url: str) -> int:
    session = requests.Session()
    res = session.get(url)
    bs = BeautifulSoup(res.text, 'lxml')
    pag = bs.find_all('li', class_='next')
    return int(pag[-1].find('a').attrs['data-page']) + 1


def grabber(links: list, parser):
    with ThreadPoolExecutor(10) as executor:
        elements = []
        threads = []
        for page in links:
            threads.append(executor.submit(parser, page))
        for page in as_completed(threads):
            elements += page.result()
    # print(elements)
    return elements


def collect_main_data():
    base_category_url = 'https://sisters.co.ua/kosmetyka-dlya-volossa/'
    pages_in_cat = pages_in_category(base_category_url)
    links_list = []
    for page in range(90, 91):
    # for page in range(1, pages_in_cat + 1):
        links_list.append(base_category_url + 'page/' + str(page))
    products = grabber(links_list, pars_main)
    full_products = grabber(products, pars_extra)
    return full_products


def to_json(data: list):
    general_list = []
    for item in data:
        general_list.append(item.__dict__)
    with open('products_test.json', 'w') as file:
        json.dump(general_list, file, indent=4, ensure_ascii=False)


list_of_shamp = collect_main_data()
collect_main_data()
# print('-----------')
# for item in list_of_shamp:
#     print(item)
# print(len(list_of_shamp))
to_json(list_of_shamp)
