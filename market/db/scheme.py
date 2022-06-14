from sqlalchemy import (
    Column, Date, Enum as PgEnum, ForeignKey, ForeignKeyConstraint, Integer,
    MetaData, String, Table, UniqueConstraint,
)

from market.api.shoptype import ShopUnitType


convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)




offer_and_category_table = Table(
    'offer_and_category',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('parentId', String, nullable=True),
    Column('date', Date, nullable=False),
    Column('price', Integer, default=0),
    Column('type', PgEnum(ShopUnitType, name='type'), nullable=False)
)

child_parent_table = Table(
    'child-parent',
    metadata,
    Column('child', String, ForeignKey('offer_and_category.id')),
    Column('parent', String, ForeignKey('offer_and_category.parentId'))
)
