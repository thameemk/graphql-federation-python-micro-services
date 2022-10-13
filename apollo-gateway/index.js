import {ApolloGateway} from "@apollo/gateway";
import {startStandaloneServer} from "@apollo/server/standalone";
import {ApolloServer} from "apollo-server";

const gateway = new ApolloGateway({
    serviceList: [
        {name: 'App 2', url: 'http://127.0.0.1:8901/graphql'},
        {name: 'App 1', url: 'http://127.0.0.1:8900/graphql'}
    ]
});


async function startApolloServer() {
  const server = new ApolloServer({ typeDefs, resolvers });
  const { url } = await startStandaloneServer(server, {
    context: async ({ req }) => ({ token: req.headers.token }),
    listen: { port: 4000 },
  });

  console.log(`🚀  Server ready at ${url}`);
}

startApolloServer()