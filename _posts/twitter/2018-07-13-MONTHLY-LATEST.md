---
layout: org-monthly-metrics-v0.1
title: TwiterOSS Metrics Report for twitter | MONTHLY-2018-07-13
permalink: /twitter/MONTHLY/

org: twitter
reportID: MONTHLY-2018-07-13
datestampThisMonth: 2018-07-13
datestampLastMonth: 2018-06-20
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Month</th>
        <th>Last Month</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitter"]["MONTHLY-2018-07-13"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_month"] }}</th>
        <th>{{ item[1]["last_month"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

