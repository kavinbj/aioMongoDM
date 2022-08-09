"""
name: example01_base
author：felix
createdAt: 2022/7/26
version: 1.0.0
description:

"""
from datetime import datetime
import asyncio
# import sys
# sys.path.append("..")
from aio_mongo_dm import Document


_db_url = 'mongodb://localhost:27000'


class User(Document):
    # customize class with schema data
    __schema__ = {
        'name': {'type': str, 'default': 'my_default_name', 'index': 1},
        'age':  {'type': int, 'default': 20, 'index': -1},
        'sex':  {'type': bool, 'default': True},
        'createdAt': {'type': datetime, 'index': -1},
        'updatedAt': {'type': datetime}
    }

    # customize class method
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
    assert user.name == 'my_default_name'
    assert user.sex is True
    # _id not exist
    assert '_id' not in user

    count1 = await User.count({})
    print(f'User count1={count1}')

    # save user object to db， then return _id (mongodb's unique index )
    await user.save()
    # _id exist
    assert '_id' in user

    count2 = await User.count({})
    assert count2 == count1 + 1
    print(f'User count2={count2}')

    user_with_name = await User.find_one_by_name('my_default_name')
    print(user_with_name, user_with_name.updatedAt)
    assert isinstance(user_with_name, User)

if __name__ == '__main__':
    asyncio.run(main())
