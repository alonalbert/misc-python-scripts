#!/usr/bin/python3

import argparse
import datetime
import gzip
import json
import os

from duolingo_client import Duo

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Daily Daily Data.')

    parser.add_argument('user', help='Duolingo user name')
    parser.add_argument('--out', help='Output dir', default=None)

    parser.add_argument('--zip', dest='zip', help='Zip data', action='store_true')
    parser.add_argument('--no-zip', dest='zip', help="Don't zip data", action='store_false')
    parser.set_defaults(zip=False)

    args = parser.parse_args()
    duo = Duo(args.user)
    dataJson =  json.dumps(duo.get_data(), indent=2)

    if args.out is None:
        print(dataJson)
    else:
        os.makedirs(args.out, exist_ok=True)
        ext = 'gz' if args.zip else 'json'
        filename = datetime.datetime.now().strftime('%Y-%m-%d-duolingo-data.') + ext
        if args.zip:
            writer = gzip.open
            data = dataJson.encode()
        else:
            writer = open
            data = dataJson
        with writer(os.path.join(args.out, filename), 'w') as f:
            f.write(data)
