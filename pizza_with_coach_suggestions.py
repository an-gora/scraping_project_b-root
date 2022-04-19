import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class PizzaPrice:
    price: str
    weight: str


@dataclass
class Pizza:
    name: str
    descr: str
    img: str
    variants: list[PizzaPrice]


class PizzasList:

    def __iter__(self):
        i = 0

        self.setup_class()
        self.fill_info(self.bs_data())

    def setup_class(self):
        self.pizza_list = []

    @staticmethod
    def bs_data() -> BeautifulSoup:
        res = requests.get('https://cipollino.ua/pizza', headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
        })
        return BeautifulSoup(res.text, 'lxml')

    def fill_info(self, bs: BeautifulSoup):
        for link in bs.find_all('div', class_='cipollino-product-item'):
            self.pizza_list.append(self.parse_product_block(link))

    @staticmethod
    def parse_product_block(link: BeautifulSoup) -> Pizza:
        pizza_name = link.find('div', class_="cipollino-product-name").text.strip()
        pizza_descr = link.find('div', class_='cipollino-product-ingredients').text.strip()
        pizza_image = link.find('img').attrs['data-src']
        price_class = link.find_all('div', class_="cipollino-product-option-price")
        pizza_prices = []

        for new_link in price_class:
            price = new_link.find('p', class_='cipollino-price').text
            weight = new_link.find('p', class_='cipollino-weight').text
            pizza = PizzaPrice(price=price, weight=weight)
            pizza_prices.append(pizza)

        return Pizza(name=pizza_name, descr=pizza_descr, img=pizza_image, variants=pizza_prices)

    def __next__(self) -> Pizza:
        if self.pizza_list:
            if self.i <= len(self.pizza_list) - 1:
                self.i += 1
                return self.pizza_list[self.i - 1]
        raise StopIteration


def main():
    base = PizzasList()
    base.__iter__()
    for item in base.pizza_list:
        print(item, end='\n')


if __name__ == '__main__':
    main()