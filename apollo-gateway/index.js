import {ApolloGateway} from "@apollo/gateway";

const gateway = new ApolloGateway({
    serviceList: [
        {name: 'App 2', url: 'http://127.0.0.1:8901/graphql'},
        {name: 'App 1', url: 'http://127.0.0.1:8900/graphql'}
    ],
    introspectionHeaders: {
        Authorization: 'Bearer abc123'
    }
});