# aio-mongo-dm
asynchronous lightweight ODM for MongoDB based on [motor](https://github.com/mongodb/motor)


# Suitable Application Environment
The goal of this package is to create an asynchronous, simple and intuitive ODM, which can be easily applied to the python asynchronous framework system.
If you happen to like asynchronous framework very much and use mongodb as your data storage system.
* [Motor documentation][https://motor.readthedocs.io/en/stable/index.html]

# Installation
```bash
pip install aio-mongo-dm
```

## Quick Start ##
```python
import asyncio
from datetime import datetime
from aio_mongo_dm import Document

class User(Document):
    # customize document field with schema data
    __schema__ = {
        'name': {'type': str, 'default': 'my_default_name', 'index': 1},
        'age':  {'type': int, 'default': 20, 'index': -1},
        'sex':  {'type': bool, 'default': True},
        'createdAt': {'type': datetime, 'index': -1},
        'updatedAt': {'type': datetime }
    }

    # customize class method
    @classmethod
    async def find_one_by_name(cls, user_name):
        return await cls.find_one({'name': user_name})

    # hook method, after user.save()
    async def after_save(self):
        print('after_save User hook method')
    
_db_url = 'mongodb://localhost:27000'
    
async def main():
    # init whole document/collection with mongodb url and db_name
    await Document.init_db(url=_db_url, db_name='mytest')

    # create User instance
    user = User()
    assert user.name == 'my_default_name'
    assert user.sex is True
    # _id not exist
    assert '_id' not in user

    count1 = await User.count({'age': {'$lg': 10}})

    # save user object to db， then return _id (mongodb's unique index )
    await user.save()
    # _id exist
    assert '_id' in user

    count2 = await User.count({})
    assert count2 == count1 + 1
    print(f'User count={count2}')

    user_with_name = await User.find_one_by_name('my_default_name')
    print(user_with_name, user_with_name.updatedAt)
    assert isinstance(user_with_name, User)
    
    cursor = User.find({'age': {'$gt': 10}}).sort('age')
    for document in await cursor.to_list(length=100):
        print(document)

if __name__ == '__main__':
    asyncio.run(main())

```

## Create Index ##
```python
import asyncio
from datetime import datetime
from aio_mongo_dm import Document

class User(Document):
    # set DB name of this document
    __db_name__ = 'mytest'
    
    # customize class with schema data
    __schema__ = {
        'name': {'type': str, 'default': 'my_default_name', 'index': 1},
        'age':  {'type': int, 'default': 20, 'index': -1},
        'sex':  {'type': bool, 'default': True},
        'createdAt': {'type': datetime, 'index': -1},
        'updatedAt': {'type': datetime }
    }

    # customize class method
    @classmethod
    async def find_one_by_name(cls, user_name):
        return await cls.find_one({'name': user_name})

    # hook method, after user.save()
    async def after_save(self):
        print('after_save User hook method')
    
_db_url = 'mongodb://localhost:27000'

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

if __name__ == '__main__':
    asyncio.run(main())

```

## Transcation ##  
**Notice: transaction need replication set env, e.g. one Primary Server, one Secondary Server, one Arbiter Server. [Detail Configuration][https://www.mongodb.com/docs/v5.0/reference/configuration-options/]**
```python
from bson.objectid import ObjectId
from datetime import datetime
import asyncio
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
```
## More Example ##
For more examples, please query the example folder.


# API Reference
### Document ###
* #### `__db_url__` ####
    set db url of this document. you can set in sub-class Document or use Document class method init_db(url='mongodb://localhost:27017')
    * `default`: 'mongodb://localhost:27017'
    
* #### `__db_name__` ####
    __optional__. Attribute for setting up the database. you can set in sub-class Document or use Document class method init_db(db_name='mytest')
    * `default`: 'test'

* #### `__collection_name__` ####
    __optional__. Attribute for setting up the collection name. e.g. the class name is 'User', so default collection name is 'users' if not set.
    * `default`:  '{class name}.lower() + s' 


* #### `__schema__` ####
     Set the initializing data for all objects in the collection when the object is initialized. Defined field default value and type will be checked .

* #### `save(session=None)` ####
    __Coroutine__. It saves the object in the database, attribute '_id' will be generated if success
    * `session`:  ClientSession instance for transaction operation
   
* #### `delete()` ####
    __Coroutine__. It remove an object from the database. If the object does not exist in the database, 
    then the __AioMongoDocumentDoesNotExist__ exception will be raised.

* #### `refresh(session=None)` ####
    __Coroutine__. Refresh the current object from the same object from the database. 
    If the object does not exist in the database, then the __AioMongoDocumentDoesNotExist__ exception will be raised.
    * `session`:  ClientSession instance for transaction operation

* #### `pre_save()` ####
    __Hook Method__. This method is called before the save() method. You can override this method in a subclass. 
    If this method is not overridden, 'updatedAt' and 'createdAt' will be updated with datetime.now() by default if the field key defined in __schema__.

* #### `after_save()` ####
    __Hook Method__. This method is called after the save() method. You can override this method in a subclass.

* #### `init_db(url: str = None, db_name: str = 'test', client_name: str = '__local__', io_loop: _UnixSelectorEventLoop = None, **kwargs) -> AioClient` ####
    __Coroutine Class Method__. init mongodb method, create AioClient instance and set class attribute __aio_client__
    * `url`:  mongodb url
    * `db_name`:  database name
    * `client_name`:  name for cache aio client
    * `io_loop`:  asyncio event loop
    ```python
    await Document.init_db(url='mongodb://localhost:27000', db_name='mytest')
    ```   

* #### `create_instance(obj: object) -> Optional[_Document]` ####
    __Class Method__. Create a document instance through an object, e.g.  User.create_instance({'name': 'kavin', 'age': 30})
    * `obj`:  an object instance
    
    
* #### `find_by_id(oid: Union[str, ObjectId], session=None) -> Optional[_Document]` ####
    __Coroutine Class Method__. document query based on document ID. e.g. User.find_by_id('xxxxxxx') 
    * `oid`:  Document ID, str or ObjectId
    * `session`:  ClientSession instance for transaction operation
    
* #### `delete_by_id(oid: Union[str, ObjectId], session=None)` ####
    __Coroutine Class Method__. delete document instance according to document ID. e.g. User.delete_by_id('xxxxxxx') 
    * `oid`:  Document ID, str or ObjectId
    * `session`:  ClientSession instance for transaction operation

* #### `find(*args, session: Optional[ClientSession] = None,**kwargs) -> AsyncIOMotorCursor` ####
    __Class Method__. Querying for More Than One Document, create a AsyncIOMotorCursor. 
    ```python
    cursor = User.find({'age': {'$gt': 10}}).sort('age')
    for document in await cursor.to_list(length=100):
        print(document)
    ```
    
* #### `find_one(*args, session: Optional[ClientSession] = None, **kwargs) -> Optional[_Document]` ####
    __Coroutine Class Method__. Getting a Single Document, return None if no matching document is found.
    ```python
    doc = await User.find_one({'age': {'$gt': 10}}).sort('age')
    ```

* #### `count(*filters: Mapping[str, Any], session: Optional[ClientSession] = None, **kwargs) -> int` ####
    __Coroutine Class Method__. Count the number of documents in this collection.
    * `filters`:  A query document that selects which documents to count in the collection.
    * `session`:  ClientSession instance for transaction operation
    ```python
    users_num = await User.count()
    users_name_num = await User.count({'name': 'kavin'})
    users_age_num = await User.count({'age': {$gt: 30}}})
    ```

* #### `get_collection(db_name: str = None) -> AioCollection` ####
    __Class Method__. get aio collection through the specified db name, if db_name is not None. 
    use attribute __db_name__  if db_name is None.
    * `db_name`:  database name 

* #### `create_index(session: Optional[ClientSession] = None) -> list` ####
    __Coroutine Class Method__. create index on this collection. When defining document subclasses, index can be defined in schema，
        In this function, we will create all the previously defined default indexes one by one
        return index str list
    * `session`:  ClientSession instance for transaction operation
    ```python
    class User(Document):
        __schema__ = {
           'name': {'type': str, 'default': 'my_default_name', 'index': -1},
           'sex':  {'type': bool},
           'age':  {'type': int, 'default': 20, 'index': 1},
           'createdAt': {'type': datetime, 'index': -1},
           'updatedAt': {'type': datetime}
        }
    res = await User.create_index()
    assert res == ['index_-1', 'age_1', 'createdAt_-1']
    ```

* #### `create_compound_index(keys: Union[str, Sequence[Tuple[str, Union[int, str, Mapping[str, Any]]]]], session: Optional[ClientSession] = None) -> str` ####
    __Coroutine Class Method__. create compound index on this collection.
    * `keys`:  list of index key and index value
    * `session`:  ClientSession instance for transaction operation
    ```python
    class User(Document):
        __schema__ = {
           'name': {'type': str, 'default': 'my_default_name', 'index': -1},
           'sex':  {'type': bool},
           'age':  {'type': int, 'default': 20, 'index': 1},
           'createdAt': {'type': datetime, 'index': -1},
           'updatedAt': {'type': datetime}
        }
    keys = [('name', 1), ('createdAt', -1)]
    res = await User.create_compound_index(keys)
    assert res == 'name_1_createdAt_-1'
    ```    
    
* #### `get_index_infor(session: Optional[ClientSession] = None) -> str` ####
    __Coroutine Class Method__. Get information on this collection’s indexes.
    * `session`:  ClientSession instance for transaction operation


