"""
Fetch metrics provided by Augur.
https://github.com/osshealth/augur

Progress: https://github.com/twitter/metrics/issues/2
"""

import datetime
import json
import os

import requests


API_ENDPOINT = "http://newtwitter.augurlabs.io/api/unstable"
PATH_TO_METRICS_DATA = "_data"
PATH_TO_METADATA = "_metadata"
DATESTAMP = datetime.datetime.now().date().isoformat()

print("LOG: Assuming the current path to be the root of the metrics repository.")
# tracked projects
with open(os.path.join(PATH_TO_METADATA, "projects_tracked.json")) as f:
    PROJECTS_TRACKED = json.load(f)

"""
Bus Factor

API: /:owner/:repo/bus_factor

The API endpoint is unstable and experimental as of now. There is no guarantee of a result
each time. That's why bus factor is cached as a one time result and frequently
updated. In future, this metric can be included in _data and saved weekly,
once the API becomes reliable.

Update _metadata/augur/bus_factor.json
"""

BUS_FACTOR = {}
bus_factor_json_file = f"{PATH_TO_METADATA}/augur/bus_factor.json"
if os.path.exists(bus_factor_json_file):
    with open(bus_factor_json_file) as f:
        BUS_FACTOR = json.load(f)

for org in PROJECTS_TRACKED['projects']:
    for repo in PROJECTS_TRACKED['projects'][org]:
        print(f"Sending request to {API_ENDPOINT}/{org}/{repo}/bus_factor")
        r = requests.get(f"{API_ENDPOINT}/{org}/{repo}/bus_factor")
        try:
            if r.ok:
                print("OK!")
                bus_factor = r.json()[0]
                BUS_FACTOR[f"{org}/{repo}"] = bus_factor
            else:
                print(f"Error! Response code {r.status_code}")
                print(r.content.decode("utf-8"))
        except Exception as e:
            print(f"Error: Something went wrong with /:owner/:repo/bus_factor - {e}")

with open(bus_factor_json_file, "w+") as f:
    json.dump(BUS_FACTOR, f)
