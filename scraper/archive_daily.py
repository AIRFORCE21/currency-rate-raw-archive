# scraper/archive_daily.py
import os
import time
from datetime import datetime, timezone, timedelta
import requests

# ---- Where to save (your exact tree) ----
BASE_DIR = os.path.join("data", "Currency Raw Data")

# ---- IST time ----
IST = timezone(timedelta(hours=5, minutes=30))

# ---- Sources ----
SOURCES = [
    {
        "name": "HDFC_Rates",
        "url": "https://www.hdfcbank.com/content/bbp/repositories/723fb80a-2dde-42a3-9793-7ae1be57c87f/?path=/Personal/Home/content/rates.pdf",
        "ext": "pdf",  # save as PDF
    },
    {
        "name": "AXIS_Rates",
        "url": "https://application.axisbank.co.in/WebForms/corporatecardrate/index.aspx",
        "ext": "html",  # save raw HTML
    },
    {
        "name": "ICICI_Rates",
        "url": "https://www.icicibank.com/corporate/global-markets/forex/forex-card-rate",
        "ext": "html",  # save raw HTML
    },
]

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def ist_folder():
    """
    data/Currency Raw Data/YYYY/December 26/12Dec 26/
    """
    now = datetime.now(IST)
    year_full = now.strftime("%Y")       # 2026
    yy        = now.strftime("%y")       # 26
    month_full = now.strftime("%B")      # December
    mon_abbr   = now.strftime("%b")      # Dec
    dd         = now.strftime("%d")      # 12

    month_folder = f"{month_full} {yy}"      # "December 26"
    day_folder   = f"{dd}{mon_abbr} {yy}"    # "12Dec 26"

    folder = os.path.join(BASE_DIR, year_full, month_folder, day_folder)
    os.makedirs(folder, exist_ok=True)
    return folder, now.isoformat(timespec="seconds")

def fetch_with_retries(url, timeout=90, retries=3, backoff=2):
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.content
        except Exception as e:
            last = e
            time.sleep(backoff * (i + 1))
    raise last

def save_file(folder, name, ext, content: bytes):
    path = os.path.join(folder, f"{name}.{ext}")
    with open(path, "wb") as f:
        f.write(content)
    kb = max(1, len(content) // 1024)
    print(f"Saved {path}  ({kb} KB)")
    return path

def write_readme(folder, when_ist, files):
    lines = [
        "Daily currency rate snapshots",
        f"Run (IST): {when_ist}",
        "",
        "Files:",
        *[f"- {os.path.basename(p)}" for p in files],
    ]
    with open(os.path.join(folder, "README.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    folder, when_ist = ist_folder()
    print("Snapshot folder:", folder)
    saved = []
    for s in SOURCES:
        try:
            content = fetch_with_retries(s["url"])
            saved.append(save_file(folder, s["name"], s["ext"], content))
        except Exception as e:
            print(f"WARNING: failed {s['name']}: {e}")
    write_readme(folder, when_ist, saved)
    print("Done.")

if __name__ == "__main__":
    main()
