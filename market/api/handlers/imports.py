from http import HTTPStatus
from typing import Generator

from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema, response_schema
from aiomisc import chunk_list

from market.api.scheme import ImportResponseSchema, ImportSchema
from market.db.scheme import imports_table, offer_and_category_table, child_parent_table
from market.utils.pg import MAX_QUERY_ARGS

from .base import BaseView


class ImportsView(BaseView):
    URL_PATH = '/imports'
    # Так как данных может быть много, а postgres поддерживает только
    # MAX_QUERY_ARGS аргументов в одном запросе, писать в БД необходимо
    # частями.
    # Максимальное кол-во строк для вставки можно рассчитать как отношение
    # MAX_QUERY_ARGS к кол-ву вставляемых в таблицу столбцов.
    MAX_CITIZENS_PER_INSERT = MAX_QUERY_ARGS // len(offer_and_category_table.columns)
    MAX_RELATIONS_PER_INSERT = MAX_QUERY_ARGS // len(child_parent_table.columns)


    @classmethod
    def make_offers_table_rows(cls, offers, import_id) -> Generator:
        """
        Генерирует данные готовые для вставки в таблицу citizens (с ключом
        import_id и без ключа relatives).
        """
        def generate_dict(id, name, parentId, price, type):
            return {
                    'import_id': import_id,
                    'id': id,
                    'name': name,
                    'parentId': parentId,
                    'price': price,
                    'type': type,
                }

        def generate_rows(sl, sp=[]):
            if sl.get('type') == 'OFFER' and sl.get('children') == None:
                sp.append(generate_dict(sl.get('id'), sl.get('name'), sl.get('parentId'), sl.get('price'), sl.get('type')))
            if sl.get('type') == 'CATEGORY' and sl.get('children') == None:
                sp.append(
                    generate_dict(sl.get('id'), sl.get('name'), sl.get('parentId'), sl.get('price'), sl.get('type')))
            if sl.get('type') == 'CATEGORY' and sl.get('children') != None:
                sp.append(
                    generate_dict(sl.get('id'), sl.get('name'), sl.get('parentId'), sl.get('price'), sl.get('type')))
                for i in range(len(sl.get('children'))):
                    generate_rows(sl.get('children')[i], sp)
            return sp

        for offer in generate_rows(offers):
            yield offer



    @classmethod
    def make_relations_table_rows(cls, items, import_id) -> Generator:
        """
        Генерирует данные готовые для вставки в таблицу relations.
        """
        for object in items:
            for child in object['child']:
                yield {
                    'import_id': import_id,
                    'child': object['citizen_id'],
                    'parent': relative_id,
                }

    @docs(summary='Добавить выгрузку с информацией о жителях')
    @request_schema(ImportSchema())
    @response_schema(ImportResponseSchema(), code=HTTPStatus.CREATED.value)
    async def post(self):
        # Транзакция требуется чтобы в случае ошибки (или отключения клиента,
        # не дождавшегося ответа) откатить частично добавленные изменения.
        async with self.pg.transaction() as conn:
            # Создаем выгрузку
            query = imports_table.insert().returning(imports_table.c.import_id)
            import_id = await conn.fetchval(query)

            # Генераторы make_citizens_table_rows и make_relations_table_rows
            # лениво генерируют данные, готовые для вставки в таблицы citizens
            # и relations на основе данных отправленных клиентом.
            citizens = self.request['data']['citizens']
            citizen_rows = self.make_offers_table_rows(citizens, import_id)
            relation_rows = self.make_relations_table_rows(citizens, import_id)

            # Чтобы уложиться в ограничение кол-ва аргументов в запросе к
            # postgres, а также сэкономить память и избежать создания полной
            # копии данных присланных клиентом во время подготовки - используем
            # генератор chunk_list.
            # Он будет получать из генератора make_citizens_table_rows только
            # необходимый для 1 запроса объем данных.
            chunked_citizen_rows = chunk_list(citizen_rows,
                                              self.MAX_CITIZENS_PER_INSERT)
            chunked_relation_rows = chunk_list(relation_rows,
                                               self.MAX_RELATIONS_PER_INSERT)

            query = citizens_table.insert()
            for chunk in chunked_citizen_rows:
                await conn.execute(query.values(list(chunk)))

            query = relations_table.insert()
            for chunk in chunked_relation_rows:
                await conn.execute(query.values(list(chunk)))

        return Response(body={'data': {'import_id': import_id}},
                        status=HTTPStatus.CREATED)