"""
name: conftest
author：felix
createdAt: 2022/8/1
version: 1.0.0
description:

mongodb replication set
pytest --url mongodb://localhost:27000 -vs --cov --cov-report=html
"""

import asyncio
import pytest
from datetime import datetime
# import sys
# sys.path.append("..")
from aio_mongo_dm import Document


def pytest_addoption(parser):
    parser.addoption(
        "--url", action="store", default='mongodb://localhost:27000',
        help="mongo url"
    )


@pytest.fixture(scope='session')
def get_mongo_url(request):
    mongo_url = request.config.getoption("--url")
    print(f'Command line: pytest --url mongo_url, get mongo url is {mongo_url}, please check it,  ')
    return mongo_url


@pytest.fixture
def empty_document():
    class EmptyDocument(Document):
        pass

    return EmptyDocument


@pytest.fixture
def user_document():
    class User(Document):
        __schema__ = {
            'name': {'type': str, 'default': 'my_default_name', 'index': -1},
            'sex':  {'type': bool},
            'age':  {'type': int, 'default': 20, 'index': 1},
            'createdAt': {'type': datetime, 'index': -1},
            'updatedAt': {'type': datetime, 'index': -1}
        }

    return User


@pytest.fixture
def user_document_other():
    class User(Document):
        __db_name__ = 'mytest2'
        __schema__ = {
            'name': {'type': str, 'default': 'my_default_name', 'index': -1},
            'sex':  {'type': bool},
            'age':  {'type': int, 'default': 20, 'index': 1},
            'createdAt': {'type': datetime, 'index': -1},
            'updatedAt': {'type': datetime, 'index': -1}
        }

    return User


@pytest.fixture
def user_document_no_time():
    class User(Document):
        __schema__ = {
            'name': {'type': str, 'default': 'my_default_name'},
            'sex':  {'type': bool},
            'age':  {'type': int, 'default': 20}
        }

    return User


@pytest.fixture(scope='module')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
