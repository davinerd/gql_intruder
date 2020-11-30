import argparse
import json
import utils
import requests
from plugin import Plugin

class Dump(Plugin):
    introspection_query =  "query IntrospectionQuery{__schema{queryType{name}mutationType{name}subscriptionType{name}types{...FullType}directives{name description locations args{...InputValue}}}}fragment FullType on __Type{kind name description fields(includeDeprecated:true){name description args{...InputValue}type{...TypeRef}isDeprecated deprecationReason}inputFields{...InputValue}interfaces{...TypeRef}enumValues(includeDeprecated:true){name description isDeprecated deprecationReason}possibleTypes{...TypeRef}}fragment InputValue on __InputValue{name description type{...TypeRef}defaultValue}fragment TypeRef on __Type{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name}}}}}}}}"
    GQL_ENDPOINT = None
    CMD_NAME = "dump"
    ANALYZE = False
    SCHEMA = None

    author = "Davide Barbato"
    description = "Dump GraphQL schema via introspection."

    def __init__(self):
        dump_argparser = argparse.ArgumentParser()
        dump_argparser.add_argument("--analyze", default=False, action="store_true")
        dump_argparser = self.build_argparse(dump_argparser)
        args = dump_argparser.parse_args()

        self.ANALYZE = args.analyze
        self.GQL_ENDPOINT = utils.parse_url(args.url)
        if self.GQL_ENDPOINT is None:
            print("URL {} is not valid!".format(args.url))
            exit(1)

    def __analyze_query_type(self, jschema):
        result = {'name': 'queryType', 'results': list()}

        if jschema.get('queryType', None) is not None:
            result['results'].append(jschema['queryType'])

        return result

    def __analyze_types(self, jschema):
        result = {'name': 'types', 'results': list()}

        schema_types = jschema.get('types', None)
        if schema_types is not None:
            print(len(schema_types))
        
        return result

    def attack(self):
        f = requests.post(self.GQL_ENDPOINT, headers=utils.set_request_headers(), json={"query": self.introspection_query})
        self.SCHEMA = f.json()
        print(json.dumps(self.SCHEMA, indent=4, sort_keys=True))

        if self.ANALYZE:
            self.analyze()

    def analyze(self):
        results = {'data': list()}

        if self.SCHEMA.get('data', None) is None:
            print("Error: 'data' not found")
            return 1
        
        if self.SCHEMA['data'].get('__schema', None) is None:
            print("Error: '__schema' not found")
            return 1

        data = self.SCHEMA['data']['__schema']

        results['data'].append(self.__analyze_query_type(data))
        results['data'].append(self.__analyze_types(data))

        print(results)
