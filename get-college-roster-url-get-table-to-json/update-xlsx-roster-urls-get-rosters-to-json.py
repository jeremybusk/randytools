import os
import yaml
import random
import time
import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from ddgs import DDGS

def get_roster_url(school, suffix):
    query = f"{school} athletics football roster"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query.lower(), max_results=5)
            if results:
                for result in results:
                    url = result.get("href", "")
                    if suffix in url:
                        return url.split(suffix)[0] + suffix
    except Exception:
        pass
    return None

def scrape_roster(url, match_pattern):
    pattern = re.compile(match_pattern)
    tables_data = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return tables_data

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
            tables_data.append({'headers': headers, 'rows': rows})
            
    return tables_data

def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    input_excel = config.get('input_excel', 'teams.xlsx')
    output_excel = config.get('output_excel', 'teams.xlsx')
    match_pattern = config.get('match_pattern', '(?i)name|player')
    search_suffix = config.get('search_suffix', '/roster')
    skip_existing = config.get('skip_existing', False)
    diff_only = config.get('diff_only', False)
    diff_report_file = config.get('diff_report_file', 'diff-report.json')

    df = pd.read_excel(input_excel)

    if "Roster URL" not in df.columns:
        df["Roster URL"] = pd.Series(dtype=object)
    else:
        df["Roster URL"] = df["Roster URL"].astype(object)

    diff_summary = {}

    for index, row in df.iterrows():
        school = row["School"]
        url = row["Roster URL"]
        
        safe_school_name = re.sub(r'(?u)[^-\w.]', '_', str(school))
        json_filename = f"{safe_school_name}.roster.out.json"
        file_exists = os.path.exists(json_filename)

        if skip_existing and file_exists and not diff_only:
            print(f"Skipping {school}, {json_filename} already exists.")
            continue

        if pd.isna(url) or str(url).strip() == "":
            print(f"Finding URL for {school}...")
            url = get_roster_url(school, search_suffix)
            if url:
                df.at[index, "Roster URL"] = url

        if url:
            print(f"Scraping {url}...")
            tables = scrape_roster(url, match_pattern)
            
            if tables:
                all_tables_data = []
                for t in tables:
                    table_dict_list = []
                    for r in t['rows']:
                        table_dict_list.append(dict(zip(t['headers'], r)))
                    all_tables_data.append(table_dict_list)

                if diff_only and file_exists:
                    with open(json_filename, 'r', encoding='utf-8') as f:
                        old_data = json.load(f)

                    old_set = set(json.dumps(row, sort_keys=True) for table in old_data for row in table)
                    new_set = set(json.dumps(row, sort_keys=True) for table in all_tables_data for row in table)

                    added = [json.loads(x) for x in new_set - old_set]
                    removed = [json.loads(x) for x in old_set - new_set]

                    if added or removed:
                        diff_summary[school] = {"added": added, "removed": removed}
                        print(f"\n--- DIFF FOR {school} ---")
                        print(f"Added:\n{json.dumps(added, indent=2)}")
                        print(f"Removed:\n{json.dumps(removed, indent=2)}\n")
                    else:
                        print(f"No changes found for {school}.")
                
                elif not diff_only:
                    with open(json_filename, 'w', encoding='utf-8') as f:
                        json.dump(all_tables_data, f, indent=2)

        num = random.randint(2, 8)
        time.sleep(num)

    if not diff_only:
        df.to_excel(output_excel, index=False)
    else:
        with open(diff_report_file, 'w', encoding='utf-8') as f:
            json.dump(diff_summary, f, indent=2)
        print(f"\nDiff report complete. Summary saved to {diff_report_file}")

if __name__ == '__main__':
    main()
