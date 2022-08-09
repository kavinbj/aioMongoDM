"""
name: example06_transaction
author：felix
createdAt: 2022/8/1
version: 1.0.0
description:


transaction need replication set env, if not, will raise error.

"""
from bson.objectid import ObjectId
from datetime import datetime
import asyncio
# import sys
# sys.path.append("..")
from aio_mongo_dm import Document, AioClient


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


class PayOrder(Document):
    # customize class with schema data
    __schema__ = {
        'user_id':    {'type': ObjectId},
        'total_fee':  {'type': int},
        'status':     {'type': str, 'default': 'Normal'},
        'createdAt':  {'type': datetime, 'index': -1},
        'updatedAt':  {'type': datetime}
    }


async def trancation_test(is_raise_exception):
    client = AioClient(client_name='__local__')
    async with await client.start_session() as s:
        async with s.start_transaction():
            user = User()
            user.name = 'kavin'
            new_user = await user.save(session=s)

            pay_order = PayOrder()
            pay_order.user_id = user['_id']
            pay_order.total_fee = 100
            pay_order.status = 'payed'
            new_order = await pay_order.save(session=s)

            assert new_user['_id'] == new_order['user_id']
            if is_raise_exception:
                raise Exception('trancation_test exception')


async def main():
    # init whole document/collection with mongodb url and db_name
    await Document.init_db(url=_db_url, client_name='__local__', db_name='mytest')

    user_count1 = await User.count()
    new_order_count1 = await PayOrder.count()
    # successful transaction
    await trancation_test(False)

    user_count2 = await User.count()
    new_order_count2 = await PayOrder.count()
    # count +1
    assert user_count2 == user_count1 + 1
    assert new_order_count2 == new_order_count1 + 1

    try:
        # failed transaction
        await trancation_test(True)
    except Exception as e:
        assert str(e) == 'trancation_test exception'

    user_count3 = await User.count()
    new_order_count3 = await PayOrder.count()
    # count nor change
    assert user_count3 == user_count2
    assert new_order_count3 == new_order_count2

    print('trancation test ok.')


if __name__ == '__main__':
    asyncio.run(main())
