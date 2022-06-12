from datetime import date
from enum import Enum, unique

from marshmallow import Schema, ValidationError, validates, validates_schema
from marshmallow.fields import Date, Dict, Float, Int, List, Nested, Str
from marshmallow.validate import Length, OneOf, Range


BIRTH_DATE_FORMAT = '%d.%m.%Y'

@unique
class ShopUnitType(Enum):
    offer = 'OFFER'
    category = 'CATEGORY'


#Базовый класс для товаров/категорий, проверка на корректность введенной даты
class ShopThings(Schema):
    id=Str(nullable=False)
    name = Str(nullable=True)
    date = Date(format=BIRTH_DATE_FORMAT)
    parentId = Str(nullable=True)
    type=Str(validate=OneOf([unit.value for unit in ShopUnitType]))
    price=Int(validate=Range(min=0), strict=True, nullable=True)
    children=List(Dict(nullable=False))

    @validates('date')
    def validate_date(self, value: date):
        if value > date.today():
            raise ValidationError("Upgrade date can't be in future")

    @validates('relatives')
    def validate_relatives_unique(self, value: list):
        if len(value) != len(set(value)):
            raise ValidationError('relatives must be unique')

class ShopUnit(Schema):
    id = Str($uuid)
    nullable: false
    example: 3
    fa85f64 - 5717 - 4562 - b3fc - 2
    c963f66a333
    Уникальный
    идентфикатор

    name * string
    nullable: false
    Имя
    элемента.

    parentId
    string($uuid)
    nullable: true
    example: 3
    fa85f64 - 5717 - 4562 - b3fc - 2
    c963f66a333
    UUID
    родительской
    категории

    type * ShopUnitTypestring
    Тип
    элемента - категория
    или
    товар

    Enum:
    Array[2]
    price
    integer($int64)
    nullable: true
    Целое
    число, для
    категорий
    поле
    должно
    содержать
    null.