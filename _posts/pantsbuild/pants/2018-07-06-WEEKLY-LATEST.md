---
layout: monthly-metrics-v0.1
title: TwiterOSS Metrics Report for pantsbuild/pants | MONTHLY-2018-07-06 | 2018-07-06
permalink: /pantsbuild/pants/MONTHLY.html

owner: pantsbuild
repo: pants
reportID: MONTHLY-2018-07-06
datestampThisMonth: 2018-07-06
datestampLastMonth: 2018-06-25
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Month</th>
        <th>Last Month</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["pantsbuild"]["pants"]["MONTHLY-2018-07-06"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_month"] }}</th>
        <th>{{ item[1]["last_month"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

