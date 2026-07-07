package main

import (
	"encoding/csv"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"
	"strings"
	"text/tabwriter"

	"github.com/PuerkitoBio/goquery"
)

type TableData struct {
	Headers []string
	Rows    [][]string
}

func main() {
	urlFlag := flag.String("url", "", "")
	regexFlag := flag.String("match", "", "")
	outfileFlag := flag.String("outfile", "", "")
	typeFlag := flag.String("type", "stdout", "")
	flag.Parse()

	if *urlFlag == "" || *regexFlag == "" {
		flag.Usage()
		os.Exit(1)
	}

	outType := strings.ToLower(*typeFlag)
	if (outType == "csv" || outType == "json") && *outfileFlag == "" {
		fmt.Fprintln(os.Stderr, "-outfile is required when -type is csv or json.")
		flag.Usage()
		os.Exit(1)
	}

	re, err := regexp.Compile(*regexFlag)
	if err != nil {
		log.Fatalf("%v", err)
	}

	res, err := http.Get(*urlFlag)
	if err != nil {
		log.Fatalf("%v", err)
	}
	defer res.Body.Close()

	if res.StatusCode != 200 {
		log.Fatalf("%d %s", res.StatusCode, res.Status)
	}

	doc, err := goquery.NewDocumentFromReader(res.Body)
	if err != nil {
		log.Fatalf("%v", err)
	}

	var tables []TableData

	doc.Find("table").Each(func(_ int, tableSel *goquery.Selection) {
		var t TableData
		headerMatch := false
		isHeaderParsed := false

		tableSel.Find("tr").Each(func(_ int, trSel *goquery.Selection) {
			isRowHeader := trSel.Parent().Is("thead") || (!isHeaderParsed && trSel.Find("th").Length() > 0)

			if isRowHeader && !isHeaderParsed {
				trSel.Find("th, td").Each(func(_ int, cell *goquery.Selection) {
					text := strings.Join(strings.Fields(cell.Text()), " ")
					t.Headers = append(t.Headers, text)
					if re.MatchString(text) {
						headerMatch = true
					}
				})
				isHeaderParsed = true
				return
			}

			if isHeaderParsed {
				var row []string
				trSel.ChildrenFiltered("td, th").Each(func(_ int, cell *goquery.Selection) {
					var cellData []string
					cell.Find("a").Each(func(_ int, aSel *goquery.Selection) {
						href, exists := aSel.Attr("href")
						if exists && (strings.Contains(href, "twitter.com") || strings.Contains(href, "x.com")) {
							cellData = append(cellData, href)
						}
					})

					text := strings.Join(strings.Fields(cell.Text()), " ")
					if text != "" {
						cellData = append(cellData, text)
					}

					row = append(row, strings.Join(cellData, " | "))
				})

				if len(row) > 0 {
					for len(row) < len(t.Headers) {
						row = append(row, "")
					}
					if len(row) > len(t.Headers) {
						row = row[:len(t.Headers)]
					}

					hasData := false
					for _, val := range row {
						if val != "" {
							hasData = true
							break
						}
					}
					if hasData {
						t.Rows = append(t.Rows, row)
					}
				}
			}
		})

		if headerMatch && len(t.Rows) > 0 {
			tables = append(tables, t)
		}
	})

	if len(tables) == 0 {
		os.Exit(0)
	}

	switch outType {
	case "csv":
		file, err := os.Create(*outfileFlag)
		if err != nil {
			log.Fatalf("%v", err)
		}
		defer file.Close()

		writer := csv.NewWriter(file)
		defer writer.Flush()

		for _, table := range tables {
			if err := writer.Write(table.Headers); err != nil {
				log.Fatalf("%v", err)
			}
			for _, row := range table.Rows {
				if err := writer.Write(row); err != nil {
					log.Fatalf("%v", err)
				}
			}
		}

	case "json":
		var allTablesData [][]map[string]string
		for _, table := range tables {
			var tableData []map[string]string
			for _, row := range table.Rows {
				obj := make(map[string]string)
				for i, header := range table.Headers {
					if i < len(row) {
						obj[header] = row[i]
					}
				}
				tableData = append(tableData, obj)
			}
			allTablesData = append(allTablesData, tableData)
		}

		file, err := os.Create(*outfileFlag)
		if err != nil {
			log.Fatalf("%v", err)
		}
		defer file.Close()

		enc := json.NewEncoder(file)
		enc.SetIndent("", "  ")
		if err := enc.Encode(allTablesData); err != nil {
			log.Fatalf("%v", err)
		}

	default:
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 3, ' ', 0)
		for i, table := range tables {
			if i > 0 {
				fmt.Fprintln(w, "")
			}
			fmt.Fprintln(w, strings.Join(table.Headers, "\t"))
			for _, row := range table.Rows {
				fmt.Fprintln(w, strings.Join(row, "\t"))
			}
		}
		w.Flush()
	}
}
