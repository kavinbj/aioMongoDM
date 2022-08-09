"""
name: test_collection
author：kavinbj
createdAt: 2021/8/2
version: 1.0.0
description:

"""
import pytest
# import sys
# sys.path.append("..")
from aio_mongo_dm import exceptions
from aio_mongo_dm.document import AbstractDocument


def test_document_no_attribute(empty_document):
    with pytest.raises(exceptions.AioMongoAttributeError) as e:
        empty = empty_document()
        empty.test = 'test'
    exec_msg = e.value.args[0]
    assert e.type is exceptions.AioMongoAttributeError
    assert exec_msg == "'EmptyDocument' object has no attribute 'test' definition."


def test_document_not_correct_type(user_document):
    with pytest.raises(exceptions.AioMongoAttributeError) as e:
        user = user_document()
        user.name = 2
    exec_msg = e.value.args[0]
    assert e.type is exceptions.AioMongoAttributeError
    assert exec_msg == "in 'User', 'name' has not correct type <class 'str'>."


def test_document_getattr(user_document):
    user = user_document()
    assert user.name == 'my_default_name'


def test_document_setattr(user_document):
    user = user_document()
    user.name = 'kavin'
    assert user.name == 'kavin'


def test_document_delattr(user_document):
    user = user_document()
    del user.name
    assert 'name' not in user


def test_document_getattr_nodata(user_document):
    with pytest.raises(exceptions.AioMongoAttributeError) as e:
        user = user_document()
        print(user.sex)
    exec_msg = e.value.args[0]
    assert exec_msg == "'User' object has no attribute 'sex'"


def test_document_delattr_no_data(user_document):
    with pytest.raises(exceptions.AioMongoAttributeError) as e:
        user = user_document()
        del user.nokey
    exec_msg = e.value.args[0]
    assert exec_msg == "'User' object has no attribute 'nokey'"


def test_document_get_item(user_document):
    user = user_document()
    assert user['name'] == 'my_default_name'


def test_document_set_item(user_document):
    user = user_document()
    user['name'] = 'kavin'
    assert user['name'] == 'kavin'


def test_document_del_item(user_document):
    user = user_document()
    del user['name']
    assert 'name' not in user


def test_document_get_item_nodata(user_document):
    with pytest.raises(KeyError) as e:
        user = user_document()
        print(user['sex'])
    exec_msg = e.value.args[0]
    assert exec_msg == 'sex'


def test_document_del_item_no_data(user_document):
    with pytest.raises(KeyError) as e:
        user = user_document()
        del user['nokey']
    exec_msg = e.value.args[0]
    assert exec_msg == 'nokey'


def test_document_init(user_document):
    user = user_document(name='kavin', age=30, sex=True)
    assert user.name == 'kavin'
    assert user.age == 30
    assert user.sex is True


def test_document_init_error_key(user_document):
    with pytest.raises(exceptions.AioMongoAttributeError) as e:
        user = user_document(error_key='kavin', age=30, sex=True)
        assert isinstance(user, user_document)
    exec_msg = e.value.args[0]
    assert exec_msg == "'User' object has no attribute 'error_key' definition."


def test_document_init_error_type(user_document):
    with pytest.raises(exceptions.AioMongoAttributeError) as e:
        user = user_document(name=30, age=30, sex=True)
        assert isinstance(user, user_document)
    exec_msg = e.value.args[0]
    assert exec_msg == "in 'User', 'name' has not correct type <class 'str'>."


def test_document_iter(user_document):
    user = user_document(name='kavin', age=30, sex=True)

    assert list(user) == ['name', 'age', 'sex']


def test_document_eq(user_document):
    user1 = user_document(name='kavin', age=30, sex=True)
    user2 = user_document(name='kavin', age=30, sex=True)

    assert user1 == user2
    assert user1 is not user2


def test_document_not_eq(user_document):
    user1 = user_document(name='kavin', age=30, sex=True)
    user2 = user_document(name='felix', age=20, sex=False)

    assert user1 != user2
    assert user1 is not user2


def test_document_eq_error_type(user_document, empty_document):
    user1 = user_document(name='kavin', age=30, sex=True)
    user2 = empty_document()

    assert user1 != user2
    assert user1 is not user2


def test_document_repr(user_document):
    user = user_document(name='kavin', age=30, sex=True)

    assert str(user) == "<User({'age': 30, 'name': 'kavin', 'sex': True})>"


def test_document_contains(user_document):
    user = user_document(name='kavin', age=30, sex=True)

    assert 'name' in user
    assert 'test_test' not in user


def test_document_len(user_document):
    user = user_document(name='kavin', age=30, sex=True)

    assert len(user) == 3


def test_document_id(user_document):
    user = user_document()
    assert '_id' not in user

    user['_id'] = 'fake_id'
    assert '_id' in user


def test_absdocument():
    doc = AbstractDocument()
    doc2 = AbstractDocument()
    assert '__getattr__' in vars(AbstractDocument)
    assert '__setattr__' in vars(AbstractDocument)
    assert '__delattr__' in vars(AbstractDocument)
    assert '__contains__' in vars(AbstractDocument)
    assert '__iter__' in vars(AbstractDocument)
    assert '__iter__' in vars(AbstractDocument)
    assert '__getitem__' in vars(AbstractDocument)
    assert '__setitem__' in vars(AbstractDocument)
    assert '__delitem__' in vars(AbstractDocument)
    assert '__len__' in vars(AbstractDocument)

    doc.test = 'test_value'
    del doc.test
    assert doc.test is None
    assert 'test_value' not in doc

    doc['test'] = 'test_value'
    del doc['test']
    assert doc['test'] is None
    assert len(doc) == 0

    assert doc != doc2
    assert list(doc) == []
