"""Merge two *downloaded* official CSVs, with checks, by epidemiological week.

Usage:
python scripts/prepare_data.py --cases data/raw/infodengue.csv \
    --climate data/raw/climate_weekly.csv --out data/processed/rio_weekly.csv

InfoDengue requires SE, data_iniSE, casprov.
Mosqlimate requires epiweek, temp_med_avg, precip_tot_sum; if geocodigo is
present this script filters Rio (3304557). The caller is responsible for
obtaining climate data using corrected precipitation where available.
"""
import argparse
from pathlib import Path
import pandas as pd

RIO = 3304557

def prepare(cases_path, climate_path):
    a = pd.read_csv(cases_path)
    b = pd.read_csv(climate_path)
    for name, df, keys in (
        ("InfoDengue", a, {"SE", "data_iniSE", "casprov"}),
        ("Mosqlimate", b, {"epiweek", "temp_med_avg", "precip_tot_sum"}),
    ):
        missing = keys - set(df.columns)
        if missing:
            raise ValueError(f"{name}: missing columns {sorted(missing)}")
    if "geocodigo" in b:
        b = b[pd.to_numeric(b["geocodigo"], errors="coerce") == RIO].copy()
    a["epiweek"] = pd.to_numeric(a["SE"]).astype(int)
    b["epiweek"] = pd.to_numeric(b["epiweek"]).astype(int)
    if a.epiweek.duplicated().any() or b.epiweek.duplicated().any():
        raise ValueError("duplicate epidemiological weeks in source")
    out = a[["epiweek","data_iniSE","casprov"]].merge(
        b[["epiweek","temp_med_avg","precip_tot_sum"]],
        on="epiweek", validate="one_to_one", how="left", indicator=True)
    if (out["_merge"] != "both").any():
        raise ValueError("some InfoDengue weeks have no climate match")
    out["week_start"] = pd.to_datetime(out["data_iniSE"], errors="raise")
    rename = {"casprov":"cases","temp_med_avg":"temperature_c",
              "precip_tot_sum":"rainfall_mm"}
    out = out.rename(columns=rename).sort_values("week_start")
    for key in ["cases","temperature_c","rainfall_mm"]:
        out[key] = pd.to_numeric(out[key], errors="raise")
    if out[["cases","temperature_c","rainfall_mm"]].isna().any().any():
        raise ValueError("missing values must be investigated, not silently filled")
    if (out[["cases","rainfall_mm"]] < 0).any().any():
        raise ValueError("negative observations")
    if not (out.week_start.diff().dropna().dt.days == 7).all():
        raise ValueError("series contains missing or noncontiguous weeks")
    return out[["week_start","epiweek","cases","temperature_c","rainfall_mm"]].reset_index(drop=True)

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--cases",required=True)
    p.add_argument("--climate",required=True)
    p.add_argument("--out",default="data/processed/rio_weekly.csv")
    args=p.parse_args()
    clean=prepare(args.cases,args.climate)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    clean.to_csv(out,index=False)
    print(f"Prepared {len(clean)} continuous weeks -> {out}")
