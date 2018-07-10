---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for twitterdev/python-enterprise-scripts | WEEKLY-2018-07-10
permalink: /twitterdev/python-enterprise-scripts/WEEKLY

owner: twitterdev
repo: python-enterprise-scripts
reportID: WEEKLY-2018-07-10
datestampThisWeek: 2018-07-10
datestampLastWeek: 2018-06-29
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitterdev"]["python-enterprise-scripts"]["WEEKLY-2018-07-10"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

