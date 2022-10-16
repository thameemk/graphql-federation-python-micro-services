import {ApolloServer} from '@apollo/server';
import {startStandaloneServer} from '@apollo/server/standalone';
import {ApolloGateway} from '@apollo/gateway';

// Initialize an ApolloGateway instance and pass it

const gateway = new ApolloGateway({
    serviceList: [
        {name: 'App 2', url: 'http://127.0.0.1:8901/graphql'},
        {name: 'App 1', url: 'http://127.0.0.1:8900/graphql'}
    ]
});

// Pass the ApolloGateway to the ApolloServer constructor

const server = new ApolloServer({
    gateway,
});


// Note the top-level `await`!
const {url} = await startStandaloneServer(server);
console.log(`🚀  Server ready at ${url}`);