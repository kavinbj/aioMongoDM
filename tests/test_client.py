"""
name: test_client
author：kavinbj
createdAt: 2021/8/2
version: 1.0.0
description:

"""
import pytest
# import sys
# sys.path.append("..")
from aio_mongo_dm import AioClient


@pytest.mark.asyncio
async def test_aio_client(get_mongo_url, event_loop):
    aio_client = AioClient(client_name='__test_client__', url=get_mongo_url, cache=False, io_loop=event_loop)

    server_info = await aio_client.server_info()
    assert server_info is not None and isinstance(server_info, dict)

    aio_client_cache = AioClient(client_name='__test_client__', cache=True, io_loop=event_loop)
    assert aio_client is aio_client_cache


@pytest.mark.asyncio
async def test_aio_client_no_loop(get_mongo_url):
    aio_client = AioClient(client_name='__test_client__', url=get_mongo_url, cache=False)

    server_info = await aio_client.server_info()
    assert server_info is not None and isinstance(server_info, dict)
