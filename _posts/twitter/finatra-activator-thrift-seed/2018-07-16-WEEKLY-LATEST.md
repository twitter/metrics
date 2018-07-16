---
layout: weekly-metrics-v0.1
title: TwiterOSS Metrics Report for twitter/finatra-activator-thrift-seed | WEEKLY-2018-07-16
permalink: /twitter/finatra-activator-thrift-seed/WEEKLY/

owner: twitter
repo: finatra-activator-thrift-seed
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
    {% for item in site.data["twitter"]["finatra-activator-thrift-seed"]["WEEKLY-2018-07-16"]["data"] %}
    <tr>
        <th>{{ item[0] }}</th>
        <th>{{ item[1]["this_week"] }}</th>
        <th>{{ item[1]["last_week"] }}</th>
        <th>{{ item[1]["diff"] }}</th>
    </tr>
    {% endfor %}
</table>

