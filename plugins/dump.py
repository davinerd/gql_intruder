import argparse
import json
import utils
import requests

class Dump:
    introspection_query =  "query IntrospectionQuery{__schema{queryType{name}mutationType{name}subscriptionType{name}types{...FullType}directives{name description locations args{...InputValue}}}}fragment FullType on __Type{kind name description fields(includeDeprecated:true){name description args{...InputValue}type{...TypeRef}isDeprecated deprecationReason}inputFields{...InputValue}interfaces{...TypeRef}enumValues(includeDeprecated:true){name description isDeprecated deprecationReason}possibleTypes{...TypeRef}}fragment InputValue on __InputValue{name description type{...TypeRef}defaultValue}fragment TypeRef on __Type{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name}}}}}}}}"
    GQL_ENDPOINT = None
    CMD_NAME = "dump"

    def __init__(self):
        dump_argparser = argparse.ArgumentParser()
        dump_argparser.add_argument("--url", required=True)
        args = dump_argparser.parse_args()
        self.GQL_ENDPOINT = utils.parse_url(args.url)
        if self.GQL_ENDPOINT is None:
            print("URL {} is not valid!".format(args.url))
            exit(1)
    
    def attack(self):
        f = requests.post(self.GQL_ENDPOINT, headers=utils.set_request_headers(), json={"query": self.introspection_query})
        print(json.dumps(f.json(), indent=4, sort_keys=True))
