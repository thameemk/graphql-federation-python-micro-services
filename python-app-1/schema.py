import graphene
from graphene_federation import build_schema


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="hello user")


schema = build_schema(query=Query)
