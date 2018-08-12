"""
This script is run every 7 days by Travis Cron job.
Here is the flowchart of how it works.

                +----------------------------------+
                |Check if any Monthly report exists|
                +---------------+------------------+
                                |
                                |
                +--------Y------+--------N---------+
                |                                  |
                v                                  |
   How old is the latest report?                   |
      |                        |                   |
      |                        |                   |
Less than 27 days        More than 27 days         |
      |                        |                   |
      |                        +-------------------+
      |                        |
      v                        v
    Quit        Pick the latest two metrics which are
                atleast 27 days apart; generate report

"""


from glob import glob
import datetime
import json
import os
import re
import textwrap


PATH_TO_METRICS_DATA = "_data"
PATH_TO_METRICS_POSTS = "_posts"
MIN_DIFFERENCE = 27 # In Days
MONTHLY_METRICS_VERSION = "0.1"
ORG_MONTHLY_METRICS_VERSION = "0.1"

ORG_REPORT_JSON = {}  # Summed up data for the entire github org


ALL_PROJECTS = filter(os.path.isdir, glob(PATH_TO_METRICS_DATA + "/*/*"))
"""
Generate report for each project
"""
for project in ALL_PROJECTS:
    print("LOG: Starting with", project)
    files_for_project = os.listdir(project)

    # Get the latest two metrics for this project which are MIN_DIFFERENCE days apart
    re_metrics = re.compile(r"METRICS-\d{4}-\d{2}-\d{2}.json")
    all_metrics = []

    for filename in files_for_project:
        if re_metrics.match(filename):
            all_metrics.append(filename)

    all_metrics.sort()
    # Come back later when there are atleast two generated metrics files
    if len(all_metrics) < 2:
        continue

    this_month_json_file = all_metrics.pop()
    print("LOG: This month json file", this_month_json_file)

    # If the latest Metrics is older than MIN_DIFFERENCE, then don't generate report
    # This is possible in cases of repo turning private or moving out
    today_datestamp = datetime.datetime.now()
    latest_datestamp = datetime.datetime.strptime(this_month_json_file, "METRICS-%Y-%m-%d.json")
    datetime_delta = today_datestamp - latest_datestamp
    if datetime_delta.days > MIN_DIFFERENCE:
        print("Skipping report for", project, "Latest metrics file is older than MIN_DIFFERENCE")
        continue

    last_month_json_file = None
    last_month_index = len(all_metrics) - 1
    while(last_month_index >= 0):
        # Calculate difference between last two metrics
        d1 = datetime.datetime.strptime(this_month_json_file, "METRICS-%Y-%m-%d.json")
        d2 = datetime.datetime.strptime(all_metrics[last_month_index], "METRICS-%Y-%m-%d.json")
        if (d1 - d2).days > MIN_DIFFERENCE:
            last_month_json_file = all_metrics[last_month_index]
            print("LOG: Last month json", last_month_json_file)
            break
        else:
            last_month_index -= 1

    # Metrics are not older than MIN_DIFFERENCE days
    if last_month_json_file is None:
        print("LOG: Latest two metrics are not older than MIN_DIFFERENCE days")
        continue

    # Data saved as the new report
    REPORT_JSON = {}

    with open(project + "/" + this_month_json_file) as f:
        this_month_json = json.load(f)

    with open(project + "/" + last_month_json_file) as f:
        last_month_json = json.load(f)

    REPORT_JSON["nameWithOwner"] = this_month_json["nameWithOwner"]
    REPORT_JSON["reportID"] = "MONTHLY-{}".format(this_month_json["datestamp"])
    REPORT_JSON["datestamp"] = {
        "this_month": this_month_json["datestamp"],
        "last_month": last_month_json["datestamp"]
    }

    org, repo = REPORT_JSON["nameWithOwner"].split("/")

    if org not in ORG_REPORT_JSON:
        ORG_REPORT_JSON[org] = {}
        ORG_REPORT_JSON[org]["name"] = org
        ORG_REPORT_JSON[org]["reportID"] = "MONTHLY-{}".format(this_month_json["datestamp"])
        ORG_REPORT_JSON[org]["datestamp"] = {
            "this_month": this_month_json["datestamp"],
            "last_month": last_month_json["datestamp"]
        }
        ORG_REPORT_JSON[org]["data"] = {}

    try:
        ORG_REPORT_JSON[org]["no_of_repos"] += 1
    except KeyError:
        ORG_REPORT_JSON[org]["no_of_repos"] = 1

    REPORT_JSON["data"] = {}
    # commits_this_month = this_month_json["defaultBranchRef"]["target"]["history"]["totalCount"]
    # commits_last_month = last_month_json["defaultBranchRef"]["target"]["history"]["totalCount"]
    # REPORT_JSON["data"]["commits"] = {
    #     "this_month": commits_this_month,
    #     "last_month": commits_last_month,
    # }

    # forks_this_month = this_month_json["forkCount"]
    # forks_last_month = last_month_json["forkCount"]
    # REPORT_JSON["data"]["forkCount"] = {
    #     "this_month": forks_this_month,
    #     "last_month": forks_last_month,
    # }

    # try:
    #     # commits
    #     ORG_REPORT_JSON[org]["data"]["commits"]["this_month"] += commits_this_month
    #     ORG_REPORT_JSON[org]["data"]["commits"]["last_month"] += commits_last_month

    #     # forks
    #     ORG_REPORT_JSON[org]["data"]["forkCount"]["this_month"] += forks_this_month
    #     ORG_REPORT_JSON[org]["data"]["forkCount"]["last_month"] += forks_last_month
    # except KeyError as e:
    #     ORG_REPORT_JSON[org]["data"]["commits"] = {
    #         "this_month": commits_this_month,
    #         "last_month": commits_last_month,
    #         "diff_breakdown": {}
    #     }

    #     ORG_REPORT_JSON[org]["data"]["forkCount"] = {
    #         "this_month": forks_this_month,
    #         "last_month": forks_last_month,
    #         "diff_breakdown": {}
    #     }

    # if commits_this_month - commits_last_month:
    #     ORG_REPORT_JSON[org]["data"]["commits"]["diff_breakdown"][repo] = commits_this_month - commits_last_month

    # if forks_this_month - forks_last_month:
    #     ORG_REPORT_JSON[org]["data"]["forkCount"]["diff_breakdown"][repo] = forks_this_month - forks_last_month

    # Grouping similar metrics
    for metric in ["commits", "forkCount", "issues", "openIssues", "closedIssues", "pullRequests", "openPullRequests",
                   "mergedPullRequests", "closedPullRequests", "stargazers", "watchers"]:
        REPORT_JSON["data"][metric] = {
            "this_month": this_month_json[metric],
            "last_month": last_month_json[metric],
        }

        try:
            ORG_REPORT_JSON[org]["data"][metric]["this_month"] += this_month_json[metric]
            ORG_REPORT_JSON[org]["data"][metric]["last_month"] += last_month_json[metric]
        except KeyError:
            ORG_REPORT_JSON[org]["data"][metric] = {
                "this_month": this_month_json[metric],
                "last_month": last_month_json[metric],
                "diff_breakdown": {}
            }

        if this_month_json[metric] - last_month_json[metric]:
            ORG_REPORT_JSON[org]["data"][metric]["diff_breakdown"][repo] = this_month_json[metric] - last_month_json[metric]

    # Project report diff
    # Org report diff done after the for loop for projects ends
    for metric in REPORT_JSON["data"]:
        REPORT_JSON["data"][metric]["diff"] = REPORT_JSON["data"][metric]["this_month"] - REPORT_JSON["data"][metric]["last_month"]

    with open("{}/{}.json".format(project, REPORT_JSON["reportID"]), "w+") as f:
        json.dump(REPORT_JSON, f)
    print("LOG: Wrote REPORT to", "{}/{}.json".format(project, REPORT_JSON["reportID"]))


    # Create .md file in _posts with datestamp
    post_text = """\
    ---
    layout: monthly-metrics-v{version}
    title: TwiterOSS Metrics Report for {owner}/{repo} | {reportID} | {datestampThisMonth}
    permalink: /{owner}/{repo}/{link}/

    owner: {owner}
    repo: {repo}
    reportID: {reportID}
    datestampThisMonth: {datestampThisMonth}
    datestampLastMonth: {datestampLastMonth}
    ---

    <table style="width: 100%">
        <tr>
            <th>Metric</th>
            <th>This Month</th>
            <th>Last Month</th>
            <th>+/-</th>
        </tr>
        {{% for item in site.data["{owner_in_data}"]["{repo_in_data}"]["{reportID}"]["data"] %}}
        <tr>
            <th>{{{{ item[0] }}}}</th>
            <th>{{{{ item[1]["this_month"] }}}}</th>
            <th>{{{{ item[1]["last_month"] }}}}</th>
            <th>{{{{ item[1]["diff"] }}}}</th>
        </tr>
        {{% endfor %}}
    </table>

    """

    normal_post_text = post_text.format(
        version=MONTHLY_METRICS_VERSION,
        owner=REPORT_JSON["nameWithOwner"].split("/")[0],
        owner_in_data=REPORT_JSON["nameWithOwner"].split("/")[0].replace('.', ''),  # Dots confused jekyll
        repo=REPORT_JSON["nameWithOwner"].split("/")[1],
        repo_in_data=REPORT_JSON["nameWithOwner"].split("/")[1].replace('.', ''),
        reportID=REPORT_JSON["reportID"],
        datestampThisMonth=REPORT_JSON["datestamp"]["this_month"],
        datestampLastMonth=REPORT_JSON["datestamp"]["last_month"],
        link=REPORT_JSON["reportID"])

    latest_post_text = post_text.format(
        version=MONTHLY_METRICS_VERSION,
        owner=REPORT_JSON["nameWithOwner"].split("/")[0],
        owner_in_data=REPORT_JSON["nameWithOwner"].split("/")[0].replace('.', ''),
        repo=REPORT_JSON["nameWithOwner"].split("/")[1],
        repo_in_data=REPORT_JSON["nameWithOwner"].split("/")[1].replace('.', ''),
        reportID=REPORT_JSON["reportID"],
        datestampThisMonth=REPORT_JSON["datestamp"]["this_month"],
        datestampLastMonth=REPORT_JSON["datestamp"]["last_month"],
        link="MONTHLY")


    # Create directory for the post, if it does not exist
    path_to_post = PATH_TO_METRICS_POSTS + "/" + REPORT_JSON["nameWithOwner"]
    os.makedirs(path_to_post, exist_ok=True)

    # This is a weird filename for sure. But I think I have an explanation for it -
    # posts need to start with %Y-%m-%d and the later is sent to page.title variable
    # Without the later date, title did not make much sense.
    normal_post_file = "{}/{}-{}.md".format(path_to_post, REPORT_JSON["datestamp"]["this_month"], REPORT_JSON["reportID"])
    with open(normal_post_file, "w+") as f:
        f.write(textwrap.dedent(normal_post_text))
    print("LOG: Created a POST", normal_post_file)

    # Delete already existing latest posts
    re_latest_report = re.compile(r"\d{4}-\d{2}-\d{2}-MONTHLY-LATEST.md")
    for filename in os.listdir(path_to_post):
        if re_latest_report.match(filename):
            print("LOG: Removing existing latest post", os.path.join(path_to_post, filename))
            os.unlink(os.path.join(path_to_post, filename))

    # Create latest report file in _posts as well
    latest_post_file = "{}/{}-MONTHLY-LATEST.md".format(path_to_post, REPORT_JSON["datestamp"]["this_month"])
    with open(latest_post_file, "w+") as f:
        f.write(textwrap.dedent(latest_post_text))
    print("LOG: Created the latest POST", latest_post_file)


"""
Get the diff of each data metric
"""
for org in ORG_REPORT_JSON:
    for metric in ORG_REPORT_JSON[org]["data"]:
        ORG_REPORT_JSON[org]["data"][metric]["diff"] = ORG_REPORT_JSON[org]["data"][metric]["this_month"] - ORG_REPORT_JSON[org]["data"][metric]["last_month"]


"""
Generate report for each org
"""
for org in ORG_REPORT_JSON:
    path_to_org = PATH_TO_METRICS_DATA + "/" + org
    with open("{}/{}.json".format(path_to_org, ORG_REPORT_JSON[org]["reportID"]), "w+") as f:
        json.dump(ORG_REPORT_JSON[org], f)

    # Create post for the org
    post_text = """\
    ---
    layout: org-monthly-metrics-v{version}
    title: TwiterOSS Metrics Report for {org} | {reportID}
    permalink: /{org}/{link}/

    org: {org}
    reportID: {reportID}
    datestampThisMonth: {datestampThisMonth}
    datestampLastMonth: {datestampLastMonth}
    ---

    <table style="width: 100%">
        <tr>
            <th>Metric</th>
            <th>This Month</th>
            <th>Last Month</th>
            <th>+/-</th>
        </tr>
        {{% for item in site.data["{org_in_data}"]["{reportID}"]["data"] %}}
        <tr>
            <th>{{{{ item[0] }}}}</th>
            <th>{{{{ item[1]["this_month"] }}}}</th>
            <th>{{{{ item[1]["last_month"] }}}}</th>
            <th>{{{{ item[1]["diff"] }}}}</th>
        </tr>
        {{% endfor %}}
    </table>

    """

    normal_post_text = post_text.format(
        version=ORG_MONTHLY_METRICS_VERSION,
        org=org,
        org_in_data=org.replace('.', ''),
        reportID=REPORT_JSON["reportID"],
        datestampThisMonth=REPORT_JSON["datestamp"]["this_month"],
        datestampLastMonth=REPORT_JSON["datestamp"]["last_month"],
        link=REPORT_JSON["reportID"])

    latest_post_text = post_text.format(
        version=ORG_MONTHLY_METRICS_VERSION,
        org=org,
        org_in_data=org.replace('.', ''),
        reportID=REPORT_JSON["reportID"],
        datestampThisMonth=REPORT_JSON["datestamp"]["this_month"],
        datestampLastMonth=REPORT_JSON["datestamp"]["last_month"],
        link="MONTHLY")


    # Create directory for the post, if it does not exist
    path_to_post = PATH_TO_METRICS_POSTS + "/" + org
    os.makedirs(path_to_post, exist_ok=True)

    # This is a weird filename for sure. But I think I have an explanation for it -
    # posts need to start with %Y-%m-%d and the later is sent to page.title variable
    # Without the later date, title did not make much sense.
    normal_post_file = "{}/{}-{}.md".format(path_to_post, ORG_REPORT_JSON[org]["datestamp"]["this_month"], ORG_REPORT_JSON[org]["reportID"])
    with open(normal_post_file, "w+") as f:
        f.write(textwrap.dedent(normal_post_text))
    print("LOG: Created a POST", normal_post_file)

    # Delete already existing latest posts
    re_latest_report = re.compile(r"\d{4}-\d{2}-\d{2}-MONTHLY-LATEST.md")
    for filename in os.listdir(path_to_post):
        if re_latest_report.match(filename):
            print("LOG: Removing existing latest post", os.path.join(path_to_post, filename))
            os.unlink(os.path.join(path_to_post, filename))

    # Create latest report file in _posts as well
    latest_post_file = "{}/{}-MONTHLY-LATEST.md".format(path_to_post, ORG_REPORT_JSON[org]["datestamp"]["this_month"])
    with open(latest_post_file, "w+") as f:
        f.write(textwrap.dedent(latest_post_text))
    print("LOG: Created the latest POST", latest_post_file)
