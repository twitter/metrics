---
layout: monthly-metrics-v0.1
title: Metrics report for twitter/gatekeeper-service | MONTHLY-2018-07-20 | 2018-07-20
permalink: /twitter/gatekeeper-service/MONTHLY/

owner: twitter
repo: gatekeeper-service
reportID: MONTHLY-2018-07-20
datestampThisMonth: 2018-07-20
datestampLastMonth: 2018-06-22
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Month</th>
        <th>Last Month</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitter"]["gatekeeper-service"]["MONTHLY-2018-07-20"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["latest"] }}</th>
        <th>{{ item[1]["previous"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>
