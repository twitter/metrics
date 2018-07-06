---
layout: metrics-v0.1
title: TwiterOSS Metrics Report for twitterdev/chrome-extension-tweetbar | WEEKLY-2018-07-06 | 2018-07-06
permalink: /twitterdev/chrome-extension-tweetbar/WEEKLY.html

owner: twitterdev
repo: chrome-extension-tweetbar
reportID: WEEKLY-2018-07-06
datestampThisWeek: 2018-07-06
datestampLastWeek: 2018-06-29
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitterdev"]["chrome-extension-tweetbar"]["WEEKLY-2018-07-06"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

