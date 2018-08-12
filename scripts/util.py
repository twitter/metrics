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
