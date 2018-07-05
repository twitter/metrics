# TwitterOSS Metrics

[twitter.github.io/metrics](https://twitter.github.io/metrics)

Generating periodic reports based on the Twitter Open Source metrics.

# Usage

Visit twitter.github.io/metrics

# How to track new repositories and orgs?

Ans: `repos-to-include.md`

If you want to track an org and all its repositories which are hosted `github.com/<org_name>`,
add `<org_name>/*` as a new line in `repos-to-include.md`.
If you want to track some and not all repositories of an org, add `<org_name>/<repo_name>` as new lines for each public repo in `repos-to-include.md`.

# How does this thing work?

This repository is integrated with Travis. A [Travis Cron Job](https://docs.travis-ci.com/user/cron-jobs/) is scheduled to run every week.

- `python scripts/fetch_all_repos.py`
   
  - Reads all the repositories and orgs listed in `repos-to-include.md`
  - Requests GitHub GraphQL API
  - Creates one JSON file for each repository with format `METRICS-YYYY-MM-DD.json`
  - Saves the file inside `_data/<owner>/<repo>/`

- `python scripts/gen_weekly_report.py`
  
  - Iterates over every project listed inside `_data`
  - Picks the latest two Metrics which are atleast 6 days apart
  - Generates a Report based on these two Metrics files
  - Saves the json inside `_data` directory corresponding to each project, format `WEEKLY-YYYY-MM-DD.json`
  - Creates a `_post` for this report with some specific variables and the layout version

- Travis Config

  - Environment variables
    
    - `OAUTH_TOKEN`: Personal Access Token with `repo` access of a GitHub account.
    - `GH_USERNAME`: Username of the GitHub account.
    - (Optional) `SLACK_TOKEN`: Slack token to receive Travis build notification on Slack. Remove it from `.travis.yml` if you do not need it.

## Notes
- Use Python 3.
- `_data` contains all the data files
- Files in `_posts` leverage `_layouts` and `_data` and generate HTML files
- Don't change html files inside layouts. Create new layouts with new version.
- Maintain versions of metrics layouts (See `METRICS_VERSION` inside the script to generate reports. Also create a new `_layout` for each metrics version). If you add more data, the new posts should be on a new version (which wouldn't break previous pages)
- Use `repos-to-include.md` and `repos-to-exlude.md` files to add org/repository for respective purposes.
- Prepend `{{ site.url }}{{ site.baseurl }}` and use relative URLs
  - e.g. `{{ site.url }}{{ site.baseurl }}/css/main.css`
- Execute all the scripts from the home of the directory. e.g. `python3 scripts/fetch_all_repos.py`
