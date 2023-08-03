# items.py
from scrapy.item import Item, Field


class ProductItem(Item):
    id = Field()
    name = Field()
    cost_price = Field()
    sale_price = Field()
    first_price = Field()
    second_price = Field()
