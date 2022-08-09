"""
name: __init__
author：kavinbj
createdAt: 2022/7/26
version: 1.0.0
description:

"""
import logging
from .document import Document
from .client import AioClient
from .collections import AioCollection
from bson.objectid import ObjectId

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = '1.1.0'
__author__ = 'kavinbj'
__credits__ = 'felix Williams'

__all__ = [
    'Document',
    'AioClient',
    'AioCollection',
    'ObjectId'
]
