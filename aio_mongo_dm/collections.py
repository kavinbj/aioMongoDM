"""
name: collections
author：felix
createdAt: 2022/7/29
version: 1.0.0
description:

Descriptor for collection
"""
from motor.motor_asyncio import AsyncIOMotorCollection
from .client import AioClient
from .exceptions import AioMongoMissParameter
import logging

logger = logging.getLogger(__name__)


class AioCollection:
    def __init__(self):
        pass

    def __get__(
        self,
        instance,
        owner
    ) -> AsyncIOMotorCollection:
        """
        Descriptor for mongodb collection
        if Document not init_db, no AioClient instance be created
        you can create AioClient instance here with the following parameters
        you can get db_url with attr "__db_url__" in document sub class,
        or use class method, Document.init_db(url=db_url)
        you can get db_name with attr "__db_name__" in document sub class
        you can get collection_name with attr "__collection_name__" in document sub class
        :param instance:
        :param owner:
        :return: motor aio collection
        """
        if instance is None:
            _aio_client = getattr(owner, '__aio_client__', None)
            _db_name = getattr(owner, '__db_name__', 'test')
            _collection_name = getattr(owner, '__collection_name__', (owner.__name__.lower() + 's'))

            if _aio_client is None:
                client_name = getattr(owner, '__client_name__', '__local__')
                db_url = getattr(owner, '__db_url__', None)

                if db_url is None:
                    raise AioMongoMissParameter('miss db_url, you can define in class with attr "__db_url__", '
                                                'or use method, Document.init_db(url=db_url)')
                logger.info(f' Document not init, here use db_url = "{db_url}" and db = "{_db_name}" ')
                _aio_client = AioClient(client_name=client_name, url=db_url, cache=True)

            return _aio_client[_db_name][_collection_name]
        else:
            return self
