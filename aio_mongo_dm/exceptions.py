"""
name: exceptions
author：felix
createdAt: 2022/7/26
version: 1.0.0
description:

"""


class AioMongoDMException(Exception):
    pass


class AioMongoDMSchemaError(AioMongoDMException):
    pass


class DocumentInitDataError(AioMongoDMException):
    pass


class AioMongoConnectError(AioMongoDMException):
    pass


class AioMongoMissParameter(AioMongoDMException):
    pass


class AioMongoAttributeError(AioMongoDMException):
    pass


class AioMongoDocumentDoesNotExist(AioMongoDMException):
    pass
