---
layout: monthly-metrics-v0.1
title: TwiterOSS Metrics Report for twitter/typeahead.js | MONTHLY-2018-07-20 | 2018-07-20
permalink: /twitter/typeahead.js/MONTHLY/

owner: twitter
repo: typeahead.js
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
    {% for item in site.data["twitter"]["typeahead.js"]["MONTHLY-2018-07-20"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_month"] }}</th>
        <th>{{ item[1]["last_month"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

