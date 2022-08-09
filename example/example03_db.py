"""
name: example03_db
author：kavinbj
createdAt: 2021/8/1
version: 1.0.0
description:

"""
from datetime import datetime
import asyncio
# import sys
# sys.path.append("..")
from aio_mongo_dm import Document


_db_url = 'mongodb://localhost:27000'


class User1(Document):
    # set DB name of this document. If not set, the default value test is used
    __db_name__ = 'mytest'
    # set collection name of this document. If not set, the default value f'{class name}s' is used
    __collection_name__ = 'users'
    # set db url of this document. If not set, the default value 'mongodb://localhost:27017' is used
    __db_url__ = _db_url

    __schema__ = {
        'name': {'type': str, 'default': 'my_default_name', 'index': 1},
        'age':  {'type': int, 'default': 20, 'index': -1},
        'sex':  {'type': bool, 'default': True},
        'createdAt': {'type': datetime, 'index': -1},
        'updatedAt': {'type': datetime}
    }

    # hook method, after user.save()
    async def after_save(self):
        print('after_save User1 hook method')


class User2(Document):
    # set DB name of this document. If not set, the default value test is used
    __db_name__ = 'mytest2'
    # set collection name of this document. If not set, the default value f'{class name}s' is used
    __collection_name__ = 'users'
    # set db url of this document. If not set, the default value 'mongodb://localhost:27017' is used
    __db_url__ = _db_url

    __schema__ = {
        'name': {'type': str, 'default': 'my_default_name', 'index': 1},
        'sex':  {'type': bool, 'default': True},
        'createdAt': {'type': datetime, 'default': datetime.now(), 'index': -1},
        'updatedAt': {'type': datetime, 'default': datetime.now()}
    }

    # hook method, after user.save()
    async def after_save(self):
        print('after_save User2 hook method')


async def main():
    # init whole document/collection with mongodb url，with default db_name=test
    await Document.init_db(url=_db_url, db_name='test')

    user1 = User1()
    user1.name = 'u_name1'
    await user1.save()
    assert '_id' in user1
    print('User1 database name', User1.get_collection().database.name)
    print('User1 collection name', User1.get_collection().name)

    user2 = User2()
    user2.name = 'u_name1'
    await user2.save()
    assert '_id' in user2
    print('User2 database name', User2.get_collection().database.name)
    print('User2 collection name', User2.get_collection().name)

    # different database
    assert User1.get_collection().database.name != User2.get_collection().database.name

    # same collection name
    assert User1.get_collection().name == User2.get_collection().name

    # different collection
    assert User1.get_collection() != User2.get_collection()


if __name__ == '__main__':
    asyncio.run(main())
