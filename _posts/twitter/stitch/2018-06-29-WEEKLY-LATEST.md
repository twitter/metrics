---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for twitter/stitch | WEEKLY-2018-06-29 | 2018-06-29
permalink: /twitter/stitch/WEEKLY.html

owner: twitter
repo: stitch
reportID: WEEKLY-2018-06-29
datestampThisWeek: 2018-06-29
datestampLastWeek: 2018-06-22
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitter"]["stitch"]["WEEKLY-2018-06-29"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

