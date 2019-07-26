import graphene


class Connection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(self, info):
        return self.length


class ErrorInterface(graphene.Interface):
    field = graphene.String(required=False, default_value=None)
    message = graphene.String(required=True)


class AuthenticationRequired(graphene.ObjectType):
    message = graphene.String(required=True, default_value='authentication_required')

    class Meta:
        interfaces = (ErrorInterface,)


class MutationPayload(graphene.ObjectType):
    ok = graphene.Boolean(required=True)
    errors = graphene.List(ErrorInterface, required=True)
    query = graphene.Field('main.schema.Query', required=True)

    def resolve_ok(self, info):
        return len(self.errors or []) == 0

    def resolve_errors(self, info):
        return self.errors or []

    def resolve_query(self, info):
        return {}


class MutationRootOptions(graphene.types.objecttype.ObjectTypeOptions):
    model = None
    has_permission = lambda obj, user: True


class MutationRoot(graphene.ObjectType):

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        model=None,
        interfaces=(),
        _meta=None,
        has_permission=None,
        **options
    ):
        if not _meta:
            _meta = MutationRootOptions(cls)
        _meta.model = model
        _meta.has_permission = has_permission or (lambda obj, user: True)
        super(MutationRoot, cls).__init_subclass_with_meta__(
            _meta=_meta, interfaces=interfaces, **options
        )

    @classmethod
    def resolve(cls, root, info, id=None):
        if cls._meta.model is None:
            return {}

        if id is None:
            return getattr(root, cls._meta.model.__name__, {})
        try:
            obj = cls._meta.model.objects.get(id=id)
            return obj if cls._meta.has_permission(obj, info.context.user) else None
        except cls._meta.model.DoesNotExist:
            return None

    @classmethod
    def Field(cls):
        return graphene.Field(cls, id=graphene.ID(required=False), resolver=cls.resolve)


class MutationException(Exception):
    def __init__(self, errors):
        super(MutationException, self).__init__(errors)
        self.errors = errors
