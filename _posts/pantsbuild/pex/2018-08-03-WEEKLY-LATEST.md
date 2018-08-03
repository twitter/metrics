---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for pantsbuild/pex | WEEKLY-2018-08-03
permalink: /pantsbuild/pex/WEEKLY/

owner: pantsbuild
repo: pex
reportID: WEEKLY-2018-08-03
datestampThisWeek: 2018-08-03
datestampLastWeek: 2018-07-27
---

<table style="width: 100%">
    <tr>
        <th>Metric</th>
        <th>This Week</th>
        <th>Last Week</th>
        <th>+/-</th>
    </tr>
    {% for item in site.data["pantsbuild"]["pex"]["WEEKLY-2018-08-03"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

