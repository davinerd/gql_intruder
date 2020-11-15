from urllib.parse import urlparse


def set_request_headers():
    return {'Content-Type': 'application/json'}

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

# Kudos to this individual: https://stackoverflow.com/a/835527
# We want to go easy on this though...
def parse_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.netloc and not parsed_url.scheme:
        return None

    return "{}://{}{}".format(parsed_url.scheme, parsed_url.netloc, parsed_url.path)