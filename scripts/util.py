"""
Utility functions or data required by the scripts
"""

def get_metrics_name(code):
    try:
        return METRICS_CODE_TO_NAME[code]
    except KeyError:
        return code

METRICS_CODE_TO_NAME = {
    'commits': 'Commits',
    'forkCount': 'Forks',
    'issues': 'Issues',
    'openIssues': 'Open Issues',
    'closedIssues': 'Closed Issues',
    'pullRequests': 'Pull Requests',
    'openPullRequests': 'Open Pull Requests',
    'mergedPullRequests': 'Merged Pull Requests',
    'closedPullRequests': 'Closed Pull Requests',
    'stargazers': 'Stars',
    'watchers': 'Watchers',

    'no_of_repos': 'No. of Projects',
}


GREEN = "#45c527"
RED = "#d31c08"
DEFAULT = ""
METRICS_HEALTHY_TREND = {
    'commits': '+',
    'forkCount': '+',
    'issues': '+',
    'openIssues': '-',
    'closedIssues': '+',
    'pullRequests': '+',
    'openPullRequests': '-',
    'mergedPullRequests': '+',
    'closedPullRequests': '+',
    'stargazers': '+',
    'watchers': '+',
    'no_of_repos': '+',
}

def get_metrics_color(metric, diff):
    if diff == 0:
        return GREEN
    elif METRICS_HEALTHY_TREND[metric] == '+' and diff > 0:
        return GREEN
    elif METRICS_HEALTHY_TREND[metric] == '-' and diff < 0:
        return GREEN
    else:
        return RED
