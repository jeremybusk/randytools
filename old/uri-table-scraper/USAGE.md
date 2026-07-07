
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Download xslx file to say Roster_URL.xlsx

Header example: ID	School	Conference	Roster URL	Website Host


Run update
```
python3 ddgs-get-roster-url-update-xlsx.py --type xlsx --file Roster_URL.xlsx
```

This get's most URLs but you may have to manually get blank ones unless you want to use different search or use api service
