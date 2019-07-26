import graphene

from .types import ErrorInterface, AuthenticationRequired, MutationException
from .utils import decapitalize


AUTHENTICATION_REQUIRED_CHECK = (
    AuthenticationRequired,
    lambda root, info, *args, **kwargs: not info.context.user.is_authenticated,
)

MUTATION_ROOT_SUFFIX = 'MutationRoot'


def create_default_create_function(model, include_user, user_field_name):
    def default_create_function(user=None, **data):
        if include_user:
            return model._default_manager.create(**data, **{user_field_name: user})
        else:
            return model._default_manager.create(**data)

    return default_create_function


def default_update_function(instance, user=None, **data):
    instance.__dict__.update(data)
    instance.save()
    return instance


def default_delete_function(instance, user=None):
    instance.delete()


def perform_checks(_checks, *mutation_args, **mutation_kwargs):
    errors = set()
    try:
        for error_class, checker in _checks:
            try:
                if checker(*mutation_args, **mutation_kwargs):
                    errors.add(error_class())
            except Exception as e:
                print(e)
    except (TypeError, ValueError, ):
        assert False, 'Checks must be an iterable of tuples (error_class, checker)'

    return errors


def get_mutation_errors(_cls, _meta, *mutation_args, **mutation_kwargs):
    errors = set()

    checks = _meta.checks
    errors |= perform_checks(checks, *mutation_args, **mutation_kwargs)
    return errors


def decorate_mutate_func(mutate_func, pre_mutate, cls, meta):
    def decorated_mutate(*args, **kwargs):
        root = args[0]
        if meta.root_required and not root:
            return None
            
        pre_mutate(*args, **kwargs)

        errors = get_mutation_errors(cls, meta, *args, **kwargs)
        if len(errors) == 0:
            try:
                return mutate_func(*args, **kwargs)
            except MutationException as e:
                return cls(errors=e.errors)

        return cls(errors=errors)

    return decorated_mutate


def get_possible_errors(checks):
    try:
        return list({error_class for error_class, checker in checks})
    except (TypeError, ValueError, ):
        assert False, 'Checks must be an iterable of tuples (error_class, checker)'
    return []


def create_meta_for_error_union(error_classes):
    return type('Meta', (), {
        'types': error_classes or [ErrorInterface, ],
    })


def create_error_union(cls, checks):
    error_classes = get_possible_errors(checks)
    name = get_error_union_name(cls)
    return type(name, (graphene.Union, ), {'Meta': create_meta_for_error_union(error_classes)})


def get_error_union_name(cls):
    return '{}Errors'.format(cls.__name__)


def define_mutation_errors(cls, checks):
    if len(checks) == 0:
        return
    cls.errors = graphene.List(create_error_union(cls, checks))


def get__default_root_name(root):
    if isinstance(root, str):
        root_class_name = root.split('.')[-1]
    else:
        root_class_name = root.__name__

    return decapitalize(root_class_name[:-len(MUTATION_ROOT_SUFFIX)])


def define_root(cls, root, root_name=None):
    root_name = None or get__default_root_name(root)
    setattr(cls, root_name, graphene.Field(root, default_value={}))
