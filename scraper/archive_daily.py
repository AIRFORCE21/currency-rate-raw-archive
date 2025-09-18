# scraper/archive_daily.py
import os
from datetime import datetime, timezone, timedelta
import requests

# ---- Sources (feel free to rename 'name' fields) ----
SOURCES = [
    {
        "name": "HDFC_Rates",
        "url": "https://www.hdfcbank.com/content/bbp/repositories/723fb80a-2dde-42a3-9793-7ae1be57c87f/?path=/Personal/Home/content/rates.pdf",
        "ext": "pdf",  # HDFC is a PDF
    },
    {
        "name": "AXIS_Rates",
        "url": "https://application.axisbank.co.in/WebForms/corporatecardrate/index.aspx",
        "ext": "html",
    },
    {
        "name": "ICICI_Rates",
        "url": "https://www.icicibank.com/corporate/global-markets/forex/forex-card-rate",
        "ext": "html",
    },
]

# ---- Where to save (your requested tree) ----
BASE_DIR = os.path.join("data", "Currency rate PDF DATA")

# ---- IST time ----
IST = timezone(timedelta(hours=5, minutes=30))

# ---- polite headers ----
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def today_paths():
    now_ist = datetime.now(IST)
    year = now_ist.strftime("%Y")
    month = now_ist.strftime("%m")
    day = now_ist.strftime("%d")
    folder = os.path.join(BASE_DIR, year, month, day)
    os.makedirs(folder, exist_ok=True)
    return folder, now_ist.isoformat(timespec="seconds")

def fetch_and_save(src, folder):
    """Download a source and save to folder with the right extension."""
    url, name, ext = src["url"], src["name"], src.get("ext", "html")
    out_path = os.path.join(folder, f"{name}.{ext}")
    r = requests.get(url, headers=DEFAULT_HEADERS, timeout=90)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    size_kb = max(1, len(r.content) // 1024)
    print(f"Saved {out_path}  ({size_kb} KB)")
    return out_path

def write_readme(folder, when_ist, saved_files):
    """Drop a tiny README in the day folder to make browsing easier."""
    lines = [
        f"# Daily currency rate snapshots",
        f"- Run (IST): {when_ist}",
        "",
        "## Files",
    ] + [f"- {os.path.basename(p)}" for p in saved_files]
    with open(os.path.join(folder, "README.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    folder, when_ist = today_paths()
    print("Snapshot folder:", folder)
    saved = []
    for s in SOURCES:
        try:
            saved.append(fetch_and_save(s, folder))
        except Exception as e:
            print(f"WARNING: failed to save {s['name']}: {e}")
    write_readme(folder, when_ist, saved)
    print("Done.")

if __name__ == "__main__":
    main()
