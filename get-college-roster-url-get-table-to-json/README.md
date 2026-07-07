# README

## Update xlsx Roster URLs

### Steps

```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Download xslx file to say teams.xlsx with header/data format like below:

ID      School  Conference      Roster URL      Website Host

```
ID|School|Conference|Roster URL|Website Host
14|Boston College|ACC|https://bceagles.com/sports/football/roster	
18|California|ACC|https://calbears.com/sports/football/roster	
```


Run update
```
python3 ddgs-get-roster-url-update-xlsx.py --type xlsx --file Roster_URL.xlsx
```

This get's most URLs but you may have to manually get blank ones unless you want to use different search or use api service



## Other Explore Options Using Playwrite

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
