## Notes
- `_data` contains all the data files
- Files `_posts` in posts leverage `_layouts` and `_data` and generate HTML files
- Maintain versions of metrics layouts. If you add more data, the new posts should be on a new version (which wouldn't break previous pages)
- By default, the metrics are generated for all twitter/* repositories. Use `repos-to-include.md` and `repos-to-exlude.md` files to add repository for respective purposes.