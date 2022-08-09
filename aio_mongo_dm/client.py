"""
name: client
author：felix
createdAt: 2022/7/26
version: 1.0.0
description:

meta class, based on motor
"""

import asyncio
from asyncio.unix_events import _UnixSelectorEventLoop
from motor.motor_asyncio import AsyncIOMotorClient


class AioClient:
    __clients = {}

    def __new__(
        cls,
        client_name: str = '__local__',
        url: str = None,
        cache: bool = True,
        io_loop: _UnixSelectorEventLoop = None,
        **kwargs
    ) -> AsyncIOMotorClient:
        """
        create motor client instance, cache with client_name
        :param client_name: cache name for motor client instance
        :param url: mongodb url
        :param cache: whether to use cache client instance
        :param io_loop: asyncio event loop
        :param kwargs:
        :return: AsyncIOMotorClient instance
        """

        if client_name in cls.__clients and cache:
            return cls.__clients[client_name]
        else:
            if io_loop is None:
                io_loop = asyncio.get_event_loop()
            client = AsyncIOMotorClient(url, io_loop=io_loop, **kwargs)
            cls.__clients[client_name] = client
            return client
