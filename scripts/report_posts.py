import re
import operator
import os
import textwrap

import util

WEEKLY_METRICS_VERSION = "0.1"
ORG_WEEKLY_METRICS_VERSION = "0.1"
MONTHLY_METRICS_VERSION = "0.1"
ORG_MONTHLY_METRICS_VERSION = "0.1"

PATH_TO_METRICS_POSTS = "_posts"

WEEKLY_PROJECT_POST = """\
---
layout: weekly-metrics-v{version}
title: Metrics report for {owner}/{repo} | {reportID}
permalink: /{owner}/{repo}/{link}/

owner: {owner}
repo: {repo}
reportID: {reportID}
datestampThisWeek: {datestampThisWeek}
datestampLastWeek: {datestampLastWeek}
---


"""

MONTHLY_PROJECT_POST = """\
---
layout: monthly-metrics-v{version}
title: Metrics report for {owner}/{repo} | {reportID} | {datestampThisMonth}
permalink: /{owner}/{repo}/{link}/

owner: {owner}
repo: {repo}
reportID: {reportID}
datestampThisMonth: {datestampThisMonth}
datestampLastMonth: {datestampLastMonth}
---

"""
# {{% for item in site.data["{owner_in_data}"]["{repo_in_data}"]["{reportID}"]["data"] %}}


WEEKLY_ORG_POST = """\
---
layout: org-weekly-metrics-v{version}
title: TwiterOSS Metrics Report for {owner} | {reportID}
permalink: /{owner}/{link}/

org: {owner}
reportID: {reportID}
datestampThisWeek: {datestampThisWeek}
datestampLastWeek: {datestampLastWeek}
---

"""
# {{% for item in site.data["{owner_in_data}"]["{reportID}"]["data"] %}}


MONTHLY_ORG_POST = """\
---
layout: org-monthly-metrics-v{version}
title: TwiterOSS Metrics Report for {owner} | {reportID}
permalink: /{owner}/{link}/

org: {owner}
reportID: {reportID}
datestampThisMonth: {datestampThisMonth}
datestampLastMonth: {datestampLastMonth}
---

"""
# {{% for item in site.data["{owner_in_data}"]["{reportID}"]["data"] %}}

def add_table_of_metrics(post_text, REPORT_JSON, data_source, ID, add_breakdown=False):
    # data_source is not used in the function
    # It can be used to create a jekyll loop like below but is being avoided
    # {{% for item in data_source %}}

    post_text += textwrap.dedent("""
    <table class="table table-condensed" style="border-collapse:collapse;">
        <thead>
        <tr>
            <th>Metric</th>
            <th>Latest</th>
            <th>Previous</th>
            <th>+/-</th>
        </tr>
        </thead>
        <tbody>
    """)
    for metric in REPORT_JSON['data']:
        color = util.get_metrics_color(metric, REPORT_JSON['data'][metric]['diff'])
        post_text += """
        <tr data-toggle="collapse" data-target="#col-{5}" class="accordion-toggle" style="cursor: pointer;">
            <td>{0}</td>
            <td>{1}</td>
            <td>{2}</td>
            <td style="color: {4}" >{3}</td>
        </tr>
        """.format(util.get_metrics_name(metric),
                   REPORT_JSON['data'][metric]['latest'],
                   REPORT_JSON['data'][metric]['previous'],
                   REPORT_JSON['data'][metric]['diff'],
                   color,
                   metric)
        # Add diff breakdown
        if add_breakdown and len(REPORT_JSON['data'][metric]['diff_breakdown'].items()):
            post_text += """
            <td class="hiddenRow" colspan="2"></td>
            <td class="hiddenRow" colspan="2" style="padding: 0" ><div class="accordian-body collapse" id="col-{0}">
            """.format(metric)
            items = list(REPORT_JSON['data'][metric]['diff_breakdown'].items())
            items.sort(key=operator.itemgetter(1), reverse=True)
            for item, value in items:
                href = "/metrics/{}/{}/{}".format(REPORT_JSON['name'], item, ID)
                post_text += """<a target="_blank" href="{2}">{0} : {1}</a><br>""".format(item, value, href)
            post_text += """</div> </td>"""
    post_text += textwrap.dedent("""
        </tbody>
    </table>
    """)

    return post_text

def _create_post(REPORT_JSON, latest=False, project=True):
    """
    latest: If True, create a post with permalink /owner/repo/{ID}
    project: If False, it means the post is for an org, else for a project
    """
    ID = REPORT_JSON['reportID'].split('-')[0]

    if project:
        org, repo = REPORT_JSON['nameWithOwner'].split("/")
    else:
        org, repo = REPORT_JSON['name'], ''

    # Create directory for the post, if it does not exist
    path_to_post = os.path.join(PATH_TO_METRICS_POSTS, org, repo)
    os.makedirs(path_to_post, exist_ok=True)

    if latest:
        # Delete already existing latest posts
        re_latest_report = re.compile(r"\d{{4}}-\d{{2}}-\d{{2}}-{}-LATEST.md".format(ID))
        for filename in os.listdir(path_to_post):
            if re_latest_report.match(filename):
                print("LOG: Removing existing latest post", os.path.join(path_to_post, filename))
                os.unlink(os.path.join(path_to_post, filename))


        # Create latest report file in _posts as well
        post_file = "{}/{}-{}-LATEST.md".format(path_to_post, REPORT_JSON["datestamp"]["latest"], ID)
    else:
        # This is a weird filename for sure. But I think I have an explanation for it -
        # posts need to start with %Y-%m-%d and the later is sent to page.title variable
        # Without the later date, title did not make much sense.
        post_file = "{}/{}-{}.md".format(path_to_post, REPORT_JSON["datestamp"]["latest"], REPORT_JSON["reportID"])

    if latest:
        link = ID
    else:
        link = REPORT_JSON["reportID"]

    if ID == "WEEKLY":
        if project:
            data_source = 'site.data["{owner_in_data}"]["{repo_in_data}"]["{reportID}"]["data"]'
            post_text = add_table_of_metrics(WEEKLY_PROJECT_POST, REPORT_JSON, data_source, 'WEEKLY')
        else:
            data_source = 'site.data["{owner_in_data}"]["{reportID}"]["data"]'
            post_text = add_table_of_metrics(WEEKLY_ORG_POST, REPORT_JSON, data_source, 'WEEKLY', add_breakdown=True)
        post_text = post_text.format(
            version=WEEKLY_METRICS_VERSION,
            owner=org,
            owner_in_data=org.replace('.', ''), # Dots confused jekyll
            repo=repo,
            repo_in_data=repo.replace('.', ''),
            reportID=REPORT_JSON["reportID"],
            datestampThisWeek=REPORT_JSON["datestamp"]["latest"],
            datestampLastWeek=REPORT_JSON["datestamp"]["previous"],
            link=link)
    elif ID == "MONTHLY":
        if project:
            data_source = 'site.data["{owner_in_data}"]["{repo_in_data}"]["{reportID}"]["data"]'
            post_text = add_table_of_metrics(MONTHLY_PROJECT_POST, REPORT_JSON, data_source, 'MONTHLY')
        else:
            data_source = 'site.data["{owner_in_data}"]["{reportID}"]["data"]'
            post_text = add_table_of_metrics(MONTHLY_ORG_POST, REPORT_JSON, data_source, 'MONTHLY', add_breakdown=True)
        post_text = post_text.format(
            version=MONTHLY_METRICS_VERSION,
            owner=org,
            owner_in_data=org.replace('.', ''),  # Dots confused jekyll
            repo=repo,
            repo_in_data=repo.replace('.', ''),
            reportID=REPORT_JSON["reportID"],
            datestampThisMonth=REPORT_JSON["datestamp"]["latest"],
            datestampLastMonth=REPORT_JSON["datestamp"]["previous"],
            link=link)

    with open(post_file, "w+") as f:
        f.write(post_text)
    if latest:
        print("LOG: Created the latest POST", post_file)
    else:
        print("LOG: Created the POST", post_file)

def create_posts(REPORT_JSON, project=True):
    _create_post(REPORT_JSON, latest=False, project=project)
    _create_post(REPORT_JSON, latest=True, project=project)
