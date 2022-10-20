import graphene
from graphene_federation import build_schema


class Query(graphene.ObjectType):
    test_app_1 = graphene.String(default_value="response from python app 1")


schema = build_schema(query=Query)
