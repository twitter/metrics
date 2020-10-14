"""
Generate METRICS-%Y-%m-%d.json for all the repositories tracked by repos-to-include.txt
and save them in their respective _data directory.
"""

import datetime
import json
import os
import requests
import graphql_queries


print("LOG: Assuming the current path to be the root of the metrics repository.")
PATH_TO_METRICS_DATA = "_data"
PATH_TO_METADATA = "_metadata"
GITHUB_USERNAME = os.environ["GH_USERNAME"]
GITHUB_OAUTH_TOKEN = os.environ["OAUTH_TOKEN"]
GITHUB_API_ENDPOINT = "https://api.github.com/graphql"
DATESTAMP = datetime.datetime.now().date().isoformat()

# Read repos-to-include.txt
all_orgs = []  # Track orgs and all its repos e.g. twitter, twitterdev
all_repos = []  # Track specific repositories e.g. ['pantsbuild/pants', 'pantsbuild/pex']

with open("repos-to-include.txt") as f:
    for line in f:
        owner, repo = line.split("/")
        repo = repo.rstrip("\n")
        if repo == "*":
            all_orgs.append(owner)
        else:
            all_repos.append(owner + "/" + repo)

print("Orgs to track", all_orgs)
print("Repos to track", all_repos)

def fetch_one_page(query_string, variables):
    """
    Request the GitHub GraphQL API

    One time, the request failed but it passed after retrying. This was the response -
    ```
    Error in GitHub API query. Status Code : 502, Response: {'data': 'null', 'errors': [{'message': 'Something went wrong while executing your query.
    This may be the result of a timeout, or it could be a GitHub bug. Please include `80A9:464B:6AEAA9:78BA60:5B748709` when reporting this issue.'}]}
    ```

    This function makes 5 trials before giving up

    """
    headers = {
        "Content-Type": "application/json",
    }
    attempt = 0
    while(attempt<=5):
        r = requests.post(GITHUB_API_ENDPOINT, json={"query": query_string, "variables": variables}, auth=(GITHUB_USERNAME, GITHUB_OAUTH_TOKEN))
        if r.status_code == 200:
            return r.json()
            break
        else:
            attempt += 1
            print("\n\n\n Error in GitHub API query. Status Code : {}, Response: {}".format(r.status_code, r.json()))
            print("\n Trying again... ({}/5)".format(attempt))

    raise Exception("Error in GitHub API query. Status Code : {}, Response: {}".format(r.status_code, r.json()))

all_org_edges = []  # All the repos in the org with their stats

for org in all_orgs:
    # Combine the paginated responses from the API
    has_next_page = False
    end_cursor = None
    num_of_pages = 0
    while True:
        # print("Num of pages", num_of_pages)
        variables = json.dumps({"owner": org, "endCursor": end_cursor})

        print("Sending request")
        response = fetch_one_page(graphql_queries.org_all_repos, variables)
        print("Received request")

        repository_edges = response["data"]["organization"]["repositories"]["edges"]
        all_org_edges.extend(repository_edges)

        pageInfo = response["data"]["organization"]["repositories"]["pageInfo"]
        has_next_page = pageInfo["hasNextPage"]
        # print("has_next_page", has_next_page)
        end_cursor = pageInfo["endCursor"]
        # print("end_cursor", end_cursor)
        num_of_pages += 1
        if not has_next_page:
            break

# print("LOG: Fetched all the org repositories. Count:", len(all_org_edges))

# Fetch individual repositories' data
all_repo_edges = []  # All individual repos

for item in all_repos:
    owner, repo = item.split("/")
    variables = json.dumps({"owner": owner, "repo": repo, "endCursor": None})

    response = fetch_one_page(graphql_queries.repo_wise, variables)
    # print("response for", repo, response)
    all_repo_edges.append(response["data"])
    # print("TYPE", type(response["data"]))

# print("LOG: Fetched all the individual repos as well. Count:", len(all_repo_edges))

# Repos to exclude from the project
repos_to_exclude = set()
with open("repos-to-exclude.txt", "r") as f:
    for line in f:
        repo = line.rstrip("\n")
        repos_to_exclude.add(repo)

# Convert all_org_edges to DATA_JSON with the following format -
# key: value :: repo_full_name: repo_data

DATA_JSON = {}

for edge in all_org_edges:
    if edge["node"]["isPrivate"]:
        continue
    if edge["node"]["nameWithOwner"] in repos_to_exclude:
        print("Skipping", edge["node"]["nameWithOwner"], "(from repos-to-exclude.txt)")
        continue
    repo_full_name = edge["node"]["nameWithOwner"]
    repo_data = edge["node"]
    DATA_JSON[repo_full_name] = repo_data

for edge in all_repo_edges:
    if edge["repository"]["isPrivate"]:
        continue
    repo_full_name = edge["repository"]["nameWithOwner"]
    repo_data = edge["repository"]
    DATA_JSON[repo_full_name] = repo_data


# Simplify the format of json
for repo in DATA_JSON:
    old_json = DATA_JSON[repo]
    new_json = {
        'datestamp': DATESTAMP,
        'nameWithOwner': old_json['nameWithOwner'],
        'name': old_json['name'],
        'commits': old_json['defaultBranchRef']['target']['history']['totalCount'],
        'forkCount': old_json['forkCount'],
        'issues': old_json['issues']['totalCount'],
        'openIssues': old_json['openIssues']['totalCount'],
        'closedIssues': old_json['closedIssues']['totalCount'],
        'pullRequests': old_json['pullRequests']['totalCount'],
        'openPullRequests': old_json['openPullRequests']['totalCount'],
        'mergedPullRequests': old_json['mergedPullRequests']['totalCount'],
        'closedPullRequests': old_json['closedPullRequests']['totalCount'],
        'stargazers': old_json['stargazers']['totalCount'],
        'watchers': old_json['watchers']['totalCount'],
    }
    DATA_JSON[repo] = new_json

# Update _metadata/projects_tracked.json
PROJECTS_TRACKED = {}
orgs_tracked = set()
repos_tracked = set()
for reponame in DATA_JSON:
    orgname = reponame.split("/")[0]
    orgs_tracked.add(orgname)
    repos_tracked.add(reponame)

PROJECTS_TRACKED['orgs'] = list(orgs_tracked)
PROJECTS_TRACKED['projects'] = {}

for reponame in repos_tracked:
    org, repo = reponame.split("/")
    try:
        PROJECTS_TRACKED['projects'][org].append(repo)
    except KeyError:
        PROJECTS_TRACKED['projects'][org] = [repo]

with open(os.path.join(PATH_TO_METADATA, "projects_tracked.json"), "w+") as f:
    json.dump(PROJECTS_TRACKED, f)

# Add CHAOSS specific metrics
# The API endpoint is http://twitter.augurlabs.io/api/unstable/
# And the API documentation is at https://osshealth.github.io/augur/api/index.html



# Save the respective JSON files
for repo in DATA_JSON:
    owner, project = repo.split("/")
    # Create directories inside twitter/metrics/_data if they don't exist
    owner_dir_path = "{}/{}".format(PATH_TO_METRICS_DATA, owner)
    repo_dir_path = "{}/{}".format(owner_dir_path, project)
    os.makedirs(repo_dir_path, exist_ok=True)
    # if not os.path.isdir(owner_dir_path):
    #     os.mkdir(owner_dir_path)
    # if not os.path.isdir(repo_dir_path):
    #     os.mkdir(repo_dir_path)

    # Save the json file with a timestamp
    file_name = "METRICS-" + DATESTAMP + ".json"
    with open(repo_dir_path + "/" + file_name, "w+") as f:
        json.dump(DATA_JSON[repo], f)
    print("LOG: Saving", file_name, "for", repo)
