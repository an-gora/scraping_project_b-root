import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class PizzaPrice:
    price: int
    weight: int


@dataclass
class Pizza:
    name: str
    descr: str
    img: str
    variants: list[PizzaPrice]


class PizzasList:

    def __iter__(self):
        self.pizza_list = []
        i = 0

        res = requests.get('https://cipollino.ua/pizza', headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
        })
        bs = BeautifulSoup(res.text, 'lxml')

        for link in bs.find_all('div', class_='cipollino-product-item'):
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

            new_pizza = Pizza(name=pizza_name, descr=pizza_descr, img=pizza_image, variants=pizza_prices)
            self.pizza_list.append(new_pizza)

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