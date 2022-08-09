"""
name: document
author：kavinbj
createdAt: 2021/7/26
version: 1.0.0
description:

"""
import logging
import reprlib
from asyncio.unix_events import _UnixSelectorEventLoop
from bson.objectid import ObjectId
from datetime import datetime
from abc import abstractmethod
from .exceptions import AioMongoConnectError, AioMongoAttributeError, AioMongoDocumentDoesNotExist
from .client import AioClient
from .utils import func_call
from .meta_base import MetaBase
from .collections import AioCollection
from motor.core import ClientSession
from motor.motor_asyncio import AsyncIOMotorCursor
from typing import (
    Optional,
    Union,
    MutableMapping,
    Any,
    Sequence,
    Tuple,
    Mapping,
    TypeVar
)

_Document = TypeVar("_Document", bound="Document")

logger = logging.getLogger(__name__)

_ID = '_id'
_DATA = '__doc_data__'


class AbstractDocument(metaclass=MetaBase):
    __abstract__ = True

    @abstractmethod
    def __getattr__(self, item):
        pass

    @abstractmethod
    def __setattr__(self, key, value):
        pass

    @abstractmethod
    def __delattr__(self, item):
        pass

    @abstractmethod
    def __contains__(self, item):
        pass

    @abstractmethod
    def __iter__(self):
        return iter([])

    @abstractmethod
    def __eq__(self, other):
        return False

    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def __delitem__(self, key):
        pass

    @abstractmethod
    def __len__(self):
        return 0


class Document(AbstractDocument):
    aio_collection = AioCollection()

    @classmethod
    async def init_db(
        cls,
        url: str = None,
        db_name: str = 'test',
        client_name: str = '__local__',
        io_loop: _UnixSelectorEventLoop = None,
        **kwargs
    ) -> AioClient:
        """
        init mongodb method, create AioClient instance and set class attribute __aio_client__
        check mongodb server health
        :param url: mongodb url
        :param db_name: database name
        :param client_name: name for cache aio client
        :param io_loop: asyncio event loop
        :param kwargs:
        :return:
        """
        aio_client = AioClient(client_name=client_name, url=url, cache=False, io_loop=io_loop, **kwargs)
        setattr(cls, '__db_name__', db_name)
        setattr(cls, '__aio_client__', aio_client)
        await cls.check_health()
        return aio_client

    @classmethod
    async def check_health(cls):
        aio_client = getattr(cls, '__aio_client__', None)
        if aio_client is not None:
            try:
                server_info = await aio_client.server_info()
                logger.info(f'mongodb connecting '
                            f'{"successful" if server_info and isinstance(server_info, dict) else "failed"}.')
            except Exception:
                raise AioMongoConnectError('mongodb connecting error.')

    def check_key_value(
        self,
        key: str,
        value: Any
    ) -> bool:
        """
        check key and value type by __schema__ defined by document sub-class
        :param key: field key
        :param value: field value
        :return:
        """
        if key == '_id':
            return True

        if key not in self.__schema__:
            raise AioMongoAttributeError(f'{type(self).__name__!r} object has no attribute {key!r} definition.')

        if not isinstance(value, self.__schema__[key]['type']):
            raise AioMongoAttributeError(f'in {type(self).__name__!r}, '
                                         f'{key!r} has not correct type {self.__schema__[key]["type"]}.')

        return key in self.__schema__ and isinstance(value, self.__schema__[key]['type'])

    def __getattr__(self, key):
        """
        get instance attribute, e.g.  user.name
        :param key:
        :return:
        """
        try:
            return self[key]
        except KeyError:
            raise AioMongoAttributeError(f'{type(self).__name__!r} object has no attribute {key!r}')

    def __setattr__(self, key, value):
        """
        set instance attribute, e.g. user.name = 'kavin'
        :param key:
        :param value:
        :return:
        """
        self[key] = value

    def __delattr__(self, key):
        """
        del instance attribute
        :param key:
        :return:
        """
        try:
            del self[key]
        except KeyError:
            raise AioMongoAttributeError(f'{type(self).__name__!r} object has no attribute {key!r}')

    def __getitem__(self, key):
        """
        get value by key value, e.g.  user['name']
        :param key:
        :return:
        """
        return vars(self)[_DATA][key]

    def __setitem__(self, key, value):
        """
        set value by key value, e.g.  user['name'] = 'kavin'
        :param key:
        :param value:
        :return:
        """
        if self.check_key_value(key, value):
            vars(self)[_DATA][key] = value

    def __delitem__(self, key):
        """
        del value by key value, e.g.  del user['name']
        :param key:
        :return:
        """
        del vars(self)[_DATA][key]

    def __contains__(self, item):
        """
        check if instance contain item,  e.g. if 'name' in user:
        :param item:
        :return:
        """
        return item in vars(self)[_DATA]

    def __iter__(self):
        """
        iterate item,  e.g.  for item in user:
        :return:
        """
        return iter(vars(self)[_DATA])

    def __eq__(self, other) -> bool:
        """
        Compare two instance objects
        :param other:
        :return: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return vars(self)[_DATA] == vars(other)[_DATA]

    def __len__(self) -> int:
        """
        return the number of items in the instance
        :return: int
        """
        return len(vars(self)[_DATA])

    def __repr__(self) -> str:
        """
        return a description string of the instance
        :return:
        """
        name = type(self).__name__
        repr_ = reprlib.repr(vars(self)[_DATA])
        return f'<{name}({repr_})>'

    async def save(
        self,
        session: Optional[ClientSession] = None,
        **kwargs
    ) -> _Document:
        """
        save document to DB
        :param session: ClientSession instance for transaction operation
        :param kwargs:
        :return:
        """
        if _ID not in self:
            await func_call(self.pre_save)
            result = await type(self).aio_collection.insert_one(vars(self)[_DATA], session=session, **kwargs)
            vars(self)[_DATA][_ID] = result.inserted_id
            await func_call(self.after_save)
            return self
        else:
            await func_call(self.pre_save)
            await type(self).aio_collection.replace_one({_ID: self[_ID]}, vars(self)[_DATA], session=session, **kwargs)
            await func_call(self.after_save)
            return self

    def pre_save(self) -> None:
        """
        Hook before save.
        :return:
        """
        if _ID not in self:
            if 'createdAt' in self.__schema__:
                self['createdAt'] = datetime.now()

        if 'updatedAt' in self.__schema__:
            self['updatedAt'] = datetime.now()
        logger.info(f'{self.__class__.__name__} pre saved from the db.')
        pass

    def after_save(self) -> None:
        """
        Hook after save.
        :return:
        """
        pass

    async def delete(
        self,
        session: Optional[ClientSession] = None
    ) -> None:
        """
        delete document instance
        :param session: ClientSession instance for transaction operation
        :return:
        """
        if _ID not in self:
            raise AioMongoDocumentDoesNotExist('document not saved.')

        result = await type(self).aio_collection.delete_one({_ID: self[_ID]}, session=session)
        if result:
            del self[_ID]

    async def refresh(
        self,
        session: Optional[ClientSession] = None
    ) -> _Document:
        """
        return document instance from DB
        :param session: ClientSession instance for transaction operation
        :return:
        """
        if _ID not in self:
            raise AioMongoDocumentDoesNotExist('document not exist.')

        res = await type(self).aio_collection.find_one({_ID: self[_ID]}, session=session)
        vars(self)[_DATA] = res
        return self

    @classmethod
    def create_instance(
        cls,
        obj: object,
        **kwargs
    ) -> Optional[_Document]:
        """
        class method which create a document instance through an object, e.g.
         User.create_instance({'name': 'kavin', 'age': 30})
        :param obj: an object instance
        :param kwargs:
        :return:
        """
        if obj is None or not isinstance(obj, dict):
            return None

        _instance = cls.__call__(**kwargs)
        for key in obj:
            _instance[key] = obj[key]
        return _instance

    @classmethod
    async def find_by_id(
        cls,
        oid: Union[str, ObjectId],
        session: Optional[ClientSession] = None
    ) -> Optional[_Document]:
        """
        document query based on document ID
        :param oid: document ID
        :param session: ClientSession instance for transaction operation
        :return:
        """
        if oid is None or oid == '':
            return None
        try:
            result = await cls.aio_collection.find_one({_ID: ObjectId(oid)}, session=session)
            return cls.create_instance(result)
        except Exception as e:
            raise AioMongoDocumentDoesNotExist(str(e))

    @classmethod
    async def delete_by_id(
        cls,
        oid: Union[str, ObjectId],
        session: Optional[ClientSession] = None
    ) -> None:
        """
        delete document instance according to document ID
        :param oid: document ID
        :param session: ClientSession instance for transaction operation
        :return:
        """
        if oid is None or oid == '':
            raise AioMongoDocumentDoesNotExist('oid is None')

        try:
            result = await cls.aio_collection.delete_one({_ID: ObjectId(oid)}, session=session)
            return result.deleted_count
        except Exception as e:
            raise AioMongoDocumentDoesNotExist(str(e))

    @classmethod
    def find(
        cls,
        *args,
        session: Optional[ClientSession] = None,
        **kwargs
    ) -> AsyncIOMotorCursor:
        """
        document query, create a MotorCursor.
        :param args:
        :param session: ClientSession instance for transaction operation
        :param kwargs:
        :return:
        """
        return cls.aio_collection.find(*args, session=session, **kwargs)

    @classmethod
    async def find_one(
        cls,
        filters: Optional[Any] = None,
        *args: Any,
        session: Optional[ClientSession] = None,
        **kwargs: Any
    ) -> Optional[_Document]:
        """
        Returns a single document, or None if no matching document is found.
        :param filters:  a dictionary specifying the query to be performed OR any other type to be used as
        the value for a query for "_id".
        :param args: any additional positional arguments are the same as the arguments to find()
        :param session: ClientSession instance for transaction operation
        :param kwargs:
        :return:
        """
        result = await cls.aio_collection.find_one(filters, *args, session=session, **kwargs)
        return cls.create_instance(result)

    @classmethod
    async def count(
        cls,
        *filters: Mapping[str, Any],
        session: Optional[ClientSession] = None,
        **kwargs
    ) -> int:
        """
        Count the number of documents in this collection.
        e.g.
        1、 users_num = await User.count()
        2、 users_name_num = await User.count({'name': 'kavin'})
        3、 users_age_num = await User.count({'age': {$gt: 30}}})

        All optional parameters should be passed as keyword arguments to this method. Valid options include:
         skip (int): The number of matching documents to skip before returning results.
         limit (int): The maximum number of documents to count. Must be a positive integer.
                      If not provided, no limit is imposed.
         maxTimeMS (int): The maximum amount of time to allow this operation to run, in milliseconds.
         collation (optional): An instance of Collation.
         hint (string or list of tuples): The index to use. Specify either the index name as a string or the index
             specification as a list of tuples (e.g. [(‘a’, pymongo.ASCENDING), (‘b’, pymongo.ASCENDING)]).

        :param filters: A query document that selects which documents to count in the collection.
        Can be an empty document to count all documents.
        :param session: ClientSession instance for transaction operation
        :param kwargs:
        :return:
        """
        _filter = {} if filters == () else filters[0]
        return await cls.aio_collection.count_documents(_filter, session=session, **kwargs)

    @classmethod
    def get_collection(
        cls,
        db_name: str = None
    ) -> AioCollection:
        """
        get aio collection through the specified db name, if db_name is not None
        :param db_name: database name
        :return:
        """
        if db_name is not None:
            cls.__db_name__ = db_name

        return cls.aio_collection

    @classmethod
    async def create_index(
        cls,
        session: Optional[ClientSession] = None,
        **kwargs: Any
    ) -> list:
        """
        create index on this collection.
        When defining document subclasses, index can be defined in schema，
        In this function, we will create all the previously defined default indexes one by one
        return index str list
        e.g.
            class User(Document):
                __schema__ = {
                   'name': {'type': str, 'default': 'my_default_name', 'index': -1},
                   'sex':  {'type': bool},
                   'age':  {'type': int, 'default': 20, 'index': 1},
                   'createdAt': {'type': datetime, 'index': -1},
                   'updatedAt': {'type': datetime}
                }
            res = await User.create_index()
            assert res == ['index_-1', 'age_1', 'createdAt_-1']

        :param session: ClientSession instance for transaction operation
        :param kwargs:
        :return:
        """
        _doc_index = []
        __schema__ = getattr(cls, '__schema__', None)
        if __schema__ is not None:
            for key in __schema__:
                if 'index' in __schema__[key]:
                    _doc_index.append((key, __schema__[key]['index']))

        if len(_doc_index) > 0:
            res_list = []
            for index_info in _doc_index:
                res = await cls.aio_collection.create_index([index_info], session=session, **kwargs)
                res_list.append(res)
            return res_list
        else:
            return []

    @classmethod
    async def create_compound_index(
        cls,
        keys: Union[str, Sequence[Tuple[str, Union[int, str, Mapping[str, Any]]]]],
        session: Optional[ClientSession] = None,
        **kwargs: Any
    ) -> str:
        """
        create compound index on this collection.
        e.g.
            class User(Document):
                __schema__ = {
                   'name': {'type': str, 'default': 'my_default_name', 'index': -1},
                   'sex':  {'type': bool},
                   'age':  {'type': int, 'default': 20, 'index': 1},
                   'createdAt': {'type': datetime, 'index': -1},
                   'updatedAt': {'type': datetime}
                }
            keys = [('name', 1), ('createdAt', -1)]
            res = await User.create_compound_index(keys)
            assert res == 'name_1_createdAt_-1'

        :param keys: list of index key and index value
        :param session: ClientSession instance for transaction operation
        :param kwargs:
        :return: compound index string
        """
        return await cls.aio_collection.create_index(keys, session=session, **kwargs)

    @classmethod
    async def get_index_infor(
        cls,
        session: Optional[ClientSession] = None,
        **kwargs: Any
    ) -> MutableMapping[str, Any]:
        """
        Get information on this collection’s indexes.
        :param session: ClientSession instance for transaction operation
        :param kwargs:
        :return:
        """
        return await cls.aio_collection.index_information(session=session, **kwargs)
