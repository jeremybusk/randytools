import pandas as pd
import random
import time
from ddgs import DDGS

csv_file = "teams.csv"
text_in_url = "roster"
url_end = "/roster"

def get_roster_url(school):
    print(school)
    query = f"{school} athletics football roster"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query.lower(), max_results=5)
            if results:
                for result in results:
                    url = result.get("href", "")
                    if text_in_url in url:
                        if url_end in url:
                            clean_url = url.split(url_end)[0] + url_end
                        else:
                            clean_url = url

                        print(url)
                        print(clean_url)
                        return clean_url
    except Exception:
        pass
    return None

df = pd.read_csv(csv_file, sep='|')

if "Roster URL" not in df.columns:
    df["Roster URL"] = pd.Series(dtype=object)
else:
    df["Roster URL"] = df["Roster URL"].astype(object)

for index, row in df.iterrows():
    if pd.isna(row["Roster URL"]) or str(row["Roster URL"]).strip() == "":
        url = get_roster_url(row["School"])
        df.at[index, "Roster URL"] = url

        num = random.randint(0, 10)
        time.sleep(num)

df.to_csv(csv_file, sep='|', index=False)
