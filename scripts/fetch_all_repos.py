import datetime
import json
import os

import requests

import graphql_queries


# PATH_TO_METRICS_REPO = "/Users/hmishra/workspace/twitter/metrics"
# PATH_TO_METRICS_DATA = PATH_TO_METRICS_REPO + "/_data"
PATH_TO_METRICS_DATA = "_data"
GITHUB_USERNAME = os.environ["GH_USERNAME"]
# GITHUB_USERNAME = "OrkoHunter"
GITHUB_OAUTH_TOKEN = os.environ["OAUTH_TOKEN"]
# GITHUB_OAUTH_TOKEN = "c673b1e8af4a56a7ccee71badfbd06b264ec190b"
GITHUB_API_ENDPOINT = "https://api.github.com/graphql"
DATESTAMP = datetime.datetime.now().date().isoformat()

def fetch_one_page(query_string, variables):
    """
    Request the GitHub GraphQL API
    """
    headers = {
        "Content-Type": "application/json",
    }
    r = requests.post(GITHUB_API_ENDPOINT, json={"query": query_string, "variables": variables}, auth=(GITHUB_USERNAME, GITHUB_OAUTH_TOKEN))
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("Error in GitHub API query. Status Code : {}, Response: {}".format(r.status_code, r.json()))

all_repository_edges = []  # All the repos in the org with their stats

# Combine the paginated responses from the API
has_next_page = False
end_cursor = None
num_of_pages = 0
while True:
    print("Num of pages", num_of_pages)
    variables = json.dumps({"owner": "twitter", "endCursor": end_cursor})

    print("Sending request")
    response = fetch_one_page(graphql_queries.org_all_repos, variables)
    print("Received request")

    repository_edges = response["data"]["organization"]["repositories"]["edges"]
    all_repository_edges.extend(repository_edges)

    pageInfo = response["data"]["organization"]["repositories"]["pageInfo"]
    has_next_page = pageInfo["hasNextPage"]
    print("has_next_page", has_next_page)
    end_cursor = pageInfo["endCursor"]
    print("end_cursor", end_cursor)
    num_of_pages += 1
    if not has_next_page:
        break

print("LOG: Fetched all the repositories. Count:", len(all_repository_edges))

## TODO: Repos to exclude and include from files in the metrics repo
repos_to_exclude = []
# repos_to_include = []

# Convert all_repository_edges to DATA_JSON with the following format -
# key: value :: repo_full_name: repo_data

DATA_JSON = {}

for edge in all_repository_edges:
    repo_full_name = edge["node"]["nameWithOwner"]
    repo_data = edge["node"]
    DATA_JSON[repo_full_name] = repo_data

for repo in repos_to_exclude:
    try:
        del DATA_JSON[repo]
    except Exception as e:
        pass


# Save the respective JSON files
for repo in DATA_JSON:
    owner, project = repo.split("/")
    # Create directories inside twitter/metrics/_data if they don't exist
    owner_dir_path = "{}/{}".format(PATH_TO_METRICS_DATA, owner)
    repo_dir_path = "{}/{}".format(owner_dir_path, project)
    if not os.path.isdir(owner_dir_path):
        os.mkdir(owner_dir_path)
    if not os.path.isdir(repo_dir_path):
        os.mkdir(repo_dir_path)

    # Add datestamp inside the JSON
    DATA_JSON[repo]["datestamp"] = DATESTAMP

    # Save the json file with a timestamp
    file_name = "METRICS-" + DATESTAMP + ".json"
    with open(repo_dir_path + "/" + file_name, "w+") as f:
        json.dump(DATA_JSON[repo], f)
    print("LOG: Saving", file_name, "for", repo)
