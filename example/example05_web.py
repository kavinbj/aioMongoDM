"""
name: example05_web
author：felix
createdAt: 2022/8/1
version: 1.0.0
description:

"""
from sanic import Sanic, response
from datetime import datetime
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


app = Sanic(__name__)


@app.listener('after_server_start')
async def notify_server_started(_app: Sanic, _loop):
    print('notify_server_started, tap http://localhost:3000/pub in web browser')
    # When the asynchronous web framework （sanic） starts, a new loop will be generated.
    # so mongo client needs to be initialized here, and cache the mongo name
    await Document.init_db(url=_db_url, db_name='mytest', io_loop=_loop)


# test http://localhost:3000/pub in web browser
@app.route('/pub', methods=['GET'])
async def test1(request):

    count = await User.count({'name': 'kavin'})
    if count <= 0:
        print('no user named kavin')
        user = User()
        user.name = 'kavin'
        await user.save()
        return response.text('no user named kavin, create one')
    else:
        kavin_user = await User.find_one_by_name('kavin')
        if kavin_user is None:
            raise Exception('error')
        kavin_user.age += 1
        await kavin_user.save()
        return response.text(f'user kavin with age {kavin_user.age}')


if __name__ == '__main__':
    print('main')
    app.run(host="127.0.0.1", port=3000)
