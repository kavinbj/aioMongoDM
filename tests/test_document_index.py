"""
name: test_create_index
author：felix
createdAt: 2022/8/2
version: 1.0.0
description:

"""
import pytest
from motor.motor_asyncio import AsyncIOMotorCollection
# import sys
# sys.path.append("..")
from aio_mongo_dm import Document


@pytest.mark.asyncio
async def test_clear_collection(get_mongo_url, event_loop):
    aio_client = await Document.init_db(url=get_mongo_url, db_name='mytest', io_loop=event_loop)

    mydb = aio_client['mytest']
    for collection in await mydb.list_collection_names():
        await mydb.drop_collection(collection)


@pytest.mark.asyncio
async def test_get_collection(user_document):
    user_collection = user_document.get_collection()

    assert isinstance(user_collection, AsyncIOMotorCollection)
    assert user_collection.name == 'users'
    assert user_collection.database.name == 'mytest'


@pytest.mark.asyncio
async def test_get_collection_db_name(user_document):
    user_collection = user_document.get_collection(db_name='mytest2')

    assert isinstance(user_collection, AsyncIOMotorCollection)
    assert user_collection.name == 'users'
    assert user_collection.database.name == 'mytest2'


@pytest.mark.asyncio
async def test_get_create_index(user_document):
    index_list = await user_document.create_index()
    assert index_list == ['name_-1', 'age_1', 'createdAt_-1', 'updatedAt_-1']


@pytest.mark.asyncio
async def test_get_create_index_no_index(user_document_no_time):
    index_list = await user_document_no_time.create_index()
    assert index_list == []


@pytest.mark.asyncio
async def test_get_create_compound_index(user_document):
    compound_index = await user_document.create_compound_index([('name', 1), ('createdAt', -1)])
    assert compound_index == 'name_1_createdAt_-1'


@pytest.mark.asyncio
async def test_get_index_information(user_document):
    # drop all index information
    await user_document.get_collection().drop_indexes()

    index_list = await user_document.create_index()
    assert index_list == ['name_-1', 'age_1', 'createdAt_-1', 'updatedAt_-1']

    compound_index = await user_document.create_compound_index([('name', 1), ('createdAt', -1)])
    assert compound_index == 'name_1_createdAt_-1'

    index_information = await user_document.get_index_infor()
    index_keys = list(index_information.keys())

    assert index_keys == ['_id_', 'name_-1', 'age_1', 'createdAt_-1', 'updatedAt_-1', 'name_1_createdAt_-1']
