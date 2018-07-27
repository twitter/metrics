---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for twitterdev/live-event-android | WEEKLY-2018-07-27
permalink: /twitterdev/live-event-android/WEEKLY/

owner: twitterdev
repo: live-event-android
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
    {% for item in site.data["twitterdev"]["live-event-android"]["WEEKLY-2018-07-27"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

