---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for twitterdev/twitter-stream-globe | WEEKLY-2018-07-27
permalink: /twitterdev/twitter-stream-globe/WEEKLY/

owner: twitterdev
repo: twitter-stream-globe
reportID: WEEKLY-2018-07-27
datestampThisWeek: 2018-07-27
datestampLastWeek: 2018-07-20
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitterdev"]["twitter-stream-globe"]["WEEKLY-2018-07-27"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

