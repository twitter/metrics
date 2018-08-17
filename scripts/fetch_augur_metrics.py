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
GITHUB_USERNAME = os.environ["GH_USERNAME"]
GITHUB_OAUTH_TOKEN = os.environ["OAUTH_TOKEN"]
GITHUB_API_ENDPOINT = "https://api.github.com/graphql"


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
Contributors

API: /:owner/:repo/contributors
"""
path_to_metrics_dir = f"{PATH_TO_METADATA}/augur/contributors"
CONTRIBUTORS = {}
for org in PROJECTS_TRACKED['projects']:
    for repo in PROJECTS_TRACKED['projects'][org]:
        dir_name = f"{path_to_metrics_dir}/{org}/{repo}"
        file_name = f"{dir_name}/data.json"
        os.makedirs(dir_name, exist_ok=True)

        print(f"Sending request to {API_ENDPOINT}/{org}/{repo}/contributors")
        r = requests.get(f"{API_ENDPOINT}/{org}/{repo}/contributors")
        try:
            if r.ok:
                print("OK!")
                data = r.json()
                CONTRIBUTORS[f"{org}/{repo}"] = data
            else:
                print(f"Error! Response code {r.status_code}")
                print(r.content.decode("utf-8"))
        except Exception as e:
            raise(e)
            print(f"Error: Something went wrong with /:owner/:repo/contributors - {e}")

# The data in CONTRIBUTORS contains a lot of bogus users
# https://github.com/osshealth/augur/issues/147
# We will now remove them
all_users = set()
for project in CONTRIBUTORS:
    for user in CONTRIBUTORS[project]:
        all_users.add(user["name"])

print(f"len(all_users) users including bogus data")

def chunks(iterable, n):
    """Yield successive n-sized chunks from l"""
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]

users_chunk = chunks(list(all_users), 2000) # GitHub API fails for a number larger than this


real_users = {}  # key: login ; value: Info
count = 0
for chunk in users_chunk:
    count += 1
    print(f"Sending request for chunk {count}")
    query = "query {"
    _query = """
        user_{key}: user (login: "{username}") {{
            ...Info
        }}
    """
    for i in range(len(chunk)):
        query += _query.format(key=i, username=chunk[i])

    query += "}"

    query += """
    fragment Info on User {
        login
        avatarUrl
        isHireable
        company
        location
        name
        url
    }
    """

    headers = {
        "Content-Type": "application/json",
    }
    attempt = 0
    while(attempt<=5):
        r = requests.post(GITHUB_API_ENDPOINT, json={"query": query}, auth=(GITHUB_USERNAME, GITHUB_OAUTH_TOKEN))
        if r.status_code == 200:
            result = r.json()
            break
        else:
            attempt += 1
            print("\n\n\n Error in GitHub API query. Status Code : {}, Response: {}".format(r.status_code, r.json()))
            print("\n Trying again... ({}/5)".format(attempt))

    for key in r.json()["data"]:
        if r.json()["data"][key]: # It's NoneValue for fake users
            username = r.json()["data"][key]["login"]
            real_users[username] = r.json()["data"][key]

print(f"{len(real_users)} actual users")

PROJECT_CONTRIBUTORS = {}
for project in CONTRIBUTORS:
    data = {}
    for _user in CONTRIBUTORS[project]:
        user = _user.copy()
        if user["name"] in real_users:
            data[user["name"]] = user
            data[user["name"]].update(real_users[user["name"]])
    PROJECT_CONTRIBUTORS[project] = data

for project in PROJECT_CONTRIBUTORS:
    dir_path = f"{path_to_metrics_dir}/{project}"
    os.makedirs(dir_path, exist_ok=True)
    file_path = f"{dir_path}/data.json"
    with open(file_path, "w+") as f:
        json.dump(PROJECT_CONTRIBUTORS[project], f)

ORG_CONTRIBUTORS = {}  # key: org ; value: aggregated data
for project in PROJECT_CONTRIBUTORS:
    org, repo = project.split("/")
    if org not in ORG_CONTRIBUTORS:
        ORG_CONTRIBUTORS[org] = {}
    for user in PROJECT_CONTRIBUTORS[project]:
        new_data = PROJECT_CONTRIBUTORS[project][user]
        try:
            ORG_CONTRIBUTORS[org][user]["commits"] += new_data["commits"]
            ORG_CONTRIBUTORS[org][user]["issues"] += new_data["issues"]
            ORG_CONTRIBUTORS[org][user]["commit_comments"] += new_data["commit_comments"]
            ORG_CONTRIBUTORS[org][user]["issue_comments"] += new_data["issue_comments"]
            ORG_CONTRIBUTORS[org][user]["pull_requests"] += new_data["pull_requests"]
            ORG_CONTRIBUTORS[org][user]["pull_requests_comments"] += new_data["pull_requests_comments"]
            ORG_CONTRIBUTORS[org][user]["total"] += new_data["total"]
        except KeyError:
            ORG_CONTRIBUTORS[org][user] = new_data

for org in ORG_CONTRIBUTORS:
    file_path = f"{path_to_metrics_dir}/{org}/data.json"
    with open(file_path, "w+") as f:
        json.dump(ORG_CONTRIBUTORS[org], f)

"""
Timeseries of new watchers

API: /:owner/:repo/timeseries/watchers

This API endpoint gives a timeseries of new watchers in a date range.
Not to be confused with actual number of watchers.
Ref https://github.com/OSSHealth/augur/issues/152

Old code leaved here for later reference

New idea: use the endpoint to get aggregate new_watchers per year or maybe something else
"""

# path_to_metrics_dir = f"{PATH_TO_METADATA}/augur/new_watchers"
# for org in PROJECTS_TRACKED['projects']:
#     for repo in PROJECTS_TRACKED['projects'][org]:
#         dir_name = f"{path_to_metrics_dir}/{org}/{repo}"
#         file_name = f"{dir_name}/data.json"
#         os.makedirs(dir_name, exist_ok=True)

#         print(f"Sending request to {API_ENDPOINT}/{org}/{repo}/timeseries/watchers")
#         r = requests.get(f"{API_ENDPOINT}/{org}/{repo}/timeseries/watchers")
#         try:
#             if r.ok:
#                 print("OK!")
#                 data = r.json()[:-1] # Last metric is not valid

#                 # Manipulation
#                 new_watchers_timeseries = []

#                 for i in range(1, len(data)):
#                     old = data[i]
#                     new = data[i - 1]
#                     new_date = datetime.datetime.strptime(new["date"].split("T")[0], "%Y-%m-%d")
#                     old_date = datetime.datetime.strptime(old["date"].split("T")[0], "%Y-%m-%d")

#                     diff_days = (new_date - old_date).days
#                     number = new["watchers"]

#                     count_per_week = round(number/diff_days * 7, 2)
#                     count_per_month = round(number/diff_days * 30, 2)

#                     new_watchers_timeseries.append({"date": new_date.strftime("%Y-%m-%d"),
#                                                     "count_per_week": count_per_week,
#                                                     "count_per_month": count_per_month})
#                 with open(file_name, "w+") as f:
#                     json.dump(new_watchers_timeseries, f)
#             else:
#                 print(f"Error! Response code {r.status_code}")
#                 print(r.content.decode("utf-8"))
#         except Exception as e:
#             raise(e)
#             print(f"Error: Something went wrong with /:owner/:repo/timeseries/watchers - {e}")
