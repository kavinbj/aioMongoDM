"""
name: example02_index
author：felix
createdAt: 2022/8/1
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
    # set DB name of this document
    __db_name__ = 'mytest'

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
    # init whole document/collection with mongodb url，with default db_name=test
    await Document.init_db(url=_db_url)

    # 1、create single index respectively according to User.__schema__ index value, e.g. name 1, createdAt -1
    single_index_results = await User.create_index()
    print('single_index_results', single_index_results)

    # 2、 create compound index
    compound_index_result = await User.create_compound_index([('name', 1), ('createdAt', -1)])
    print('compound_index_result', compound_index_result)

    # 3、 get all index information
    index_information = await User.get_index_infor()
    print('index_information', index_information)

    # 3、 drop all index information
    await User.get_collection().drop_indexes()
    print('drop_indexes')

    # get index_information
    index_information = await User.get_index_infor()
    print('after drop_indexes info',  index_information)

    print('read_preference', User.get_collection().read_preference)

if __name__ == '__main__':
    asyncio.run(main())
