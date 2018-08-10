---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for twitter/twitter-korean-text | WEEKLY-2018-08-10
permalink: /twitter/twitter-korean-text/WEEKLY/

owner: twitter
repo: twitter-korean-text
reportID: WEEKLY-2018-08-10
datestampThisWeek: 2018-08-10
datestampLastWeek: 2018-08-03
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitter"]["twitter-korean-text"]["WEEKLY-2018-08-10"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

