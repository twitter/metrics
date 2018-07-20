---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for twitterdev/twitter-ruby-ads-sdk | WEEKLY-2018-07-20
permalink: /twitterdev/twitter-ruby-ads-sdk/WEEKLY/

owner: twitterdev
repo: twitter-ruby-ads-sdk
reportID: WEEKLY-2018-07-20
datestampThisWeek: 2018-07-20
datestampLastWeek: 2018-07-13
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["twitterdev"]["twitter-ruby-ads-sdk"]["WEEKLY-2018-07-20"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

