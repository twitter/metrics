"""
This script creates various graphs using the metrics data available.
"""
from glob import glob
import datetime
import operator
import os
import json

import pygal

import util

PATH_TO_METRICS_DATA = "_data"
PATH_TO_GRAPHS = "graphs"
PATH_TO_METADATA = "_metadata"

with open(os.path.join(PATH_TO_METADATA, "projects_tracked.json")) as f:
    PROJECTS_TRACKED = json.load(f)

"""
Generate graphs for all Orgs
"""
ALL_ORGS = PROJECTS_TRACKED["orgs"]


def create_dateline(timeseries, plot_name="", as_title=False):
    """
    timeseries: A list of tuples. Tuple : (datetime object, integer)
    Should either be in increasing or decreasing order
    """
    if as_title:
        dateline = pygal.DateTimeLine(x_label_rotation=25,
                                      x_value_formatter=lambda dt: dt.strftime('%b %Y'),
                                      title=plot_name)
    else:
        dateline = pygal.DateTimeLine(x_label_rotation=25,
                                      x_value_formatter=lambda dt: dt.strftime('%b %Y'))

    # Calculate x_labels
    x_labels = []

    months_span = abs((timeseries[-1][0] - timeseries[0][0]).days//30) + 1
    # print(months_span)
    start_date = min(timeseries[0][0], timeseries[-1][0])
    x_labels.append(start_date)
    _next_date = start_date
    for _ in range(months_span):
        _next_date += datetime.timedelta(days=30)
        x_labels.append(_next_date)

    # More than 10 x_labels gets hard to read, so space them out
    if len(x_labels) > 10:
        new_x_labels = []
        new_x_labels.append(x_labels[0])

        jump_length = (len(x_labels) - 2)//(10 - 2) # Two fixed labels are the first and last
        index = jump_length + 1
        while(index < len(x_labels) - 1):
            new_x_labels.append(x_labels[index])
            index += jump_length

        new_x_labels.append(x_labels[-1])

        dateline.x_labels = new_x_labels
    else:
        dateline.x_labels = x_labels

    if as_title:
        dateline.add("", timeseries)
    else:
        dateline.add(plot_name, timeseries)

    return dateline



for org in ALL_ORGS:
    all_weekly_metrics_files = glob(f"{PATH_TO_METRICS_DATA}/{org}/WEEKLY-REPORT-*.json")
    all_monthly_metrics_files = glob(f"{PATH_TO_METRICS_DATA}/{org}/MONTHLY-REPORT-*.json")

    all_weekly_metrics_files.sort()  # Important to sort by date in increasing order

    orgname = org.split("/")[-1]

    """
    Create timeseries of all the data for the org
    """
    print(f"Creating timeseries of all the github metrics for {org}")
    timeseries = {}
    timeseries['no_of_repos'] = []
    timeseries['forkCount'] = []
    timeseries['issues'] = []
    timeseries['openIssues'] = []
    timeseries['closedIssues'] = []
    timeseries['pullRequests'] = []
    timeseries['openPullRequests'] = []
    timeseries['mergedPullRequests'] = []
    timeseries['closedPullRequests'] = []
    timeseries['stargazers'] = []
    timeseries['watchers'] = []

    for file in all_weekly_metrics_files:
        with open(file) as f:
            data = json.load(f)
        # try/except because the data format changed for weekly reports
        try:
            y, m, d = data['datestamp']['latest'].split('-')
        except KeyError:
            y, m, d = data['datestamp']['this_week'].split('-')
        date_obj = datetime.date(int(y), int(m), int(d))

        no_of_repos = data['no_of_repos']
        timeseries['no_of_repos'].append((date_obj, no_of_repos))

        for metric in ['forkCount', 'issues', 'openIssues', 'closedIssues',
                       'pullRequests', 'openPullRequests', 'mergedPullRequests',
                       'closedPullRequests', 'stargazers', 'watchers']:
            try:
                count = data['data'][metric]['latest']
            except KeyError:
                count = data['data'][metric]['this_week']
            timeseries[metric].append((date_obj, count))

    # Save the SVG images
    for metric in timeseries:
        plot_name = util.get_metrics_name(metric)
        dateline = create_dateline(timeseries[metric], plot_name=plot_name)

        file_path = "{}/{}/timeseries_{}.svg".format(PATH_TO_GRAPHS, orgname, metric)
        os.makedirs("{}/{}".format(PATH_TO_GRAPHS, orgname), exist_ok=True)

        dateline.render_to_file(file_path)

    """
    Create Binary Tree map for breakdowns
    ORG - WEEKLY and ORG - MONTHLY
    """
    latest_weekly_report = json.load(open(all_weekly_metrics_files[-1]))
    print(f"Creating weekly binary tree map of breakdowns for {org}")
    for metric in latest_weekly_report["data"]:
        treemap = pygal.Treemap()

        treemap.title = util.get_metrics_name(metric)

        # Add blocks in decreasing order of their count
        items = list(latest_weekly_report["data"][metric]["diff_breakdown"].items())
        items.sort(key=operator.itemgetter(1), reverse=True)

        if len(items):
            for item, value in items:
                if value > 0:
                    treemap.add(item, [value])
            file_path = "{}/{}/treemap_weekly_{}.svg".format(PATH_TO_GRAPHS, orgname, metric)
            os.makedirs("{}/{}".format(PATH_TO_GRAPHS, orgname), exist_ok=True)
            treemap.render_to_file(file_path)

    print(f"Creating monthly binary tree map of breakdowns for {org}")
    latest_monthly_report = json.load(open(all_weekly_metrics_files[-1]))
    for metric in latest_monthly_report["data"]:
        treemap = pygal.Treemap()

        treemap.title = util.get_metrics_name(metric)

        # Add blocks in decreasing order of their count
        items = list(latest_monthly_report["data"][metric]["diff_breakdown"].items())
        items.sort(key=operator.itemgetter(1), reverse=True)

        if len(items):
            for item, value in items:
                if value > 0:
                    treemap.add(item, [value])
            file_path = "{}/{}/treemap_monthly_{}.svg".format(PATH_TO_GRAPHS, orgname, metric)
            os.makedirs("{}/{}".format(PATH_TO_GRAPHS, orgname), exist_ok=True)
            treemap.render_to_file(file_path)


"""
Timeseries of new watchers
PROJECT - WEEKLY and PROJECT - MONTHLY
"""
path_to_dir = f"{PATH_TO_METADATA}/augur/timeseries_new_watchers"
for org in PROJECTS_TRACKED["projects"]:
    for repo in PROJECTS_TRACKED["projects"][org]:
        data_file_path = f"{path_to_dir}/{org}/{repo}/data.json"
        graph_dir_path = f"{PATH_TO_GRAPHS}/{org}/{repo}"
        os.makedirs(graph_dir_path, exist_ok=True)

        graph_file_path_per_week = f"{graph_dir_path}/timeseries_new_watchers_per_week.svg"
        graph_file_path_per_month = f"{graph_dir_path}/timeseries_new_watchers_per_month.svg"


        try:
            with open(data_file_path) as f:
                timeseries_new_watchers = json.load(f)
        except Exception as e:
            print(f"Got exception while opening {data_file_path} : {e}")
            continue

        print(f"Creating timeseries of new watchers for {org}/{repo}")

        data_dateline_per_week = []
        data_dateline_per_month = []
        for item in timeseries_new_watchers:
            date_obj = datetime.datetime.strptime(item["date"], "%Y-%m-%d")

            count_per_week = item["count_per_week"]
            data_dateline_per_week.append((date_obj, count_per_week))

            count_per_month = item["count_per_month"]
            data_dateline_per_month.append((date_obj, count_per_month))

        try:
            dateline_per_week = create_dateline(data_dateline_per_week, "Rate of new Watchers per week", as_title=True)
            dateline_per_week.render_to_file(graph_file_path_per_week)

            dateline_per_month = create_dateline(data_dateline_per_month, "Rate of new Watchers per month", as_title=True)
            dateline_per_month.render_to_file(graph_file_path_per_month)
        except Exception as e:
            print(f"Error in {org}/{repo} - {e}")
            print(data_dateline_per_week)
            print(data_dateline_per_month)
