"""
name: test_document_method
author：kavinbj
createdAt: 2021/8/2
version: 1.0.0
description:

"""
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
# import sys
# sys.path.append("..")
from aio_mongo_dm import exceptions, Document, ObjectId


@pytest.mark.asyncio
async def test_document_clear_collection(get_mongo_url, event_loop):
    aio_client = await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)
    assert isinstance(aio_client, AsyncIOMotorClient)

    mydb = aio_client['mytest']
    for collection in await mydb.list_collection_names():
        await mydb.drop_collection(collection)


@pytest.mark.asyncio
async def test_document_aio_client(get_mongo_url, event_loop):
    aio_client = await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)
    assert aio_client is Document.__aio_client__


@pytest.mark.asyncio
async def test_document_error_connect(event_loop):
    with pytest.raises(exceptions.AioMongoConnectError) as e:
        await Document.init_db(url='error_url', db_name='mytest', io_loop=event_loop, serverSelectionTimeoutMS=3)
    exec_msg = e.value.args[0]
    assert exec_msg == "mongodb connecting error."


@pytest.mark.asyncio
async def test_document_db_name(user_document, user_document_other):
    assert Document.__db_name__ == 'mytest'
    assert user_document.get_collection().database.name == 'mytest'
    assert user_document_other.get_collection().database.name == 'mytest2'


@pytest.mark.asyncio
async def test_document_save(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)
    user = user_document()
    user.name = 'kavin'
    assert '_id' not in user

    await user.save()
    assert '_id' in user

    instance_id = user['_id']
    assert isinstance(instance_id, ObjectId)

    user['name'] = 'felix'
    new_user = await user.save()

    assert isinstance(new_user, user_document)
    assert new_user['_id'] == instance_id


@pytest.mark.asyncio
async def test_document_save_time(user_document):
    user = user_document()
    await user.save()
    assert 'createdAt' in user
    assert 'updatedAt' in user


@pytest.mark.asyncio
async def test_document_save_no_time(user_document_no_time):
    user_no_time = user_document_no_time()
    await user_no_time.save()
    assert 'createdAt' not in user_no_time
    assert 'updatedAt' not in user_no_time


@pytest.mark.asyncio
async def test_document_delete(user_document):
    user = user_document()
    await user.save()
    assert '_id' in user

    await user.delete()
    assert '_id' not in user


@pytest.mark.asyncio
async def test_document_delete_exception(user_document):
    with pytest.raises(exceptions.AioMongoDocumentDoesNotExist) as e:
        user = user_document()
        await user.delete()

    exec_msg = e.value.args[0]
    assert exec_msg == "document not saved."


@pytest.mark.asyncio
async def test_document_refresh(user_document):
    user = user_document(name='kavin', age=30, sex=True)
    await user.save()

    user.name = 'felix'
    assert user['name'] == 'felix'

    await user.refresh()
    assert user['name'] == 'kavin'


@pytest.mark.asyncio
async def test_document_refresh_exception(user_document):
    with pytest.raises(exceptions.AioMongoDocumentDoesNotExist) as e:
        user = user_document(name='kavin', age=30, sex=True)
        await user.refresh()

    exec_msg = e.value.args[0]
    assert exec_msg == "document not exist."


@pytest.mark.asyncio
async def test_document_pre_save_hook():
    class User(Document):
        __schema__ = {
            'name': {'type': str, 'default': '', 'index': -1},
            'sex':  {'type': bool},
            'age':  {'type': int, 'default': 20}
        }

        async def pre_save(self):
            raise exceptions.AioMongoDMException('User pre_save hook method run.')

    with pytest.raises(exceptions.AioMongoDMException) as e:
        user = User()
        await user.save()
    exec_msg = e.value.args[0]
    assert exec_msg == "User pre_save hook method run."


@pytest.mark.asyncio
async def test_document_after_save_hook():
    class User(Document):
        __schema__ = {
            'name': {'type': str, 'default': '', 'index': -1},
            'sex':  {'type': bool},
            'age':  {'type': int, 'default': 20}
        }

        def after_save(self):
            raise exceptions.AioMongoDMException('User after_save hook method run.')

    with pytest.raises(exceptions.AioMongoDMException) as e:
        user = User()
        await user.save()
    exec_msg = e.value.args[0]
    assert exec_msg == "User after_save hook method run."
