---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for twitter/ios-twitter-logging-service | WEEKLY-2018-07-16
permalink: /twitter/ios-twitter-logging-service/WEEKLY/

owner: twitter
repo: ios-twitter-logging-service
reportID: WEEKLY-2018-07-16
datestampThisWeek: 2018-07-16
datestampLastWeek: 2018-07-06
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitter"]["ios-twitter-logging-service"]["WEEKLY-2018-07-16"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

