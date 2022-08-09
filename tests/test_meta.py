"""
name: test_meta
author：felix
createdAt: 2022/8/3
version: 1.0.0
description:

"""
import pytest
from motor.motor_asyncio import AsyncIOMotorCollection
# import sys
# sys.path.append("..")
from aio_mongo_dm import exceptions, Document, AioCollection


class User(Document):
    __client_name__ = '__test_client__'
    __db_url__ = 'mongodb://localhostlocalhost:27017'
    __aio_client__ = None
    __db_name__ = 'mmtest'
    __collection_name__ = 'uusers'
    __schema__ = {
        'name': {'type': str, 'default': 'my_default_name'},
        'sex':  {'type': bool},
        'age':  {'type': int, 'default': 20}
    }


def test_collection_init_client():
    user = User()
    assert user.get_collection().name == 'uusers'
    assert user.get_collection().database.name == 'mmtest'
    assert isinstance(User.get_collection(), AsyncIOMotorCollection)
    assert isinstance(user.aio_collection, AioCollection)


def test_document_define_error_data():
    with pytest.raises(exceptions.AioMongoDMSchemaError) as e:
        class UserError(Document):
            __schema__ = {
                'name': 'str',
                'sex':  {'type': bool},
                'age':  {'type': int, 'default': 20}
                }
    exec_msg = e.value.args[0]
    assert e.type is exceptions.AioMongoDMSchemaError
    assert exec_msg == "field: 'name' has error definition."


def test_document_define_miss_para():
    with pytest.raises(exceptions.AioMongoMissParameter) as e:
        class UserError(Document):
            __client_name__ = '__test_client__'
            __db_url__ = None
            __aio_client__ = None
            __db_name__ = 'mmtest'
            __collection_name__ = 'uusers'
            __schema__ = {
                'name': {'type': str, 'default': 'my_default_name', 'index': -1},
                'sex':  {'type': bool},
                'age':  {'type': int, 'default': 20}
            }
        user = UserError()
        aio_collection = user.get_collection()
        assert isinstance(aio_collection, AioCollection)
    exec_msg = e.value.args[0]
    assert e.type is exceptions.AioMongoMissParameter
    assert exec_msg == 'miss db_url, you can define in class with attr "__db_url__", ' \
                       'or use method, Document.init_db(url=db_url)'


def test_document_define_not_type():
    with pytest.raises(exceptions.AioMongoDMSchemaError) as e:
        class UserNoType(Document):
            __schema__ = {
                'name': {'default': 'my_default_name', 'index': -1},
                'sex':  {'type': bool},
                'age':  {'type': int, 'default': 20}
            }
    exec_msg = e.value.args[0]
    assert e.type is exceptions.AioMongoDMSchemaError
    assert exec_msg == "field: 'name' not has 'type' definition."


def test_document_define_error_type():
    with pytest.raises(exceptions.AioMongoDMSchemaError) as e:
        class UserErrorType(Document):
            __schema__ = {
                'name': {'type': str, 'default': 30, 'index': -1},
                'sex':  {'type': bool},
                'age':  {'type': int, 'default': 20}
            }
    exec_msg = e.value.args[0]
    assert e.type is exceptions.AioMongoDMSchemaError
    assert exec_msg == "field: 'name' default value has error type."


def test_document_define_error_index():
    with pytest.raises(exceptions.AioMongoDMSchemaError) as e:
        class UserErrorIndex(Document):
            __schema__ = {
                'name': {'type': str, 'default': 'my_default_name', 'index': 5},
                'sex':  {'type': bool},
                'age':  {'type': int, 'default': 20}
            }
    exec_msg = e.value.args[0]
    assert e.type is exceptions.AioMongoDMSchemaError
    assert exec_msg == "field: 'name' index value not as [1, -1, '2d', '2dsphere', 'hashed', 'text']."


def test_document_define_error_key():
    with pytest.raises(exceptions.AioMongoDMSchemaError) as e:
        class UserErrorIndex(Document):
            __schema__ = {
                'name': {'type': str, 'default': 'my_default_name', 'index': -1, 'error_key': 'error_value'},
                'sex':  {'type': bool},
                'age':  {'type': int, 'default': 20}
            }
    exec_msg = e.value.args[0]
    assert e.type is exceptions.AioMongoDMSchemaError
    assert exec_msg == "field: 'name' has error definition key ['error_key']."
