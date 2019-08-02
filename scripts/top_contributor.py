import requests
import json
import queries
import header
from dateutil import parser
from dateutil.relativedelta import *
from datetime import *

GITHUB_USERNAME = os.environ["GH_USERNAME"]
GITHUB_OAUTH_TOKEN = os.environ["OAUTH_TOKEN"]
GITHUB_API_ENDPOINT = "https://api.github.com/graphql"

headers = {
  "Authorization": f"Bearer {GITHUB_OAUTH_TOKEN}"
}
'''
Runs the GraphQL query given to it by posting to the GitHub
Api Endpoint and then checking if the returned status code is okay or not
and raising exceptions if not.
'''


def run_queury(query):
  request = requests.post(GITHUB_API_ENDPOINT, json={'query': query}, headers=headers)
  if request.status_code == 200:
    return request.json()
  else:
    raise Exception("Query failed with status code {}. {}.".format(request.status_code, query))


'''
Queries for getting the reepositories 
from an organization and then the PRs from those repos.
'''
login_query = queries.query2
email_query = queries.query3

# Keeping track of time taken to query
start_time = datetime.now()

result = run_queury(login_query)
# An iterable dict from the query with iterables being repository dicts themselves
repository_edges = result["data"]["organization"]["repositories"]["edges"]
# Keeping track of the logins of top contributors
login_list = {}
for repo in repository_edges:
  login_list[repo["node"]["name"]] = []
  pull_request_edges = repo["node"]["pullRequests"]["edges"]
  for pr in pull_request_edges:
    '''
    making sure that the pull requests are recent enough and breaking
    if not since we know that the PRs are goint to be chronologically sorted.
    '''
    merge_date = (parser.parse(pr["node"]["closedAt"]))
    today = datetime.now(timezone.utc)
    time_delta = relativedelta(today, merge_date)
    if (time_delta.years != 0 or time_delta.months > 3):
      break
    if pr["node"]["author"] is None:
      continue
    login_list[repo["node"]["name"]].append(pr["node"]["author"]["login"])


repos = login_list.keys()
contributor_dict = {}
unique_emails = {}
# Keeping track of contributions over the organizational level
total_contributions = {}

for repo in repos:
  contributor_list = login_list[repo]
  contributor_dict[repo] = {}
  for contributor in contributor_list:
    if contributor not in unique_emails.keys():
      email_json = run_queury(email_query.substitute(login=str(contributor)))
      if ("data" not in email_json.keys()):
        continue
      email = email_json["data"]["user"]["email"]
      name = email_json["data"]["user"]["name"]
      if (email is None or email == ""):
        continue
      if (name is None or email == ""):
        continue
      contributor_dict_key = name + " <" + email + ">"
      unique_emails[contributor] = contributor_dict_key
      total_contributions[contributor_dict_key] = 1
    if unique_emails[contributor] not in contributor_dict.keys():
      contributor_dict[repo][unique_emails[contributor]] = 1
      total_contributions[unique_emails[contributor]] += 1
    else:
      contributor_dict[repo][unique_emails[contributor]] += 1
      total_contributions[unique_emails[contributor]] += 1
  print("Time Elapsed ", repo, ": ", (datetime.now() - start_time).seconds)


with open('result.json', 'w') as file:
  json.dump(contributor_dict, file, ensure_ascii=False, indent=2)
with open('contributors.json', 'w') as file:
  json.dump(total_contributions, file, ensure_ascii=False, indent=2)
with open('top_emails.txt', 'w') as file:
  for repo in contributor_dict:
    if len(contributor_dict[repo].keys()) == 0:
      continue
    file.write((repo + ": \n"))
    for key in contributor_dict[repo].keys():
      file.write(key+"\n")
    file.write("\n")

print("Done")
