import graphene
from graphene_federation import build_schema


class Query(graphene.ObjectType):
    get_name = graphene.String(default_value="user")


schema = build_schema(query=Query)
