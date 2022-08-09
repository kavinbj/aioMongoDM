"""
name: example04_collection
author：kavinbj
createdAt: 2021/8/1
version: 1.0.0
description:

"""
from pymongo import ReadPreference
from datetime import datetime
import asyncio
# import sys
# sys.path.append("..")
from aio_mongo_dm import Document


_db_url = 'mongodb://localhost:27000'


class User(Document):
    __schema__ = {
        'name': {'type': str, 'default': 'my_default_name', 'index': 1},
        'age':  {'type': int, 'default': 20, 'index': -1},
        'sex':  {'type': bool, 'default': True},
        'createdAt': {'type': datetime, 'index': -1},
        'updatedAt': {'type': datetime}
    }

    @classmethod
    async def find_one_by_name(cls, user_name):
        return await cls.find_one({'name': user_name})

    # hook method, after user.save()
    async def after_save(self):
        print('after_save User hook method')


async def main():
    # init whole document/collection with mongodb url and db_name
    await Document.init_db(url=_db_url, db_name='mytest')

    # create User instance
    user = User()
    user.name = 'new_user_name'
    user.sex = False

    # save user object to db， then return _id (mongodb's unique index )
    new_user = await user.save()

    assert id(new_user) == id(user)

    # get collection instance, and you can use more methods which refer to
    # 'https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_collection.html'
    collection = user.get_collection()

    # e.g. with_options (read_preference)
    read_collection = collection.with_options(read_preference=ReadPreference.SECONDARY)

    print('collection.read_preference', collection.read_preference)
    print('read_collection.read_preference', read_collection.read_preference)


if __name__ == '__main__':
    asyncio.run(main())
