---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for twitter/twemoji | WEEKLY-2018-07-13
permalink: /twitter/twemoji/WEEKLY/

owner: twitter
repo: twemoji
reportID: WEEKLY-2018-07-13
datestampThisWeek: 2018-07-13
datestampLastWeek: 2018-07-06
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitter"]["twemoji"]["WEEKLY-2018-07-13"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

