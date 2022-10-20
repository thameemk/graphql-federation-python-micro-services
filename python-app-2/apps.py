import falcon

from graphql_ import GraphQL

app = falcon.App()

app.add_route('/graphql', GraphQL())
