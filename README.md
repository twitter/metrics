# TwitterOSS Metrics
This document is available at [go/runbook/oss-metrics](http://go/runbook/oss-metrics)
# General

This is the README for the TwitterOSS Metrics repo, which generates periodic reports based on the health of Twitter Open Source projects.  

For more info, see [twitter.github.io/metrics](https://twitter.github.io/metrics)

# Contact Information
| Contact Method      | Details              |   |   |   |
|---------------------|----------------------|---|---|---|
| Non-Emergency Email | oss-team@twitter.com |   |   |   |
| Slack Channel       | #open-source         |   |   |   |
| Help Desk           | [go/oss-help](http://go/oss-help)   |   |   |   |


# Dependencies
| Service            | Details                                                                                                  |
|--------------------|----------------------------------------------------------------------------------------------------------|
| [CHAOSS Augur](https://chaoss.community/)       | Used to retrieve metrics such as Aggregate Summary, Bus Factor, and Repo Commits.                         |
| [TravisCI](https://docs.travis-ci.com/user/cron-jobs/)           | Runs a weekly cron job that runs scripts in order to fetch data and generate reports.                     |
| [GraphQL](https://graphql.github.io/)           | Directly used to fetch metrics from the GitHub GraphQL API.                                               |
| [Twitter Service](https://github.com/twitter-service)    | Indirectly used for personal access token environment variable.                                           |
| [Metrics Dashboard](https://twitter.github.io/metrics/)  | Contains all reports for Repositories in repos-to-include.txt.                                            |
| [Slack reports Repo](https://github.com/twitter/chatops) | Runs a cron job and posts a message to slack with daily project activity based on metrics repo.           |
| [Year In Review](https://twitter.github.io/year-in-review)     | Weekly updating, sliding window overview of past 12 months of activity on Twitter's Open Source Projects. |


# Service Outage Impact 

If the service experiences problems:

* Year in Review, Metrics Dashboard, and Slack Reports Repo will be unable to update.


# Build
## Environment Setup
1. Clone Repo  
    ```bash
    $ git clone https://github.com/twitter/metrics.git  
    $ cd ./metrics
    ```
#### Note
For this to work, You need to be in oss-github role.

## Tracking new repositories and orgs

Edit `repos-to-include.md`

If you want to track an org and all its repositories which are hosted `github.com/<org_name>`,
add `<org_name>/*` as a new line in `repos-to-include.md`.
If you want to track some and not all repositories of an org, add `<org_name>/<repo_name>` as new lines for each public repo in `repos-to-include.md`.

## Run The Scripts

`$ python scripts/fetch_all_metrics.py`
   
  - Reads all the repositories and orgs listed in `repos-to-include.md`
  - Requests GitHub GraphQL API
  - Creates one JSON file for each repository with format `METRICS-YYYY-MM-DD.json`
  - Saves the file inside `_data/<owner>/<repo>/`

`$ python scripts/fetch_year_in_review.py`

  - Hits [aggregate_summary](http://apidocs.newtwitter.augurlabs.io/#api-Experimental-aggregate_summary_repo_group) endpoint
  - Creates one JSON file that includes the metrics from the endpoint (watchers, stars, counts, merged PRs, committers,           commits)
  - Saves the file inside `_metadata/augur/`
  
`$ python scripts/gen_weekly_report.py`
  
  - Iterates over every project listed inside `_data`
  - Picks the latest two Metrics which are atleast 6 days apart
  - Generates a Report based on these two Metrics files
  - Saves the json inside `_data` directory corresponding to each project, format `WEEKLY-YYYY-MM-DD.json`
  - Creates a `_post` for this report with some specific variables and the layout version


## Additional Notes
- Travis Config

  - Environment variables
    
    - `OAUTH_TOKEN`: Personal Access Token with `repo` access of a GitHub account. This project uses [Twitter Service](https://github.com/twitter-service)
    - `GH_USERNAME`: Username of the GitHub account.
    - (Optional) `SLACK_TOKEN`: Slack token to receive Travis build notification on Slack. Remove it from `.travis.yml` if you do not need it.  

- Use Python 3.
- `_data` contains all the data files
- Files in `_posts` leverage `_layouts` and `_data` and generate HTML files
- Don't change html files inside layouts. Create new layouts with new version.
- Maintain versions of metrics layouts (See `METRICS_VERSION` inside the script to generate reports. Also create a new `_layout` for each metrics version). If you add more data, the new posts should be on a new version (which wouldn't break previous pages)
- Use `repos-to-include.md` and `repos-to-exlude.md` files to add org/repository for respective purposes.
- Prepend `{{ site.url }}{{ site.baseurl }}` and use relative URLs
  - e.g. `{{ site.url }}{{ site.baseurl }}/css/main.css`
- Execute all the scripts from the home of the directory. e.g. `python3 scripts/fetch_all_metrics.py`
