"""
name: utils
author：felix
createdAt: 2022/7/29
version: 1.0.0
description:

"""
import inspect
from contextlib import suppress
from itertools import chain


def find_token(classes, token):
    def find(cls):
        targets = (vars(c).get(token) for c in cls.__mro__)
        return filter(None, targets)

    with suppress(StopIteration):
        return next(chain.from_iterable(map(find, classes)))


async def func_call(fn, *args, **kwargs):
    if inspect.iscoroutinefunction(fn) or inspect.isawaitable(fn):
        fn = await fn(*args, **kwargs)
    elif callable(fn):
        fn = fn(*args, **kwargs)
    return fn
