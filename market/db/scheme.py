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


imports_table = Table(
    'imports',
    metadata,
    Column('import_id', Integer, primary_key=True),
    Column('updateDate', Date, nullable=False)
)

offer_and_category_table = Table(
    'offer_and_category',
    metadata,
    Column('import_id', Integer, ForeignKey('imports.import_id'),
           primary_key=True),
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('parentId', String, nullable=True),
    Column('price', Integer, default=0),
    Column('type', PgEnum(ShopUnitType, name='type'), nullable=False),
)

child_parent_table = Table(
    'child-parent',
    metadata,
    Column('import_id', Integer, primary_key=True),
    Column('child', String, primary_key=True),
    Column('parent', String, primary_key=True),
    ForeignKeyConstraint(
        ('import_id', 'child'),
        ('offer_and_category.import_id', 'offer_and_category.id')
    ),
    ForeignKeyConstraint(
        ('import_id', 'parent'),
        ('offer_and_category.import_id', 'offer_and_category.parentId')
    ),
)
