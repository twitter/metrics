# TwitterOSS Metrics

## General

This is the README for the TwitterOSS Metrics repo, which generates periodic reports based on the health of Twitter Open Source projects.

For more information, visit [twitter.github.io/metrics](https://twitter.github.io/metrics).

## Dependencies

| Service                                                 | Details                                                                                                                  |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| [CHAOSS Augur](https://chaoss.community/)                  | Used to retrieve metrics such as Aggregate Summary, Bus Factor, and Repo Commits.                                        |
| [GitHub Actions](https://github.com/features/actions)      | Runs a weekly cron job that runs scripts in order to fetch data and generate reports.                                    |
| [GraphQL](https://graphql.github.io/)                      | Used directly to fetch metrics from the GitHub GraphQL API.                                                              |
| [Twitter Service](https://github.com/twitter-service)      | Indirectly used for personal access token environment variable.                                                          |
| [Metrics Dashboard](https://twitter.github.io/metrics/)    | Contains all reports for repositories in repos-to-include.txt.                                                           |
| [Slack Reports Repo](https://github.com/twitter/chatops)   | Runs a cron job and posts a message to Slack with daily project activity based on the metrics repo.                      |
| [Year In Review](https://twitter.github.io/year-in-review) | Provides a weekly updating, sliding window overview of the past 12 months of activity on Twitter's Open Source Projects. |

## Service Outage Impact

If the service experiences problems:

- Year in Review, Metrics Dashboard, and Slack Reports Repo will be unable to update.

## Build

### Environment Setup

1. Clone the Repo:
   ```bash
   $ git clone https://github.com/twitter/metrics.git  
   $ cd ./metrics
   ```

### Tracking new repositories and orgs

Edit `repos-to-include.md`.

To track an org and all its repositories hosted on `github.com/<org_name>`, add `<org_name>/*` as a new line in `repos-to-include.md`. If you want to track specific repositories of an org, add `<org_name>/<repo_name>` as new lines for each public repo in `repos-to-include.md`.

### Run The Scripts

`$ python scripts/fetch_all_metrics.py`

- Reads all the repositories and orgs listed in `repos-to-include.md`.
- Requests the GitHub GraphQL API.
- Creates one JSON file for each repository with the format `METRICS-YYYY-MM-DD.json`.
- Saves the file inside `_data/<owner>/<repo>/`.

`$ python scripts/fetch_year_in_review.py`

- Hits the [aggregate_summary](http://apidocs.newtwitter.augurlabs.io/#api-Experimental-aggregate_summary_repo_group) endpoint.
- Creates one JSON file that includes the metrics from the endpoint (watchers, stars, counts, merged PRs, committers, commits).
- Saves the file inside `_metadata/augur/`.

`$ python scripts/gen_weekly_report.py`

- Iterates over every project listed inside `_data`.
- Picks the latest two metrics files that are at least 6 days apart.
- Generates a report based on these two Metrics files.
- Saves the JSON inside the `_data` directory corresponding to each project with the format `WEEKLY-YYYY-MM-DD.json`.
- Creates a `_post` for this report with specific variables and the layout version.

### Additional Notes

- GitHub Actions Config:

  - Environment variables:
    - `OAUTH_TOKEN`: Personal Access Token with `repo` access for a GitHub account.
    - `GH_USERNAME`: Username of the GitHub account.
- Use Python 3.
- The `_data` directory contains all the data files.
- Files in `_posts` leverage `_layouts` and `_data` to generate HTML files.
- Do not change HTML files inside layouts. Create new layouts with a new version.
- Maintain versions of metrics layouts (See `METRICS_VERSION` inside the script to generate reports). Also, create a new `_layout` for each metrics version. If you add more data, the new posts should be on a new version (which won't break previous pages).
- Use `repos-to-include.md` and `repos-to-exclude.md` files to add org/repository for respective purposes.
- Prepend `{{ site.url }}{{ site.baseurl }}` and use relative URLs. For example, `{{ site.url }}{{ site.baseurl }}/css/main.css`.
- Execute all the scripts from the home directory. For example, `python3 scripts/fetch_all_metrics.py`.
