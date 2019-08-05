import inspect
import logging

import graphene

from .types import ErrorInterface
from .utils import snake_to_upper_camel_case


logger = logging.getLogger(name=__name__)


def decorate_foo_with_logging(foo, name):
    def decorated(*args, **kwargs):
        result = foo(*args, **kwargs)
        logger.info(f'{name}: {args}, {kwargs} -> {result}')
        return result

    return decorated


class LoggingMetaclass(type):

    def __init__(cls, name, bases, namespace):
        super(LoggingMetaclass, cls).__init__(name, bases, namespace)

        functions = [
            (name, method) for name, method in namespace.items() if isinstance(method, staticmethod)
        ]
        functions = inspect.getmembers(cls, predicate=inspect.isfunction)

        for method_name, method in functions:
            decorated_method = decorate_foo_with_logging(method, f'{cls.__name__}:{method_name}')
            setattr(cls, method_name, decorated_method)


def error_constructor(name):
    error_name = snake_to_upper_camel_case(name)
    error_meta_class = type('Meta', (), {
        'interfaces': (ErrorInterface,),
    })
    return type(error_name, (graphene.ObjectType, ), {
        'Meta': error_meta_class,
    })


class ErrorMetaclass(type):

    def __init__(cls, name, bases, namespace):
        super(ErrorMetaclass, cls).__init__(name, bases, namespace)

        assert hasattr(cls, 'errors'), f'errors field is required on {cls.__name__}'
        errors = cls.errors

        for error in errors:
            setattr(cls, error, error_constructor(error))
