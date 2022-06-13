from enum import Enum, unique


@unique
class ShopUnitType(Enum):
    offer = 'OFFER'
    category = 'CATEGORY'