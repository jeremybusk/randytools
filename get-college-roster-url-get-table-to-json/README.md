# README

## Update xlsx Roster URLs

### Steps

```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

edit config.yaml

Note you can input or output to csv or xlsx files based on .csv or .xlsx file extension in config


Download xslx file to say teams.xlsx with header/data format like below:

ID      School  Conference      Roster URL      Website Host

```
ID|School|Conference|Roster URL|Website Host
14|Boston College|ACC|https://bceagles.com/sports/football/roster	
18|California|ACC|https://calbears.com/sports/football/roster	
```

Run update
```
python3 update-xlsx-roster-urls-get-rosters-to-json.py

```

This get's most URLs but you may have to manually get blank ones unless you want to use different search or use api service

If URL doesn't exist it will not be able to scrape and output json file for that college roster

Roster json will be outputed on a per college basis like so

BYU.roster.out.json
Georgia_Tech.roster.out.json

If you enable diff only it will only report diffs to the diff_report_file.

diff only example config
```
input_file: "teams.csv"
output_file: "teams_updated.xlsx"
csv_delimiter: "|"
match_pattern: "(?i)name|player|number"
search_suffix: "/roster"
skip_existing: true
diff_only: false
diff_report_file: "diff-report.json"
```


## Other Options

In old/uri-table-scraper directory I added an example of using playwright that might be more helpful at times when parsing rendered html tables isn't good enough.
