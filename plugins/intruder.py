import pathlib
import os
import utils
import json
from time import time
import argparse
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession



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



class Intruder:
    ROOT_PAYLOAD_FOLDER = "{}/payloads".format(pathlib.Path().absolute())

    PAYLOADS_FOLDER = {
        'sqli': "{}/sqli/".format(ROOT_PAYLOAD_FOLDER),
        'xss': "{}/xss/".format(ROOT_PAYLOAD_FOLDER)
    }

    CMD_NAME = "attack"

    ENDPOINT = None
    SCHEMA = None
    KEY = None
    TYPE = None
    ATTACK = None
    THREADS = 5


    def __init__(self):
        extra_argparser = argparse.ArgumentParser()
        extra_argparser.add_argument("--url", required=True)
        extra_argparser.add_argument("--max-threads", type=int)
        extra_argparser.add_argument("--key", required=True)
        extra_argparser.add_argument("--schema", required=True)
        extra_argparser.add_argument("--attack", required=True, type=str, choices=list(self.PAYLOADS_FOLDER.keys()))
        extra_argparser.add_argument("--type", type=str)

        args = extra_argparser.parse_args()
        self.GQL_ENDPOINT = utils.parse_url(args.url)
        if self.GQL_ENDPOINT is None:
            print("URL {} is not valid!".format(args.url))
            exit(1)
        self.SCHEMA = args.schema
        self.KEY = args.key
        self.TYPE = args.type
        self.ATTACK = args.attack
        self.THREADS = args.max_threads if args.max_threads else self.THREADS

    def attack(self):
        schema = None
        futures = list()
        payloads = list()
        session = ElapsedFuturesSession(max_workers=self.THREADS)

        if not os.path.isfile(self.SCHEMA):
            print("Schema file {} not found!".format(self.SCHEMA))
            return False

        with open(self.SCHEMA, 'r') as f:
            schema = json.load(f)

        key_found = utils.find_key(schema, self.KEY)
        if len(key_found) == 0:
            print("Key {} not found!".format(self.KEY))
            return False

        path = self.PAYLOADS_FOLDER[self.ATTACK]
        if self.TYPE:
            path = "{}/{}.txt".format(self.PAYLOADS_FOLDER[self.ATTACK], self.TYPE)

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
            utils.edit_value(schema, self.KEY, payload.rstrip())
            future = session.post(self.GQL_ENDPOINT,  headers=utils.set_request_headers(), json=schema)
            # payloads containing brackets or other chars may be escaped in schema and so 
            # this way I can check for real what payload has been sent
            # TODO escape chars so they made it into json
            future.payload = utils.find_key(schema, self.KEY)[0]
            futures.append(future)

        # attack!
        for future in as_completed(futures):
            response = future.result()
            print("Tested: {}".format(future.payload))
            print("Status: {}".format(response.status_code))
            print("{}".format(response.text))
            print("Elapsed: {}s".format(response.elapsed))
            print("="*10)
        