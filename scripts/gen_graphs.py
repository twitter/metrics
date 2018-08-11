"""
This script creates various graphs using the metrics data available.
"""
from glob import glob
import datetime
import operator
import os
import json

import pygal

PATH_TO_METRICS_DATA = "_data"
# PATH_TO_GRAPHS = os.path.abspath(os.curdir) + "/graphs"
PATH_TO_GRAPHS = "graphs"

"""
Generate graphs for all Orgs
"""
ALL_ORGS = filter(os.path.isdir, glob(PATH_TO_METRICS_DATA + "/*"))

for org in ALL_ORGS:
    all_metrics_files = glob(org + "/WEEKLY-*.json")
    all_metrics_files.sort()  # Important to sort by date in increasing order

    orgname = org.split("/")[-1]

    # Create timeseries of all the data for the org
    # In future if more metrics are added, use try/catch to escape the errors in older files
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

    for file in all_metrics_files:
        data = json.load(open(file))
        y, m, d = data['datestamp']['this_week'].split('-')
        date_obj = datetime.date(int(y), int(m), int(d))

        no_of_repos = data['no_of_repos']
        timeseries['no_of_repos'].append((date_obj, no_of_repos))

        forkCount = data['data']['forkCount']['this_week']
        timeseries['forkCount'].append((date_obj, forkCount))

        issues = data['data']['issues']['this_week']
        timeseries['issues'].append((date_obj, issues))

        openIssues = data['data']['openIssues']['this_week']
        timeseries['openIssues'].append((date_obj, openIssues))

        closedIssues = data['data']['closedIssues']['this_week']
        timeseries['closedIssues'].append((date_obj, closedIssues))

        pullRequests = data['data']['pullRequests']['this_week']
        timeseries['pullRequests'].append((date_obj, pullRequests))

        openPullRequests = data['data']['openPullRequests']['this_week']
        timeseries['openPullRequests'].append((date_obj, openPullRequests))

        mergedPullRequests = data['data']['mergedPullRequests']['this_week']
        timeseries['mergedPullRequests'].append((date_obj, mergedPullRequests))

        closedPullRequests = data['data']['closedPullRequests']['this_week']
        timeseries['closedPullRequests'].append((date_obj, closedPullRequests))

        stargazers = data['data']['stargazers']['this_week']
        timeseries['stargazers'].append((date_obj, stargazers))

        watchers = data['data']['watchers']['this_week']
        timeseries['watchers'].append((date_obj, watchers))

    # Save the SVG images
    for metric in timeseries:
        dateline = pygal.DateTimeLine(x_label_rotation=25,
                                  x_value_formatter=lambda dt: dt.strftime('%b %Y'))

        # Calculate x_labels
        x_labels = []

        months_span = (timeseries[metric][-1][0] - timeseries[metric][0][0]).days//30 + 1
        start_date = timeseries[metric][0][0]
        x_labels.append(start_date)
        _next_date = start_date
        for _ in range(months_span):
            _next_date += datetime.timedelta(days=30)
            x_labels.append(_next_date)

        dateline.x_labels = x_labels

        dateline.add(metric, timeseries[metric])

        file_path = "{}/{}/timeseries_{}.svg".format(PATH_TO_GRAPHS, orgname, metric)
        os.makedirs("{}/{}".format(PATH_TO_GRAPHS, orgname), exist_ok=True)
        dateline.render_to_file(file_path)

    """
    Create Binary Tree map for breakdowns
    """
    latest_report = json.load(open(all_metrics_files[-1]))
    for metric in latest_report["data"]:
        treemap = pygal.Treemap()
        treemap.title = metric

        # Add blocks in decreasing order of their count
        items = list(latest_report["data"][metric]["diff_breakdown"].items())
        items.sort(key=operator.itemgetter(1), reverse=True)

        if len(items):
            for item, value in items:
                if value > 0:
                    treemap.add(item, [value])
            file_path = "{}/{}/treemap_{}.svg".format(PATH_TO_GRAPHS, orgname, metric)
            os.makedirs("{}/{}".format(PATH_TO_GRAPHS, orgname), exist_ok=True)
            treemap.render_to_file(file_path)


"""
Generate graphs for all Repos
"""
ALL_REPOS = filter(os.path.isdir, glob(PATH_TO_METRICS_DATA + "/*/*"))
# TODO
