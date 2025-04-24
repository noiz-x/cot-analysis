import re
import requests
import csv
import sys
from bs4 import BeautifulSoup

def parse_block(block):
    import re

    header_m = re.search(r"^(.+?)\s+Code-(\d+)", block, re.MULTILINE)
    if not header_m:
        return None
    instrument, code = header_m.group(1).strip(), header_m.group(2)

    date_m = re.search(r"AS OF\s+(\d{2}/\d{2}/\d{2})", block)
    date = date_m.group(1) if date_m else ""

    unit_m = re.search(r"\(CONTRACTS OF\s+(.+?)\)", block)
    unit = unit_m.group(1).strip() if unit_m else ""

    oi_m = re.search(r"OPEN INTEREST:\s*([\d,]+)", block)
    open_interest = oi_m.group(1).replace(",", "") if oi_m else ""

    cm = re.search(r"COMMITMENTS.*?\n\s*([-\d, ]+)", block, re.DOTALL)
    commits = re.findall(r"-?[\d,]+", cm.group(1)) if cm else []

    ch = re.search(r"CHANGES FROM.*?\n\s*([-\d, ,]+)", block, re.DOTALL)
    changes = re.findall(r"-?[\d,]+", ch.group(1)) if ch else []

    pm = re.search(r"PERCENT OF OPEN INTEREST.*?\n\s*([-\d\.\s]+)", block, re.DOTALL)
    percents = re.findall(r"-?\d+\.\d+|-?\d+", pm.group(1)) if pm else []

    tm = re.search(r"NUMBER OF TRADERS.*?\n\s*([\d\s]+)", block, re.DOTALL)
    traders_all = re.findall(r"\d+", tm.group(1)) if tm else []
    total_tr_m = re.search(r"TOTAL TRADERS:\s*(\d+)", block)
    total_traders = total_tr_m.group(1) if total_tr_m else ""
    if traders_all and traders_all[0] == total_traders:
        traders = traders_all[1:]
    else:
        traders = traders_all

    labels = [
      "noncom_long","noncom_short","noncom_spreads",
      "com_long","com_short",
      "tot_long","tot_short",
      "nonrep_long","nonrep_short"
    ]

    data = {
      "instrument":    instrument,
      "code":          code,
      "date":          date,
      "unit":          unit,
      "open_interest": open_interest,
      "total_traders": total_traders
    }

    for i, lab in enumerate(labels):
        data[f"commit_{lab}"]  = commits[i].replace(",", "") if i < len(commits) else ""
        data[f"change_{lab}"]  = changes[i].replace(",", "") if i < len(changes) else ""
        data[f"percent_{lab}"] = percents[i]            if i < len(percents) else ""

    for i, lab in enumerate(labels[:7]):
        data[f"traders_{lab}"] = traders[i] if i < len(traders) else ""

    return data

def fetch_text(url):
    r = requests.get(url)
    r.raise_for_status()
    html = r.text

    soup = BeautifulSoup(html, 'html.parser')
    pre = soup.find('pre')
    if not pre:
        raise ValueError("No <pre> tag found in HTML at " + url)
    return pre.get_text()

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <output_csv>")
        sys.exit(1)
    
    out_csv = sys.argv[1]
    
    links = [
        "https://www.cftc.gov/dea/futures/deacmesf.htm",
        "https://www.cftc.gov/dea/futures/deanybtsf.htm",
    ]
    
    instrument_filter = [
        "USD INDEX - ICE FUTURES U.S.",
        "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",
    ]
    
    all_records = []
    
    for url in links:
        try:
            text = fetch_text(url)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

        blocks = re.split(r"\n\s*\n(?=.*\bCode\b)", text.strip())
        for b in blocks:
            record = parse_block(b)
            if record:
                if record["instrument"] in instrument_filter:
                    all_records.append(record)
    
    if not all_records:
        print("No records found for specified instruments.")
        sys.exit(0)

    fieldnames = list(all_records[0].keys())
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)
    
    print(f"CSV written to {out_csv}")

if __name__=="__main__":
    main()
