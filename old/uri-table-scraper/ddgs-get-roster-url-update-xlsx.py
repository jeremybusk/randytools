import pandas as pd
import random
import time
import argparse
from ddgs import DDGS

def get_roster_url(school):
    print(school)
    query = f"{school} athletics football roster"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query.lower(), max_results=5)
            if results:
                for result in results:
                    url = result.get("href", "")
                    if "/roster" in url:
                        clean_url = url.split("/roster")[0] + "/roster"
                        print(f"dirty_url: {url}")
                        print(f"clean_url: {clean_url}")
                        return clean_url
    except Exception:
        pass
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=['csv', 'xlsx'], required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--deliminator", default='|')
    args = parser.parse_args()

    if args.type == 'csv':
        df = pd.read_csv(args.file, sep=args.deliminator)
    else:
        df = pd.read_excel(args.file)

    if "Roster URL" not in df.columns:
        df["Roster URL"] = pd.Series(dtype=object)
    else:
        df["Roster URL"] = df["Roster URL"].astype(object)

    for index, row in df.iterrows():
        if pd.isna(row["Roster URL"]) or str(row["Roster URL"]).strip() == "":
            url = get_roster_url(row["School"])
            
            if url and url.endswith("/roster"):
                df.at[index, "Roster URL"] = url

            num = random.randint(0, 10)
            time.sleep(num)

    if args.type == 'csv':
        df.to_csv(args.file, sep=args.deliminator, index=False)
    else:
        df.to_excel(args.file, index=False)

if __name__ == "__main__":
    main()
