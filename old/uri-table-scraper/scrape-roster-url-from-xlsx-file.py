import argparse
import csv
import json
import re
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-url')
    parser.add_argument('-xlsx')
    parser.add_argument('-match', required=True)
    parser.add_argument('-outfile')
    parser.add_argument('-type', default='stdout', choices=['stdout', 'csv', 'json'])
    args = parser.parse_args()

    if not args.url and not args.xlsx:
        parser.error("Either -url or -xlsx must be provided.")

    if (args.type == "csv" or args.type == "json") and args.outfile is None:
        parser.error("-outfile is required when -type is csv or json.")

    pattern = re.compile(args.match)
    
    urls = []
    if args.url:
        urls.append(args.url)
    
    if args.xlsx:
        try:
            df = pd.read_excel(args.xlsx)
            if "Roster URL" in df.columns:
                urls.extend([url for url in df["Roster URL"].dropna().astype(str).tolist() if url.strip()])
        except Exception as e:
            sys.exit(f"Error reading Excel file: {e}")

    tables_data = []

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}", file=sys.stderr)
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        for table in soup.find_all('table'):
            headers = []
            rows = []
            header_match = False
            is_header_parsed = False

            for tr in table.find_all('tr'):
                cells = tr.find_all(['th', 'td'])
                if not cells:
                    continue

                is_row_header = tr.parent.name == 'thead' or (not is_header_parsed and tr.find('th'))

                if is_row_header and not is_header_parsed:
                    for cell in cells:
                        text = ' '.join(cell.stripped_strings)
                        headers.append(text)
                        if pattern.search(text):
                            header_match = True
                    is_header_parsed = True
                    continue

                if is_header_parsed:
                    row_data = []
                    for cell in cells:
                        cell_content = []
                        for a in cell.find_all('a', href=True):
                            href = a['href']
                            if 'twitter.com' in href or 'x.com' in href:
                                cell_content.append(href)

                        text = ' '.join(cell.stripped_strings)
                        if text:
                            cell_content.append(text)

                        row_data.append(' | '.join(cell_content))

                    if any(row_data):
                        while len(row_data) < len(headers):
                            row_data.append("")
                        row_data = row_data[:len(headers)]
                        rows.append(row_data)

            if header_match and rows:
                tables_data.append({'headers': headers, 'rows': rows, 'source_url': url})

    if not tables_data:
        sys.exit(0)

    out_type = args.type.lower()

    if out_type == 'csv':
        with open(args.outfile, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for t in tables_data:
                writer.writerow(t['headers'] + ['Source_URL'])
                for row in t['rows']:
                    writer.writerow(row + [t['source_url']])

    elif out_type == 'json':
        all_tables_data = []
        for t in tables_data:
            table_dict_list = []
            for row in t['rows']:
                row_dict = dict(zip(t['headers'], row))
                row_dict['Source_URL'] = t['source_url']
                table_dict_list.append(row_dict)
            all_tables_data.append(table_dict_list)
        
        with open(args.outfile, 'w', encoding='utf-8') as f:
            json.dump(all_tables_data, f, indent=2)

    else:
        for i, t in enumerate(tables_data):
            if i > 0:
                print()

            print(f"Source URL: {t['source_url']}")
            col_widths = [len(h) for h in t['headers']]
            for row in t['rows']:
                for j, col in enumerate(row):
                    if j < len(col_widths):
                        col_widths[j] = max(col_widths[j], len(col))

            header_fmt = "   ".join([f"{h:<{w}}" for h, w in zip(t['headers'], col_widths)])
            print(header_fmt)

            for row in t['rows']:
                row_fmt = "   ".join([f"{c:<{w}}" for c, w in zip(row, col_widths)])
                print(row_fmt)

if __name__ == '__main__':
    main()
