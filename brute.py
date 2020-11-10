from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
import json
import argparse
import pathlib
import os
import sys
from urllib.parse import urlparse
from time import time

class ElapsedFuturesSession(FuturesSession):

    def request(self, method, url, hooks=None, *args, **kwargs):
        start = time()
        if hooks is None:
            hooks = {}

        def timing(r, *args, **kwargs):
            r.elapsed = time() - start
        
        try:
            if isinstance(hooks['response'], (list, tuple)):
                # needs to be first so we don't time other hooks execution
                hooks['response'].insert(0, timing)
            else:
                hooks['response'] = [timing, hooks['response']]
        except KeyError:
            hooks['response'] = timing

        return super(ElapsedFuturesSession, self).request(method, url, hooks=hooks, *args, **kwargs)

MAX_WORKERS = 5
ROOT_PAYLOAD_FOLDER = "{}/payloads".format(pathlib.Path().absolute())

PAYLOADS_FOLDER = {
    'sqli': "{}/sqli/".format(ROOT_PAYLOAD_FOLDER),
    'xss': "{}/xss/".format(ROOT_PAYLOAD_FOLDER)
}

main_parser = argparse.ArgumentParser(add_help=False)
main_parser.add_argument("--url", required=True)
main_parser.add_argument("--max-threads", type=int)

attack_argparser = argparse.ArgumentParser()
attack_argparser.add_argument("--key", required=True)
attack_argparser.add_argument("--schema", required=True)
attack_argparser.add_argument("--attack", required=True, type=str, choices=list(PAYLOADS_FOLDER.keys()))
attack_argparser.add_argument("--type", type=str)

dump_argparser = argparse.ArgumentParser()

introspection_query =  "query IntrospectionQuery{__schema{queryType{name}mutationType{name}subscriptionType{name}types{...FullType}directives{name description locations args{...InputValue}}}}fragment FullType on __Type{kind name description fields(includeDeprecated:true){name description args{...InputValue}type{...TypeRef}isDeprecated deprecationReason}inputFields{...InputValue}interfaces{...TypeRef}enumValues(includeDeprecated:true){name description isDeprecated deprecationReason}possibleTypes{...TypeRef}}fragment InputValue on __InputValue{name description type{...TypeRef}defaultValue}fragment TypeRef on __Type{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name}}}}}}}}"
headers = {
    'Content-Type': 'application/json'
}

def build_argparse(parse_to_add):
    return argparse.ArgumentParser(parents=[main_parser, parse_to_add], add_help=False)

# Kudos to this individual: https://stackoverflow.com/a/835527
# We want to go easy on this though...
def parse_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.netloc and not parsed_url.scheme:
        return None

    return "{}://{}{}".format(parsed_url.scheme, parsed_url.netloc, parsed_url.path)

def attack():
    schema = None
    futures = list()
    payloads = list()

    if not os.path.isfile(args.schema):
        print("Schema file {} not found!".format(args.schema))
        return False

    with open(args.schema, 'r') as f:
        schema = json.load(f)

    key_found = find_key(schema, args.key)
    if len(key_found) == 0:
        print("Key {} not found!".format(args.key))
        return False

    path = PAYLOADS_FOLDER[args.attack]
    if args.type:
        path = "{}/{}.txt".format(PAYLOADS_FOLDER[args.attack], args.type)

    if os.path.isdir(path):
        with os.scandir(path) as files:
            for item in files:
                with open(item, 'r') as sqlfile:
                    payloads.extend(sqlfile.readlines())
    else:
        if not os.path.isfile(path):
            print("File {} not found!".format(path))
            return False
        with open(path, 'r') as sqlfile:
            payloads = sqlfile.readlines()

    # create futures
    for payload in payloads:
        edit_value(schema, args.key, payload.rstrip())
        future = session.post(GQL_ENDPOINT,  headers=headers, json=schema)
        # payloads containing brackets or other chars may be escaped in schema and so 
        # this way I can check for real what payload has been sent
        # TODO escape chars so they made it into json
        future.payload = find_key(schema, args.key)[0]
        futures.append(future)

    # attack!
    for future in as_completed(futures):
        response = future.result()
        print("Tested: {}".format(future.payload))
        print("Status: {}".format(response.status_code))
        print("{}".format(response.text))
        print("Elapsed: {}s".format(response.elapsed))
        print("="*10)

def dump():
    f = session.post(GQL_ENDPOINT, headers=headers, json={"query": introspection_query})
    re = f.result()
    print(json.dumps(re.json(), indent=4, sort_keys=True))

def find_key(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values

def edit_value(obj, key, value):

    def extract(obj, key, value):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, key, value)
                elif k == key:
                   obj[k] = value
                   return True
        elif isinstance(obj, list):
            for item in obj:
                extract(item, key, value)
        return None

    values = extract(obj, key, value)
    return values


VALID_COMMANDS = {
    'attack': {
        'func': attack,
        'args': attack_argparser
    },
    'dump': {
        'func': dump,
        'args': dump_argparser
    }
}

action = sys.argv[1]
del sys.argv[1]

if action not in list(VALID_COMMANDS.keys()):
    print("Action not supported")
    exit(1)

parser = build_argparse(VALID_COMMANDS[action]['args'])

args = parser.parse_args()

threads = args.max_threads if args.max_threads else MAX_WORKERS
session = ElapsedFuturesSession(max_workers=threads)

GQL_ENDPOINT = parse_url(args.url)
if GQL_ENDPOINT is None:
    print("URL {} is not valid!".format(args.url))
    exit(1)

if not VALID_COMMANDS[action]['func']():
    exit(1)

exit()