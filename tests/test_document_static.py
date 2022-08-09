
"""
name: test_document_static
author：felix
createdAt: 2022/8/2
version: 1.0.0
description:

"""
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
# import sys
# sys.path.append("..")
from aio_mongo_dm import exceptions, Document


@pytest.mark.asyncio
async def test_document_clear_collection(get_mongo_url, event_loop):
    aio_client = await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)
    assert isinstance(aio_client, AsyncIOMotorClient)

    mydb = aio_client['mytest']
    for collection in await mydb.list_collection_names():
        await mydb.drop_collection(collection)


@pytest.mark.asyncio
async def test_document_create_instance(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    user = user_document.create_instance({'name': 'kavin', 'age': 30, 'sex': True})

    assert user.name == 'kavin'
    assert user.age == 30
    assert user.sex is True


@pytest.mark.asyncio
async def test_document_create_instance_error(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    user = user_document.create_instance(None)
    assert user is None

    user = user_document.create_instance(('name', 'kavin'))
    assert user is None


@pytest.mark.asyncio
async def test_document_find_by_id(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    user = user_document.create_instance({'name': 'kavin', 'age': 30, 'sex': True})
    await user.save()
    assert '_id' in user

    find_user = await user_document.find_by_id(user['_id'])

    assert find_user.name == user.name
    assert find_user.age == user.age
    assert find_user.sex == user.sex


@pytest.mark.asyncio
async def test_document_find_by_id_error(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    find_user = await user_document.find_by_id('')
    assert find_user is None

    with pytest.raises(exceptions.AioMongoDocumentDoesNotExist) as e:
        find_user = await user_document.find_by_id('error_id')
        assert isinstance(find_user, user_document)

    exec_msg = e.value.args[0]
    assert exec_msg == "'error_id' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string"


@pytest.mark.asyncio
async def test_document_delete_by_id(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    user = user_document.create_instance({'name': 'kavin', 'age': 30, 'sex': True})
    await user.save()
    assert '_id' in user

    delete_result = await user_document.delete_by_id(user['_id'])
    assert delete_result == 1


@pytest.mark.asyncio
async def test_document_delete_by_id_error(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    with pytest.raises(exceptions.AioMongoDocumentDoesNotExist) as e:
        delete_count = await user_document.delete_by_id('')
        assert delete_count == 1
    exec_msg = e.value.args[0]
    assert exec_msg == "oid is None"

    with pytest.raises(exceptions.AioMongoDocumentDoesNotExist) as e:
        delete_count = await user_document.delete_by_id('error_id')
        assert delete_count == 1
    exec_msg = e.value.args[0]
    assert exec_msg == "'error_id' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string"


@pytest.mark.asyncio
async def test_document_find(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    user1 = user_document.create_instance({'name': 'felix', 'age': 30, 'sex': True})
    await user1.save()

    user2 = user_document.create_instance({'name': 'felix', 'age': 20, 'sex': False})
    await user2.save()

    user3 = user_document.create_instance({'name': 'felix', 'age': 10, 'sex': True})
    await user3.save()

    cursor = user_document.find({'name': 'felix'}).sort('age', 1)
    documents = await cursor.to_list(length=100)
    assert len(documents) == 3


@pytest.mark.asyncio
async def test_document_find_one(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    find_user = await user_document.find_one({'name': 'felix'})
    assert '_id' in find_user
    assert isinstance(find_user, user_document)
    assert find_user.name == 'felix'


@pytest.mark.asyncio
async def test_document_count(get_mongo_url, event_loop, user_document):
    await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    count = await user_document.count({'name': 'felix'})
    assert count == 3
