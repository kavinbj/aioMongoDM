"""
name: meta_base
author：felix
createdAt: 2022/7/29
version: 1.0.0
description:

"""
from .exceptions import AioMongoDMSchemaError
from .utils import find_token

# pymongo.ASCENDING = 1 # Ascending sort order.
# pymongo.DESCENDING = -1 # Descending sort order.
# pymongo.GEO2D = '2d' # Index specifier for a 2-dimensional geospatial index.
# pymongo.GEOSPHERE = '2dsphere' # Index specifier for a spherical geospatial index.
# pymongo.HASHED = 'hashed' # Index specifier for a hashed index.
# pymongo.TEXT = 'text' # Index specifier for a text index.

index_type_list = [1, -1, '2d', '2dsphere', 'hashed', 'text']


class MetaBase(type):
    def __new__(mcs, name, bases, clsargs):
        """
        mata class , check document subclass definition and create a document instance
        :param name:
        :param bases:
        :param clsargs:
        :return:
        """
        abstract = clsargs.pop('__abstract__', False)
        if abstract or name == 'Document':
            return super().__new__(mcs, name, bases, clsargs)

        _schema = clsargs.pop('__schema__', find_token(bases, '__schema__'))

        if _schema is None or not isinstance(_schema, dict):
            _schema = {}

        # check schema
        mcs.check_schema(_schema)

        cls = super().__new__(mcs, name, bases, clsargs)
        setattr(cls, '__schema__', _schema)

        return cls

    @staticmethod
    def check_schema(schema):
        """
        check schema
        e.g.
        class User(Document):
                __schema__ = {
                   'name': {'type': str, 'default': 'my_default_name', 'index': -1},
                   'sex':  {'type': bool},
                   'age':  {'type': int, 'default': 20, 'index': 1},
                   'createdAt': {'type': datetime, 'index': -1},
                   'updatedAt': {'type': datetime}
                }

        check parameters in __schema__

        :param schema:
        :return:
        """
        for field_key, field_definition in schema.items():
            if not isinstance(field_definition, dict):
                raise AioMongoDMSchemaError(f"field: '{field_key}' has error definition.")

            if 'type' not in field_definition.keys():
                raise AioMongoDMSchemaError(f"field: '{field_key}' not has 'type' definition.")

            if 'default' in field_definition and not isinstance(field_definition['default'], field_definition['type']):
                raise AioMongoDMSchemaError(f"field: '{field_key}' default value has error type.")

            if 'index' in field_definition and field_definition['index'] not in index_type_list:
                raise AioMongoDMSchemaError(f"field: '{field_key}' index value not as {index_type_list}.")

            error_key_list = [k for k in field_definition.keys() if k not in ['type', 'default', 'index']]
            if len(error_key_list) > 0:
                raise AioMongoDMSchemaError(f"field: '{field_key}' has error definition key {error_key_list}.")

    def __call__(cls, **kwargs):
        """
        create document subclass instance, and initial it
        :param kwargs:
        :return:
        """
        self = super().__call__()

        # initial instance
        _doc_data = {}
        __schema__ = getattr(cls, '__schema__', None)
        if __schema__ is not None:
            for key in __schema__:
                if 'default' in __schema__[key]:
                    _doc_data[key] = __schema__[key]['default']

        # set default value for __doc_data__
        vars(self)['__doc_data__'] = _doc_data

        for k, v in kwargs.items():
            self[k] = v

        return self
