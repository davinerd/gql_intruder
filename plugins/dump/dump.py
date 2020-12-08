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

    def __get_connection_object_by_name(self, where, name):
        data = self.SCHEMA['data']['__schema']

        branch = data[where]
        for entry in branch:
            print(entry)
            if entry['name'] == name:
                print("goal")
                return entry
            print("="*10)

        return None

    def __analyze_query_type(self, jschema):
        result = {'name': 'queryType', 'results': list()}

        if jschema.get('queryType', None) is not None:
            result['results'].append(jschema['queryType'])

        return result

    def __get_of_type(self, obj):
        result = {'defaultValue': str(), 'returnType': str(), 'returnValue': str(), 'kindValue': str()}

        sub_type = obj.get('ofType', None)
        if sub_type is not None:
            if sub_type.get('ofType', None) is not None:
                result['kindValue'] = sub_type.get('ofType', None).get('kind')
                result['returnValue'] = sub_type.get('ofType', None).get('name')

        result['defaultValue'] = obj['kind']
        return result
    def __object_extract(self, obj):
        objs = list()
        print("Digging {}".format(obj['name']))
        result = {'args': list(), 'query_strings': list()}
        print(obj['fields'])
        if obj.get('fields', None) is None:
            print("No more fields pal")
            return result

        for field in obj['fields']:
            #if field['type']['kind'] != "OBJECT" or field['isDeprecated'] is True:
            if field['isDeprecated'] is True:
                continue
            
            args_query_string = ""
            function_entry = {'objName': field['name'], 'args': list()}
            print("FIELD NAME {}".format(field['name']))
            # We need to look for stuff in both field['args] and field['type]
            for arg in field['args']:
                arg_entry = dict()
                arg_entry['name'] = arg['name']
                arg_entry['type'] = arg['type']['name']
                arg_entry['defaultValue'] = arg['defaultValue']
                
                args_query_string = args_query_string + "{}:{}, ".format(arg_entry['name'], arg_entry['type'])
                if arg_entry['defaultValue'] is not None:
                    args_query_string = args_query_string + "<{}>, ".format(arg_entry['defaultValue'])
                function_entry['args'].append(arg_entry)

                if arg_entry['type'] == "OBJECT" or arg['type'].get('ofType', None) is not None:
                    of_type = self.__get_of_type(arg['type'])
                    if of_type['kindValue'] == "OBJECT":
                        conn_obj = self.__get_connection_object_by_name('types', of_type['returnValue'])
                        if conn_obj['kind'] == "OBJECT" and not conn_obj['name'].startswith("__"):
                            print("yep, digging it")
                            objs.append(self.__object_extract(conn_obj))

            result['args'].append(function_entry)
            query_string = "query {0} ( {1} )".format(field['name'], args_query_string.rstrip(', '))
            result['query_strings'].append(query_string)

            # let's parse field['type']
            print("ASDASDASd")
            print(field)
            print("Asdasdas")
            if field['type'].get('ofType', None) is not None:
                    of_type = self.__get_of_type(field['type'])
                    if of_type['kindValue'] == "OBJECT":
                        print("Looking for {}".format(field['type']['name']))
                        conn_obj = self.__get_connection_object_by_name('types', of_type['returnValue'])
                        if conn_obj['kind'] == "OBJECT" and not conn_obj['name'].startswith("__"):
                            print("yep, digging it")
                            objs.append(self.__object_extract(conn_obj))
            
            elif not field['type']['name'].startswith("__"):
                print("Looking for {}".format(field['type']['name']))
                conn_obj = self.__get_connection_object_by_name('types', field['type']['name'])
                if conn_obj is None:
                    print("WJAAAA NOOOOONEEE")
                else:
                    objs.append(self.__object_extract(conn_obj))

            objs.append(result)

        return objs

    def __analyze_types_query(self, entry):
        # TODO think about a data structure to improve readibiliy
        result = {'type': 'query', 'args': list(), 'query_strings': list()}

        obj = self.__get_connection_object_by_name('types', 'Query')
        print("Looking for {}".format(obj['name']))
        result['args'].append(self.__object_extract(obj))

        return result

    def __analyze_types(self, jschema):
        result = {'name': 'types', 'results': list()}

        types_schema = jschema.get('types', None)
        
        if types_schema is not None:
            for entry in types_schema:
                if entry['kind'] != "OBJECT":
                    continue
                
                # This should be results['data'][*]['QueryType']['name']
                if entry['name'] == "Query":
                    result['results'].append(self.__analyze_types_query(entry))
                    continue

        return result

    def attack(self):
        f = requests.post(self.GQL_ENDPOINT, headers=utils.set_request_headers(), json={"query": self.introspection_query})
        self.SCHEMA = f.json()
        #print(json.dumps(self.SCHEMA, indent=4, sort_keys=True))

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

        print(json.dumps(results, indent=4, sort_keys=True))
