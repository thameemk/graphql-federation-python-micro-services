import json
from collections import OrderedDict
from contextlib import redirect_stdout
from os import devnull

import falcon

from schema import schema


class GraphQL:
    @staticmethod
    def on_post(req,resp):
        """Handles GraphQL POST requests.
                1. requests with ?query={query_string} parameters in url
                (this takes precedence over POST request bodies, will be used first)
                (can also be used in tandem with POST body)
                examples:
                  curl -H "Content-Type: application/json" \
                    -d "{}" \
                    -g "http://localhost:4004/graphql?query={hello}"
                  curl -g -H "Content-Type: application/graphql" \
                    -d 'query RollDice($dice: Int!, $sides: Int){rollDice(dice:$dice,sides:$sides)}' \
                    'http://localhost:4004/graphql?variables={"dice":5}'
                2. 'content-type: application/json' requests
                (this is the preferred method, used by graphiql)
                examples:
                  curl -H 'Content-Type: application/json' \
                    -d '{"query": "{hello}"}' \
                    "http://localhost:4004/graphql"
                  curl -H 'Content-Type: application/json' \
                    -d '{"query":"query RollDice($dice: Int!, $sides: Int){rollDice(dice:$dice,sides:$sides)}","variables":"{\"dice\": 8,\"sides\":9}","operationName":"RollDice"}' \
                    "http://localhost:4004/graphql"
                3. 'content-type: application/graphql' requests
                (request body is the query string; pass variables/operationName in url)
                example:
                  curl -H 'Content-Type: application/graphql' \
                    -d '{hello}' \
                    "http://localhost:4004/graphql"
                4. 'content-type: application/x-www-form-urlencoded' requests
                examples:
                  curl -d 'query={hello}' "http://localhost:4004/graphql"
                  curl "http://localhost:4004/graphql" \
                    --data-urlencode 'query=query RollDice($dice: Int!, $sides: Int) { rollDice(dice: $dice, sides: $sides)}' \
                    --data-urlencode 'variables={"dice": 5, "sides": 9}' \
                    --data-urlencode 'operationName=RollDice'
                """

        # parse url parameters in the request first
        if req.params and 'query' in req.params and req.params['query']:
            query = str(req.params['query'])
        else:
            query = None

        if 'variables' in req.params and req.params['variables']:
            try:
                variables = json.loads(str(req.params['variables']),
                                       object_pairs_hook=OrderedDict)
            except json.decoder.JSONDecodeError:
                resp.status = falcon.HTTP_400
                resp.body = json.dumps(
                    {"errors": [{"message": "Variables are invalid JSON."}]},
                    separators=(',', ':')
                )
                return
        else:
            variables = None

        if 'operationName' in req.params and req.params['operationName']:
            operation_name = str(req.params['operationName'])
        else:
            operation_name = None

        # Next, handle 'content-type: application/json' requests
        if req.content_type and 'application/json' in req.content_type:
            # error for requests with no content
            if req.content_length in (None, 0):
                resp.status = falcon.HTTP_400
                resp.body = json.dumps(
                    {"errors": [{"message": "POST body sent invalid JSON."}]},
                    separators=(',', ':')
                )
                return

            # read and decode request body
            raw_json = req.stream.read()
            try:
                req.context['post_data'] = json.loads(
                    raw_json.decode('utf-8'),
                    object_pairs_hook=OrderedDict
                )
            except json.decoder.JSONDecodeError:
                resp.status = falcon.HTTP_400
                resp.body = json.dumps(
                    {"errors": [{"message": "POST body sent invalid JSON."}]},
                    separators=(',', ':')
                )
                return

            # build the query string (Graph Query Language string)
            if (query is None and req.context['post_data'] and
                    'query' in req.context['post_data']):
                query = str(req.context['post_data']['query'])
            elif query is None:
                resp.status = falcon.HTTP_400
                resp.body = json.dumps(
                    {"errors": [{"message": "Must provide query string."}]},
                    separators=(',', ':')
                )
                return

            # build the variables string (JSON string of key/value pairs)
            if (variables is None and req.context['post_data'] and
                    'variables' in req.context['post_data'] and
                    req.context['post_data']['variables']):
                variables = str(req.context['post_data']['variables'])
                try:
                    json_str = str(req.context['post_data']['variables'])
                    variables = json.loads(json_str,
                                           object_pairs_hook=OrderedDict)
                except json.decoder.JSONDecodeError:
                    resp.status = falcon.HTTP_400
                    resp.body = json.dumps(
                        {"errors": [
                            {"message": "Variables are invalid JSON."}
                        ]},
                        separators=(',', ':')
                    )
                    return
            elif variables is None:
                variables = ""

            # build the operationName string (matches a query or mutation name)
            if (operation_name is None and
                    'operationName' in req.context['post_data'] and
                    req.context['post_data']['operationName']):
                operation_name = str(req.context['post_data']['operationName'])

        # Alternately, handle 'content-type: application/graphql' requests
        elif req.content_type and 'application/graphql' in req.content_type:
            # read and decode request body
            req.context['post_data'] = req.stream.read().decode('utf-8')

            # build the query string
            if query is None and req.context['post_data']:
                query = str(req.context['post_data'])

            elif query is None:
                resp.status = falcon.HTTP_400
                resp.body = json.dumps(
                    {"errors": [{"message": "Must provide query string."}]},
                    separators=(',', ':')
                )
                return

        # Skip application/x-www-form-urlencoded since they are automatically
        # included by setting req_options.auto_parse_form_urlencoded = True

        elif query is None:
            # this means that the content-type is wrong and there aren't any
            # query params in the url
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(
                {"errors": [{"message": "Must provide query string."}]},
                separators=(',', ':')
            )
            return

        # redirect stdout of schema.execute to /dev/null
        with open(devnull, 'w') as f:
            with redirect_stdout(f):
                # run the query
                if operation_name is None:
                    result = schema.execute(query, variable_values=variables)
                else:
                    result = schema.execute(query, variable_values=variables,
                                            operation_name=operation_name)

        # construct the response and return the result
        if result.data:
            data_ret = {'data': result.data}
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(data_ret, separators=(',', ':'))
            return
        elif result.errors:
            # NOTE: these errors don't include the optional 'locations' key
            err_msgs = [{'message': str(i)} for i in result.errors]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({'errors': err_msgs}, separators=(',', ':'))
            return
        else:
            # responses should always have either data or errors
            raise
