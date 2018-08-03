---
layout: monthly-metrics-v0.1
title: TwiterOSS Metrics Report for twitterdev/django-rest-apis | MONTHLY-2018-08-03 | 2018-08-03
permalink: /twitterdev/django-rest-apis/MONTHLY/

owner: twitterdev
repo: django-rest-apis
reportID: MONTHLY-2018-08-03
datestampThisMonth: 2018-08-03
datestampLastMonth: 2018-07-06
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Month</th>
        <th>Last Month</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitterdev"]["django-rest-apis"]["MONTHLY-2018-08-03"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_month"] }}</th>
        <th>{{ item[1]["last_month"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

