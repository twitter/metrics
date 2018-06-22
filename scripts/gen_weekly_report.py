"""
The script traverses inside _data/ directory recursively.
For every project, it picks the latest two METRICS-<datestamp>.json files (more than 6 days apart),
and generates the weekly report with appropriate number. It also updates the latest-weekly report.
"""

from glob import glob
import datetime
import json
import os
import re
import textwrap

PATH_TO_METRICS_REPO = "/Users/hmishra/workspace/twitter/metrics"
PATH_TO_METRICS_DATA = PATH_TO_METRICS_REPO + "/_data"
PATH_TO_METRICS_POSTS = PATH_TO_METRICS_REPO + "/_posts"
MIN_DIFFERENCE = 6 # In Days
METRICS_VERSION = "0.1"

ALL_PROJECTS = glob(PATH_TO_METRICS_DATA + "/*/*")

for project in ALL_PROJECTS:
    print("LOG: Starting with", project)
    files_for_project = os.listdir(project)

    # Get the next report number for WEEKLY-{N}
    new_report_number = 1
    re_weekly_report = re.compile(r"WEEKLY-[0-9]+.json")

    # Get the latest two metrics for this week project which are MIN_DIFFERENCE days apart
    re_metrics = re.compile(r"METRICS-\d{4}-\d{2}-\d{2}.json")
    all_metrics = []

    for filename in files_for_project:
        if re_weekly_report.match(filename):
            new_report_number += 1
        if re_metrics.match(filename):
            all_metrics.append(filename)

    all_metrics.sort()

    # Come back later when there are atleast two generated metrics files
    if len(all_metrics) < 2:
        continue

    this_week_json_file = all_metrics.pop()
    print("LOG: This week json file", this_week_json_file)

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
    REPORT_JSON["reportID"] = "WEEKLY-{}".format(new_report_number)
    REPORT_JSON["datestamp"] = {
        "this_week": this_week_json["datestamp"],
        "last_week": last_week_json["datestamp"]
    }

    REPORT_JSON["data"] = {}
    REPORT_JSON["data"]["commits"] = {
        "this_week": this_week_json["defaultBranchRef"]["target"]["history"]["totalCount"],
        "last_week": last_week_json["defaultBranchRef"]["target"]["history"]["totalCount"],
    }
    REPORT_JSON["data"]["issues"] = {
        "this_week": this_week_json["issues"]["totalCount"],
        "last_week": last_week_json["issues"]["totalCount"],
    }
    REPORT_JSON["data"]["openIssues"] = {
        "this_week": this_week_json["openIssues"]["totalCount"],
        "last_week": last_week_json["openIssues"]["totalCount"],
    }
    REPORT_JSON["data"]["closedIssues"] = {
        "this_week": this_week_json["closedIssues"]["totalCount"],
        "last_week": last_week_json["closedIssues"]["totalCount"],
    }
    REPORT_JSON["data"]["pullRequests"] = {
        "this_week": this_week_json["pullRequests"]["totalCount"],
        "last_week": last_week_json["pullRequests"]["totalCount"],
    }
    REPORT_JSON["data"]["openPullRequests"] = {
        "this_week": this_week_json["openPullRequests"]["totalCount"],
        "last_week": last_week_json["openPullRequests"]["totalCount"],
    }
    REPORT_JSON["data"]["mergedPullRequests"] = {
        "this_week": this_week_json["mergedPullRequests"]["totalCount"],
        "last_week": last_week_json["mergedPullRequests"]["totalCount"],
    }
    REPORT_JSON["data"]["closedPullRequests"] = {
        "this_week": this_week_json["closedPullRequests"]["totalCount"],
        "last_week": last_week_json["closedPullRequests"]["totalCount"],
    }
    REPORT_JSON["data"]["forkCount"] = {
        "this_week": this_week_json["forkCount"],
        "last_week": last_week_json["forkCount"],
    }
    REPORT_JSON["data"]["stargazers"] = {
        "this_week": this_week_json["stargazers"]["totalCount"],
        "last_week": last_week_json["stargazers"]["totalCount"],
    }
    REPORT_JSON["data"]["watchers"] = {
        "this_week": this_week_json["watchers"]["totalCount"],
        "last_week": last_week_json["watchers"]["totalCount"],
    }

    for metric in REPORT_JSON["data"]:
        REPORT_JSON["data"][metric]["diff"] = REPORT_JSON["data"][metric]["this_week"] - REPORT_JSON["data"][metric]["last_week"]

    with open("{}/{}.json".format(project, REPORT_JSON["reportID"]), "w+") as f:
        json.dump(REPORT_JSON, f)
    print("LOG: Wrote REPORT to", "{}/{}.json".format(project, REPORT_JSON["reportID"]))


    # Create .md file in _posts with datestamp
    post_text = """\
    ---
    layout: metrics-v{version}
    title: TwiterOSS Metrics Report for {owner}/{repo} | {reportID} | {datestampThisWeek}
    permalink: /{owner}/{repo}/{reportID}.html

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
        {{% for item in site.data["{owner}"]["{repo}"]["{reportID}"]["data"] %}}
        <tr>
            <th>{{{{ item[0] }}}}</th>
            <th>{{{{ item[1]["this_week"] }}}}</th>
            <th>{{{{ item[1]["last_week"] }}}}</th>
            <th>{{{{ item[1]["diff"] }}}}</th>
        </tr>
        {{% endfor %}}
    </table>

    """.format(version=METRICS_VERSION,
               owner=REPORT_JSON["nameWithOwner"].split("/")[0],
               repo=REPORT_JSON["nameWithOwner"].split("/")[1],
               reportID=REPORT_JSON["reportID"],
               datestampThisWeek=REPORT_JSON["datestamp"]["this_week"],
               datestampLastWeek=REPORT_JSON["datestamp"]["last_week"])

    # Create directory for the post, if it does not exist
    path_to_post = PATH_TO_METRICS_POSTS + "/" + REPORT_JSON["nameWithOwner"]
    os.makedirs(path_to_post, exist_ok=True)

    post_file = "{}/{}-{}.md".format(path_to_post, REPORT_JSON["datestamp"]["this_week"], REPORT_JSON["reportID"])
    with open(post_file, "w+") as f:
        f.write(textwrap.dedent(post_text))
    print("LOG: Created a POST", post_file)

    #TODO: Create latest.md file in _posts as well



