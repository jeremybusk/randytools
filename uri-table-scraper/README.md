# README

## Python Examples

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



