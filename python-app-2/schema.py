import graphene
from graphene_federation import build_schema


class Query(graphene.ObjectType):
    test_app_2 = graphene.String(default_value="response from python app 2")


schema = build_schema(query=Query)
