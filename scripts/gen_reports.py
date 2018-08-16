"""
Create WEEKLY-REPORT-<DATE>.json for all the orgs and projects,
and save then inside _data directory.
Similarly for MONTHLY report as well.
Also call report_posts.py module to create _posts reflecting the reports.
"""

from glob import glob
import datetime
import json
import os
import re

import report_posts

PATH_TO_METRICS_DATA = "_data"
PATH_TO_METRICS_POSTS = "_posts"
WEEKLY_MIN_DIFFERENCE = 6 # In Days
MONTHLY_MIN_DIFFERENCE = 27 # In Days

ALL_PROJECTS = filter(os.path.isdir, glob(PATH_TO_METRICS_DATA + "/*/*"))


def get_metrics_files(project, MIN_DIFFERENCE):
    """
    Return the latest two METRICS-<datestamp>.json files

    project: Path to directory inside _data referring to a project

    returns:
        is_eligible: Permission to create a report for the project
    """
    print("LOG: Starting with", project)

    # Get the latest two metrics for this project which are MIN_DIFFERENCE days apart
    re_metrics = re.compile(r"METRICS-\d{4}-\d{2}-\d{2}.json")
    all_metrics = []

    for filename in os.listdir(project):
        if re_metrics.match(filename):
            all_metrics.append(filename)

    all_metrics.sort()

    # Come back later when there are atleast two generated metrics files
    if len(all_metrics) < 2:
        return False, {}, {}

    current_metrics_json_file = all_metrics.pop()
    print("LOG: Current metrics json file", current_metrics_json_file)

    # If the latest Metrics is older than MIN_DIFFERENCE, then don't generate report
    # This is possible in cases of repo turning private or moving out
    today_datestamp = datetime.datetime.now()
    latest_datestamp = datetime.datetime.strptime(current_metrics_json_file, "METRICS-%Y-%m-%d.json")
    datetime_delta = today_datestamp - latest_datestamp
    if datetime_delta.days > MIN_DIFFERENCE:
        print("Skipping report for", project, "Latest metrics file is older than MIN_DIFFERENCE")
        return False, {}, {}

    previous_metrics_json_file = None
    previous_metrics_index_index = len(all_metrics) - 1
    while(previous_metrics_index_index >= 0):
        # Calculate difference between last two metrics
        d1 = datetime.datetime.strptime(current_metrics_json_file, "METRICS-%Y-%m-%d.json")
        d2 = datetime.datetime.strptime(all_metrics[previous_metrics_index_index], "METRICS-%Y-%m-%d.json")
        if (d1 - d2).days > MIN_DIFFERENCE:
            previous_metrics_json_file = all_metrics[previous_metrics_index_index]
            print("LOG: Previous metrics json", previous_metrics_json_file)
            break
        else:
            previous_metrics_index_index -= 1

    # Metrics are not older than MIN_DIFFERENCE days
    if previous_metrics_json_file is None:
        return False, {}, {}

    return True, current_metrics_json_file, previous_metrics_json_file


def get_modulo_highlights(latest, previous):
    modulo_flag = False
    modulo_number = 0 # The highlight number crossed by the metric

    if latest//100 != previous//100:
        modulo_flag = True
        modulo_number = max(latest, previous) - max(latest, previous)%100
    if latest//1000 != previous//1000:
        modulo_flag = True
        modulo_number = max(latest, previous) - max(latest, previous)%1000
    if latest//10000 != previous//10000:
        modulo_flag = True
        modulo_number = max(latest, previous) - max(latest, previous)%1000

    return modulo_flag, modulo_number


def create_report(latest_metrics, previous_metrics, ORG_REPORT_JSON, ID):
    """
    Create json report for a project
    Add up its metrics to its org
    """
    REPORT_JSON = {}
    REPORT_JSON["nameWithOwner"] = latest_metrics["nameWithOwner"]
    REPORT_JSON["reportID"] = "{}-REPORT-{}".format(ID, latest_metrics["datestamp"])
    REPORT_JSON["datestamp"] = {
        "latest": latest_metrics["datestamp"],
        "previous": previous_metrics["datestamp"]
    }

    org, repo = REPORT_JSON["nameWithOwner"].split("/")

    # Initialize org in org report
    if org not in ORG_REPORT_JSON:
        ORG_REPORT_JSON[org] = {}
        ORG_REPORT_JSON[org]["name"] = org
        ORG_REPORT_JSON[org]["reportID"] = "{}-REPORT-{}".format(ID, latest_metrics["datestamp"])
        ORG_REPORT_JSON[org]["datestamp"] = {
            "latest": latest_metrics["datestamp"],
            "previous": previous_metrics["datestamp"]
        }
        ORG_REPORT_JSON[org]["data"] = {}
        ORG_REPORT_JSON[org]["highlights"] = []

    try:
        ORG_REPORT_JSON[org]["no_of_repos"] += 1
    except KeyError:
        ORG_REPORT_JSON[org]["no_of_repos"] = 1

    REPORT_JSON["data"] = {}

    github_metrics = ["commits",
                      "issues",
                      "openIssues",
                      "closedIssues",
                      "pullRequests",
                      "openPullRequests",
                      "mergedPullRequests",
                      "closedPullRequests",
                      "forkCount",
                      "stargazers",
                      "watchers"]

    for metric in github_metrics:
        REPORT_JSON["data"][metric] = {
            "latest": latest_metrics[metric],
            "previous": previous_metrics[metric],
        }

        try:
            ORG_REPORT_JSON[org]["data"][metric]["latest"] += latest_metrics[metric]
            ORG_REPORT_JSON[org]["data"][metric]["previous"] += previous_metrics[metric]
        except KeyError:
            ORG_REPORT_JSON[org]["data"][metric] = {
                "latest": latest_metrics[metric],
                "previous": previous_metrics[metric],
                "diff_breakdown": {}
            }

        if latest_metrics[metric] - previous_metrics[metric]:
            ORG_REPORT_JSON[org]["data"][metric]["diff_breakdown"][repo] = latest_metrics[metric] - previous_metrics[metric]

    # Project report diff; Org report diff done after the for loop for projects ends
    for metric in REPORT_JSON["data"]:
        REPORT_JSON["data"][metric]["diff"] = REPORT_JSON["data"][metric]["latest"] - REPORT_JSON["data"][metric]["previous"]

    # Highlight if any metric crosses %100, %1000 and %10000!
    for metric in github_metrics:
        modulo_flag, modulo_number = get_modulo_highlights(latest_metrics[metric], previous_metrics[metric])
        if modulo_flag:
            ORG_REPORT_JSON[org]["highlights"].append((REPORT_JSON["nameWithOwner"].split('/')[1], modulo_number, metric))

    return REPORT_JSON


def create_weekly_report_and_posts(project, latest_metrics, previous_metrics, ORG_REPORT_JSON, ID):
    with open(os.path.join(project, latest_metrics)) as f:
        latest_metrics = json.load(f)
    with open(os.path.join(project, previous_metrics)) as f:
        previous_metrics = json.load(f)

    # print(eligible, latest_metrics, previous_metrics)
    REPORT_JSON = create_report(latest_metrics, previous_metrics, ORG_REPORT_JSON, ID)

    report_file = "{}/{}.json".format(project, REPORT_JSON["reportID"])
    with open(report_file, "w+") as f:
        json.dump(REPORT_JSON, f)
    print("LOG: Wrote REPORT to", report_file)

    # Create posts
    report_posts.create_posts(REPORT_JSON, is_project=True)


def create_monthly_report_and_posts(org, ORG_REPORT_JSON):
    path_to_org = os.path.join(PATH_TO_METRICS_DATA, org)
    report_file = "{}/{}.json".format(path_to_org, ORG_REPORT_JSON[org]["reportID"])
    with open(report_file, "w+") as f:
        json.dump(ORG_REPORT_JSON[org], f)
    print("LOG: Wrote REPORT to", report_file)

    report_posts.create_posts(ORG_REPORT_JSON[org], is_project=False)



if __name__ == '__main__':
    """
    The script traverses inside _data/ directory recursively.
    For every project, it picks the latest two METRICS-<datestamp>.json files (more than MIN_DIFFERENCE days apart),
    and generates the weekly report with appropriate number. It also updates the latest-weekly report.
    """
    WEEKLY_ORG_REPORT_JSON = {} # Summed up data for the entire github org
    MONTHLY_ORG_REPORT_JSON = {} # Summed up data for the entire github org

    for project in ALL_PROJECTS:
        print("WEEKLY")
        eligible, latest_metrics, previous_metrics = get_metrics_files(project, WEEKLY_MIN_DIFFERENCE)
        # print(eligible, latest_metrics, previous_metrics)
        if eligible:
            create_weekly_report_and_posts(project, latest_metrics, previous_metrics, WEEKLY_ORG_REPORT_JSON, 'WEEKLY')

        print("MONTHLY")
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
        eligible, latest_metrics, previous_metrics = get_metrics_files(project, MONTHLY_MIN_DIFFERENCE)
        if eligible:
            create_weekly_report_and_posts(project, latest_metrics, previous_metrics, MONTHLY_ORG_REPORT_JSON, 'MONTHLY')

    # ORG
    print("WEEKLY")
    for org in WEEKLY_ORG_REPORT_JSON:
        # Get the diff of each data metric in org
        for metric in WEEKLY_ORG_REPORT_JSON[org]["data"]:
            WEEKLY_ORG_REPORT_JSON[org]["data"][metric]["diff"] = WEEKLY_ORG_REPORT_JSON[org]["data"][metric]["latest"] - WEEKLY_ORG_REPORT_JSON[org]["data"][metric]["previous"]

        create_monthly_report_and_posts(org, WEEKLY_ORG_REPORT_JSON)

    print("MONTHLY")
    for org in MONTHLY_ORG_REPORT_JSON:
        for metric in MONTHLY_ORG_REPORT_JSON[org]["data"]:
            MONTHLY_ORG_REPORT_JSON[org]["data"][metric]["diff"] = MONTHLY_ORG_REPORT_JSON[org]["data"][metric]["latest"] - MONTHLY_ORG_REPORT_JSON[org]["data"][metric]["previous"]

        create_monthly_report_and_posts(org, MONTHLY_ORG_REPORT_JSON)
