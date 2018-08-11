"""
The script traverses inside _data/ directory recursively.
For every project, it picks the latest two METRICS-<datestamp>.json files (more than 6 days apart),
and generates the weekly report with appropriate number. It also updates the latest-weekly report.

I thought a lot about abstracting as much as I can. But duplication is required here to allow free growth
of all 4 types of reports (org/project + weekly/monthly)
Just in time, this article was #1 on HN - https://news.ycombinator.com/item?id=17578714
"""

from glob import glob
import datetime
import json
import os
import re
import textwrap

PATH_TO_METRICS_DATA = "_data"
PATH_TO_METRICS_POSTS = "_posts"
MIN_DIFFERENCE = 6 # In Days
WEEKLY_METRICS_VERSION = "0.1"
ORG_WEEKLY_METRICS_VERSION = "0.1"

ALL_PROJECTS = filter(os.path.isdir, glob(PATH_TO_METRICS_DATA + "/*/*"))

ORG_REPORT_JSON = {}  # Summed up data for the entire github org

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

    this_week_json_file = all_metrics.pop()
    print("LOG: This week json file", this_week_json_file)

    # If the latest Metrics is older than MIN_DIFFERENCE, then don't generate report
    # This is possible in cases of repo turning private or moving out
    today_datestamp = datetime.datetime.now()
    latest_datestamp = datetime.datetime.strptime(this_week_json_file, "METRICS-%Y-%m-%d.json")
    datetime_delta = today_datestamp - latest_datestamp
    if datetime_delta.days > MIN_DIFFERENCE:
        print("Skipping report for", project, "Latest metrics file is older than MIN_DIFFERENCE")
        continue

    last_week_json_file = None
    last_week_index = len(all_metrics) - 1
    while(last_week_index >= 0):
        # Calculate difference between last two metrics
        d1 = datetime.datetime.strptime(this_week_json_file, "METRICS-%Y-%m-%d.json")
        d2 = datetime.datetime.strptime(all_metrics[last_week_index], "METRICS-%Y-%m-%d.json")
        if (d1 - d2).days > MIN_DIFFERENCE:
            last_week_json_file = all_metrics[last_week_index]
            print("LOG: Last week json", last_week_json_file)
            break
        else:
            last_week_index -= 1

    # Metrics are not older than MIN_DIFFERENCE days
    if last_week_json_file is None:
        continue

    # Data saved as the new report
    REPORT_JSON = {}


    with open(project + "/" + this_week_json_file) as f:
        this_week_json = json.load(f)

    with open(project + "/" + last_week_json_file) as f:
        last_week_json = json.load(f)

    REPORT_JSON["nameWithOwner"] = this_week_json["nameWithOwner"]
    REPORT_JSON["reportID"] = "WEEKLY-{}".format(this_week_json["datestamp"])
    REPORT_JSON["datestamp"] = {
        "this_week": this_week_json["datestamp"],
        "last_week": last_week_json["datestamp"]
    }

    org, repo = REPORT_JSON["nameWithOwner"].split("/")

    if org not in ORG_REPORT_JSON:
        ORG_REPORT_JSON[org] = {}
        ORG_REPORT_JSON[org]["name"] = org
        ORG_REPORT_JSON[org]["reportID"] = "WEEKLY-{}".format(this_week_json["datestamp"])
        ORG_REPORT_JSON[org]["datestamp"] = {
            "this_week": this_week_json["datestamp"],
            "last_week": last_week_json["datestamp"]
        }
        ORG_REPORT_JSON[org]["data"] = {}

    try:
        ORG_REPORT_JSON[org]["no_of_repos"] += 1
    except KeyError:
        ORG_REPORT_JSON[org]["no_of_repos"] = 1

    REPORT_JSON["data"] = {}

    commits_this_week = this_week_json["defaultBranchRef"]["target"]["history"]["totalCount"]
    commits_last_week = last_week_json["defaultBranchRef"]["target"]["history"]["totalCount"]
    REPORT_JSON["data"]["commits"] = {
        "this_week": commits_this_week,
        "last_week": commits_last_week,
    }

    forks_this_week = this_week_json["forkCount"]
    forks_last_week = last_week_json["forkCount"]
    REPORT_JSON["data"]["forkCount"] = {
        "this_week": forks_this_week,
        "last_week": forks_last_week,
    }

    try:
        # commits
        ORG_REPORT_JSON[org]["data"]["commits"]["this_week"] += commits_this_week
        ORG_REPORT_JSON[org]["data"]["commits"]["last_week"] += commits_last_week
        if commits_this_week - commits_last_week:
            ORG_REPORT_JSON[org]["data"]["commits"]["diff_breakdown"][repo] = commits_this_week - commits_last_week

        # forks
        ORG_REPORT_JSON[org]["data"]["forkCount"]["this_week"] += forks_this_week
        ORG_REPORT_JSON[org]["data"]["forkCount"]["last_week"] += forks_last_week
        if forks_this_week - forks_last_week:
            ORG_REPORT_JSON[org]["data"]["forkCount"]["diff_breakdown"][repo] = forks_this_week - forks_last_week
    except KeyError:
        ORG_REPORT_JSON[org]["data"]["commits"] = {
            "this_week": commits_this_week,
            "last_week": commits_last_week,
        }
        if commits_this_week - commits_last_week:
            ORG_REPORT_JSON[org]["data"]["commits"]["diff_breakdown"] = {
                repo: commits_this_week - commits_last_week
            }

        ORG_REPORT_JSON[org]["data"]["forkCount"] = {
            "this_week": forks_this_week,
            "last_week": forks_last_week,
        }
        if forks_this_week - forks_last_week:
            ORG_REPORT_JSON[org]["data"]["forkCount"]["diff_breakdown"] = {
                repo: forks_this_week - forks_last_week
            }


    # Grouping similar metrics
    for metric in ["issues", "openIssues", "closedIssues", "pullRequests", "openPullRequests", "mergedPullRequests",
                   "closedPullRequests", "stargazers", "watchers"]:
        metric_this_week = this_week_json[metric]["totalCount"]
        metric_last_week = last_week_json[metric]["totalCount"]
        REPORT_JSON["data"][metric] = {
            "this_week": metric_this_week,
            "last_week": metric_last_week,
        }
        try:
            ORG_REPORT_JSON[org]["data"][metric]["this_week"] += metric_this_week
            ORG_REPORT_JSON[org]["data"][metric]["last_week"] += metric_last_week
            if metric_this_week - metric_last_week:
                ORG_REPORT_JSON[org]["data"][metric]["diff_breakdown"][repo] = metric_this_week - metric_last_week
        except KeyError:
            ORG_REPORT_JSON[org]["data"][metric] = {
                "this_week": metric_this_week,
                "last_week": metric_last_week,
            }
            if metric_this_week - metric_last_week:
                ORG_REPORT_JSON[org]["data"][metric]["diff_breakdown"] = {
                    repo: metric_this_week - metric_last_week
                }


    # Project report diff
    # Org report diff done after the for loop for projects ends
    for metric in REPORT_JSON["data"]:
        REPORT_JSON["data"][metric]["diff"] = REPORT_JSON["data"][metric]["this_week"] - REPORT_JSON["data"][metric]["last_week"]

    with open("{}/{}.json".format(project, REPORT_JSON["reportID"]), "w+") as f:
        json.dump(REPORT_JSON, f)
    print("LOG: Wrote REPORT to", "{}/{}.json".format(project, REPORT_JSON["reportID"]))


    # Create .md file in _posts with datestamp
    post_text = """\
    ---
    layout: weekly-metrics-v{version}
    title: TwiterOSS Metrics Report for {owner}/{repo} | {reportID}
    permalink: /{owner}/{repo}/{link}/

    owner: {owner}
    repo: {repo}
    reportID: {reportID}
    datestampThisWeek: {datestampThisWeek}
    datestampLastWeek: {datestampLastWeek}
    ---

    <table style="width: 100%">
        <tr>
            <th>Metric</th>
            <th>This Week</th>
            <th>Last Week</th>
            <th>+/-</th>
        </tr>
        {{% for item in site.data["{owner_in_data}"]["{repo_in_data}"]["{reportID}"]["data"] %}}
        <tr>
            <th>{{{{ item[0] }}}}</th>
            <th>{{{{ item[1]["this_week"] }}}}</th>
            <th>{{{{ item[1]["last_week"] }}}}</th>
            <th>{{{{ item[1]["diff"] }}}}</th>
        </tr>
        {{% endfor %}}
    </table>

    """

    normal_post_text = post_text.format(
        version=WEEKLY_METRICS_VERSION,
        owner=org,
        owner_in_data=org.replace('.', ''),  # Dots confused jekyll
        repo=repo,
        repo_in_data=repo.replace('.', ''),
        reportID=REPORT_JSON["reportID"],
        datestampThisWeek=REPORT_JSON["datestamp"]["this_week"],
        datestampLastWeek=REPORT_JSON["datestamp"]["last_week"],
        link=REPORT_JSON["reportID"])

    latest_post_text = post_text.format(
        version=WEEKLY_METRICS_VERSION,
        owner=org,
        owner_in_data=org.replace('.', ''),
        repo=repo,
        repo_in_data=repo.replace('.', ''),
        reportID=REPORT_JSON["reportID"],
        datestampThisWeek=REPORT_JSON["datestamp"]["this_week"],
        datestampLastWeek=REPORT_JSON["datestamp"]["last_week"],
        link="WEEKLY")


    # Create directory for the post, if it does not exist
    path_to_post = PATH_TO_METRICS_POSTS + "/" + REPORT_JSON["nameWithOwner"]
    os.makedirs(path_to_post, exist_ok=True)

    # This is a weird filename for sure. But I think I have an explanation for it -
    # posts need to start with %Y-%m-%d and the later is sent to page.title variable
    # Without the later date, title did not make much sense.
    normal_post_file = "{}/{}-{}.md".format(path_to_post, REPORT_JSON["datestamp"]["this_week"], REPORT_JSON["reportID"])
    with open(normal_post_file, "w+") as f:
        f.write(textwrap.dedent(normal_post_text))
    print("LOG: Created a POST", normal_post_file)

    # Delete already existing latest posts
    re_latest_report = re.compile(r"\d{4}-\d{2}-\d{2}-WEEKLY-LATEST.md")
    for filename in os.listdir(path_to_post):
        if re_latest_report.match(filename):
            print("LOG: Removing existing latest post", os.path.join(path_to_post, filename))
            os.unlink(os.path.join(path_to_post, filename))

    # Create latest report file in _posts as well
    latest_post_file = "{}/{}-WEEKLY-LATEST.md".format(path_to_post, REPORT_JSON["datestamp"]["this_week"])
    with open(latest_post_file, "w+") as f:
        f.write(textwrap.dedent(latest_post_text))
    print("LOG: Created the latest POST", latest_post_file)

"""
Get the diff of each data metric
"""
for org in ORG_REPORT_JSON:
    for metric in ORG_REPORT_JSON[org]["data"]:
        ORG_REPORT_JSON[org]["data"][metric]["diff"] = ORG_REPORT_JSON[org]["data"][metric]["this_week"] - ORG_REPORT_JSON[org]["data"][metric]["last_week"]

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
    layout: org-weekly-metrics-v{version}
    title: TwiterOSS Metrics Report for {org} | {reportID}
    permalink: /{org}/{link}/

    org: {org}
    reportID: {reportID}
    datestampThisWeek: {datestampThisWeek}
    datestampLastWeek: {datestampLastWeek}
    ---

    <table style="width: 100%">
        <tr>
            <th>Metric</th>
            <th>This Week</th>
            <th>Last Week</th>
            <th>+/-</th>
        </tr>
        {{% for item in site.data["{org_in_data}"]["{reportID}"]["data"] %}}
        <tr>
            <th>{{{{ item[0] }}}}</th>
            <th>{{{{ item[1]["this_week"] }}}}</th>
            <th>{{{{ item[1]["last_week"] }}}}</th>
            <th>{{{{ item[1]["diff"] }}}}</th>
        </tr>
        {{% endfor %}}
    </table>

    """

    normal_post_text = post_text.format(
        version=ORG_WEEKLY_METRICS_VERSION,
        org=org,
        org_in_data=org.replace('.', ''),
        reportID=REPORT_JSON["reportID"],
        datestampThisWeek=REPORT_JSON["datestamp"]["this_week"],
        datestampLastWeek=REPORT_JSON["datestamp"]["last_week"],
        link=REPORT_JSON["reportID"])

    latest_post_text = post_text.format(
        version=ORG_WEEKLY_METRICS_VERSION,
        org=org,
        org_in_data=org.replace('.', ''),
        reportID=REPORT_JSON["reportID"],
        datestampThisWeek=REPORT_JSON["datestamp"]["this_week"],
        datestampLastWeek=REPORT_JSON["datestamp"]["last_week"],
        link="WEEKLY")


    # Create directory for the post, if it does not exist
    path_to_post = PATH_TO_METRICS_POSTS + "/" + org
    os.makedirs(path_to_post, exist_ok=True)

    # This is a weird filename for sure. But I think I have an explanation for it -
    # posts need to start with %Y-%m-%d and the later is sent to page.title variable
    # Without the later date, title did not make much sense.
    normal_post_file = "{}/{}-{}.md".format(path_to_post, ORG_REPORT_JSON[org]["datestamp"]["this_week"], ORG_REPORT_JSON[org]["reportID"])
    with open(normal_post_file, "w+") as f:
        f.write(textwrap.dedent(normal_post_text))
    print("LOG: Created a POST", normal_post_file)

    # Delete already existing latest posts
    re_latest_report = re.compile(r"\d{4}-\d{2}-\d{2}-WEEKLY-LATEST.md")
    for filename in os.listdir(path_to_post):
        if re_latest_report.match(filename):
            print("LOG: Removing existing latest post", os.path.join(path_to_post, filename))
            os.unlink(os.path.join(path_to_post, filename))

    # Create latest report file in _posts as well
    latest_post_file = "{}/{}-WEEKLY-LATEST.md".format(path_to_post, ORG_REPORT_JSON[org]["datestamp"]["this_week"])
    with open(latest_post_file, "w+") as f:
        f.write(textwrap.dedent(latest_post_text))
    print("LOG: Created the latest POST", latest_post_file)
