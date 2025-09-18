# scraper/archive_daily.py
import os
from datetime import datetime, timezone, timedelta
import requests

# ---- Sources (HDFC is already a PDF; AXIS & ICICI we render via Node) ----
HDFC = {
    "name": "HDFC_Rates",
    "url": "https://www.hdfcbank.com/content/bbp/repositories/723fb80a-2dde-42a3-9793-7ae1be57c87f/?path=/Personal/Home/content/rates.pdf",
}

# ---- Base folder (exact spelling you asked) ----
BASE_DIR = os.path.join("data", "Currency Raw Data")

# ---- IST time ----
IST = timezone(timedelta(hours=5, minutes=30))

# ---- polite headers ----
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/pdf, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def today_folder_paths():
    """
    Build your nested path using IST:
      data/Currency Raw Data/YYYY/<FullMonth YY>/<DDMonAbbrev YY>/
    Example for 12 Dec 2026:
      data/Currency Raw Data/2026/December 26/12Dec 26/
    """
    now = datetime.now(IST)
    year_full = now.strftime("%Y")   # 2026
    year_2    = now.strftime("%y")   # 26
    month_full = now.strftime("%B")  # December
    month_abbr = now.strftime("%b")  # Dec
    day        = now.strftime("%d")  # 12

    year_folder  = year_full
    month_folder = f"{month_full} {year_2}"
    day_folder   = f"{day}{month_abbr} {year_2}"

    abs_folder = os.path.join(BASE_DIR, year_folder, month_folder, day_folder)
    os.makedirs(abs_folder, exist_ok=True)
    return abs_folder, now.isoformat(timespec="seconds")

def save_hdfc_pdf(folder):
    out_path = os.path.join(folder, f"{HDFC['name']}.pdf")
    r = requests.get(HDFC["url"], headers=DEFAULT_HEADERS, timeout=90)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    print(f"Saved {out_path}  ({max(1, len(r.content)//1024)} KB)")
    return out_path

def write_readme(folder, when_ist):
    with open(os.path.join(folder, "README.txt"), "w", encoding="utf-8") as f:
        f.write(
            "Daily currency rate PDF snapshots\n"
            f"Run (IST): {when_ist}\n"
            "\n"
            "Files:\n"
            "- HDFC_Rates.pdf\n"
            "- AXIS_Rates.pdf\n"
            "- ICICI_Rates.pdf\n"
        )

def main():
    folder, when_ist = today_folder_paths()
    print("Snapshot folder:", folder)
    try:
        save_hdfc_pdf(folder)
    except Exception as e:
        print("WARNING: failed saving HDFC PDF:", e)

    # Note: AXIS/ICICI PDFs are produced by the Node step after this script runs.
    write_readme(folder, when_ist)
    print("Folder prepared. (Node step will add AXIS/ICICI PDFs.)")

if __name__ == "__main__":
    main()
