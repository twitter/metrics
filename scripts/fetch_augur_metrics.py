"""
Fetch metrics provided by Augur.
https://github.com/osshealth/augur

Progress: https://github.com/twitter/metrics/issues/2
"""

import json
import os
import datetime
import requests

API_ENDPOINT = "http://twitter.augurlabs.io/api/unstable"
PATH_TO_METRICS_DATA = "_data"
PATH_TO_METADATA = "_metadata"
DATESTAMP = datetime.datetime.now().date().isoformat()

print("LOG: Assuming the current path to be the root of the metrics repository.")
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


"""
Timeseries of new watchers

API: /:owner/:repo/timeseries/watchers

This API endpoint gives a timeseries of new watchers in a date range.
Not to be confused with actual number of watchers.
Ref https://github.com/OSSHealth/augur/issues/152
"""
path_to_metrics_dir = f"{PATH_TO_METADATA}/augur/timeseries_new_watchers"
for org in PROJECTS_TRACKED['projects']:
    for repo in PROJECTS_TRACKED['projects'][org]:
        dir_name = f"{path_to_metrics_dir}/{org}/{repo}"
        file_name = f"{dir_name}/data.json"
        os.makedirs(dir_name, exist_ok=True)

        print(f"Sending request to {API_ENDPOINT}/{org}/{repo}/timeseries/watchers")
        r = requests.get(f"{API_ENDPOINT}/{org}/{repo}/timeseries/watchers")
        try:
            if r.ok:
                print("OK!")
                data = r.json()[:-1] # Last metric is not valid

                # Manipulation
                new_watchers_timeseries = []

                for i in range(1, len(data)):
                    old = data[i]
                    new = data[i - 1]
                    new_date = datetime.datetime.strptime(new["date"].split("T")[0], "%Y-%m-%d")
                    old_date = datetime.datetime.strptime(old["date"].split("T")[0], "%Y-%m-%d")

                    diff_days = (new_date - old_date).days
                    number = new["watchers"]

                    count_per_week = round(number/diff_days * 7, 2)
                    count_per_month = round(number/diff_days * 30, 2)

                    new_watchers_timeseries.append({"date": new_date.strftime("%Y-%m-%d"),
                                                    "count_per_week": count_per_week,
                                                    "count_per_month": count_per_month})
                with open(file_name, "w+") as f:
                    json.dump(new_watchers_timeseries, f)
            else:
                print(f"Error! Response code {r.status_code}")
                print(r.content.decode("utf-8"))
        except Exception as e:
            raise(e)
            print(f"Error: Something went wrong with /:owner/:repo/timeseries/watchers - {e}")
