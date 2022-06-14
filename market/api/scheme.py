from datetime import date

from marshmallow import Schema, ValidationError, validates, validates_schema
from marshmallow.fields import Date, Dict, Float, Int, List, Nested, Str
from marshmallow.validate import Length, OneOf, Range

from market.api.shoptype import ShopUnitType


DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"



# class PatchCitizenSchema(Schema):
#     name = Str(validate=Length(min=1, max=256))
#     type = Str(validate=OneOf([types.value for types in ShopUnitType]))
#     birth_date = Date(format=BIRTH_DATE_FORMAT)
#     town = Str(validate=Length(min=1, max=256))
#     street = Str(validate=Length(min=1, max=256))
#     building = Str(validate=Length(min=1, max=256))
#     price = Int(validate=Range(min=0), strict=True)
#     relatives = List(Int(validate=Range(min=0), strict=True))
#
#     @validates('birth_date')
#     def validate_birth_date(self, value: date):
#         if value > date.today():
#             raise ValidationError("Birth date can't be in future")
#
#     @validates('relatives')
#     def validate_relatives_unique(self, value: list):
#         if len(value) != len(set(value)):
#             raise ValidationError('relatives must be unique')


class OfferAndCategorySchema(Schema):
    id = Str(validate=Length(min=1, max=256), strict=True, required=True),
    name = Str(validate=Length(min=1, max=256), required=True)
    type = Str(validate=OneOf([types.value for types in ShopUnitType]),
                 required=True),
    parentId = Str(validate=Length(min=1, max=256), required=True)
    price = Int(validate=Range(min=0), strict=True, required=True)
    child = List(Dict(), required=True)


class ImportSchema(Schema):
    items = Nested(OfferAndCategorySchema, many=True, required=True,
                      validate=Length(max=10000))
    date = Date(format=DATE_FORMAT, required=True)

    @validates_schema
    def validate_unique_id(self, data, **_):
        ids = set()
        for goods in data['offer_and_category']:
            if goods['id'] in ids:
                raise ValidationError(
                    'id %r is not unique' % goods['id']
                )
            ids.add(goods['id'])


    #проверка, что товар (offer) не является родителем для кого-либо
    @validates_schema
    def validate_relatives(self, data, **_):
        child = {
            goods['type']: set(goods['child'])
            for goods in data['offer_and_category']
        }
        for types, list_children in child.items():
            if types == 'OFFER' and len(list_children) != 0:
                raise ValidationError(
                    400, 'offer can`t has child'
                )

#!!!!!!!!!!!!!!!
class ImportIdSchema(Schema):
    import_id = Int(strict=True, required=True)


class ImportResponseSchema(Schema):
    data = Nested(ImportIdSchema(), required=True)


class CitizensResponseSchema(Schema):
    data = Nested(OfferAndCategorySchema(many=True), required=True)


class PatchCitizenResponseSchema(Schema):
    data = Nested(OfferAndCategorySchema(), required=True)




class Error(Schema):
    code = Int(required=True)
    message = Str(required=True)


class ErrorResponseSchema(Schema):
    error = Nested(Error(), required=True)