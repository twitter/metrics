---
layout: monthly-metrics-v0.1
title: TwiterOSS Metrics Report for twitter/plumage.js | MONTHLY-2018-07-27 | 2018-07-27
permalink: /twitter/plumage.js/MONTHLY/

owner: twitter
repo: plumage.js
reportID: MONTHLY-2018-07-27
datestampThisMonth: 2018-07-27
datestampLastMonth: 2018-06-29
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Month</th>
        <th>Last Month</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitter"]["plumagejs"]["MONTHLY-2018-07-27"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_month"] }}</th>
        <th>{{ item[1]["last_month"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

