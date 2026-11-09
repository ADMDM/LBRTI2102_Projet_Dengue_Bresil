"""Download raw InfoDengue CSV for Rio. Requires Internet; no API key needed.

This is for data acquisition, not a claim of successful access. Cross-check
the data dictionary and URL parameters against the current InfoDengue API.
"""
import argparse
from pathlib import Path
import requests

URL="https://info.dengue.mat.br/api/alertcity"

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--start-year",type=int,default=2023)
    p.add_argument("--end-year",type=int,default=2024)
    p.add_argument("--out",type=Path,default=Path("data/raw/infodengue.csv"))
    a=p.parse_args()
    if a.start_year > a.end_year:
        p.error("start-year must be <= end-year")
    response=requests.get(URL,params={"geocode":3304557,"disease":"dengue",
        "format":"csv","ew_start":1,"ew_end":53,
        "ey_start":a.start_year,"ey_end":a.end_year},timeout=60)
    response.raise_for_status()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_bytes(response.content)
    print("Downloaded:",a.out,"bytes:",len(response.content))
    print("Check SE, data_iniSE, casprov and coverage before using.")
