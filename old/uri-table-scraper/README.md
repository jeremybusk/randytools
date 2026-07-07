# README

## Scraper examples 

### stdout
```
python3 uri-table-scraper.py -match "(?i)position" -url https://byucougars.com/sports/football/roster -type stdout
```

### csv & json file 
```
python3 uri-table-scraper.py -match "(?i)position" -url https://byucougars.com/sports/football/roster -type csv -outfile out.csv
python3 uri-table-scraper.py -match "(?i)position" -url https://byucougars.com/sports/football/roster -type json -outfile out.json
```

# Go Examples

### Compile
```
go mod init
go mod tidy
go build .
```

### Run

```
./uri-table-scraper.py -match "(?i)position" -url https://byucougars.com/sports/football/roster -type stdout
```


## Using Playwrite

```
python3 -m venv .venv
. .venv/bin/activate
pip install playwright
playwright install-deps
python3 useplaywright.py
```

### URL example from playwright you could utilize instead table parsing
```
https://byucougars.com/website-api/rosters?filter%5Bsport_id%5D=4&include=season&sort=-id&per_page=200
```


## Update xlsx Roster URLs

### Steps

```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Download xslx file to say Roster_URL.xlsx

Header example: ID      School  Conference      Roster URL      Website Host


Run update
```
python3 ddgs-get-roster-url-update-xlsx.py --type xlsx --file Roster_URL.xlsx
```

This get's most URLs but you may have to manually get blank ones unless you want to use different search or use api service
