# TwitterOSS Metrics

[twitter.github.io/metrics](https://twitter.github.io/metrics)

Generating periodic reports based on the Twitter Open Source metrics.

# Usage

Go to twitter.github.io/metrics and choose a project/org.

# [WIP] How to add new repositories and orgs?

If you want to track an org and all its repositories which are hosted `github.com/<org_name>`,
add `<org_name>/*` as a new line in `repos_to_include.md`.
If you want to track some and not all repositories of an org, add `<org_name>/<repo_name>` as new lines for each public repo in `repos_to_include.md`.

## Notes
- `_data` contains all the data files
- Files `_posts` in posts leverage `_layouts` and `_data` and generate HTML files
- Maintain versions of metrics layouts. If you add more data, the new posts should be on a new version (which wouldn't break previous pages)
- By default, the metrics are generated for all twitter/* repositories. Use `repos-to-include.md` and `repos-to-exlude.md` files to add repository for respective purposes.
- Prepend `{{ site.url }}{{ site.baseurl }}` and use relative URLs
  - e.g. `{{ site.url }}{{ site.baseurl }}/css/main.css`
- Execute all the scripts from the home of the directory. e.g. `python3 scripts/fetch_all_repos.py`
- 
