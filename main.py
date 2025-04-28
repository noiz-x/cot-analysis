import sys
import pandas as pd

# 1. Load and clean COT report CSV
def load_and_clean(csv_path):
    df = pd.read_csv(f"data/{csv_path}")
    # Explicitly parse 'date' column after reading
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y', errors='coerce')

    # Strip non-numeric characters from numeric fields
    num_cols = [
        'open_interest',
        'commit_noncom_long', 'change_noncom_long',
        'commit_noncom_short', 'change_noncom_short',
        'commit_noncom_spreads', 'change_noncom_spreads',
        'commit_com_long', 'change_com_long',
        'commit_com_short', 'change_com_short',
        'traders_noncom_long', 'traders_noncom_short',
        'traders_com_long', 'traders_com_short'
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = (
                df[c].astype(str)
                       .str.replace(r"[^\d\.-]", "", regex=True)
                       .replace('', pd.NA)
                       .astype(float)
            )
    return df.sort_values('date').reset_index(drop=True)

# 2. Compute average commitment per trader for each category and set bias
def compute_avg_commitment_bias(df):
    # Avoid division by zero by replacing 0 with NaN temporarily
    df['avg_com_long_per_trader'] = df['commit_com_long'] / df['traders_com_long'].replace(0, pd.NA)
    df['avg_com_short_per_trader'] = df['commit_com_short'] / df['traders_com_short'].replace(0, pd.NA)
    df['avg_noncom_long_per_trader'] = df['commit_noncom_long'] / df['traders_noncom_long'].replace(0, pd.NA)
    df['avg_noncom_short_per_trader'] = df['commit_noncom_short'] / df['traders_noncom_short'].replace(0, pd.NA)

    # Fill NaNs created by division-by-zero with 0
    df[['avg_com_long_per_trader', 'avg_com_short_per_trader',
        'avg_noncom_long_per_trader', 'avg_noncom_short_per_trader']] = df[[
            'avg_com_long_per_trader', 'avg_com_short_per_trader',
            'avg_noncom_long_per_trader', 'avg_noncom_short_per_trader'
        ]].fillna(0)

    # Determine bias based on highest average
    def decide_bias(row):
        avgs = {
            'COM_LONG': row['avg_com_long_per_trader'],
            'COM_SHORT': row['avg_com_short_per_trader'],
            'NONCOM_LONG': row['avg_noncom_long_per_trader'],
            'NONCOM_SHORT': row['avg_noncom_short_per_trader']
        }
        if all(v == 0 for v in avgs.values()):
            return 'NEUTRAL'
        return max(avgs, key=avgs.get)

    df['bias'] = df.apply(decide_bias, axis=1)
    return df

# 3. Main execution
def main(csv_path, export_csv=False, csv_out=None):
    df = load_and_clean(csv_path)
    df = compute_avg_commitment_bias(df)

    # Columns to display
    cols = [
        'date', 'instrument',
        'avg_com_long_per_trader', 'avg_com_short_per_trader',
        'avg_noncom_long_per_trader', 'avg_noncom_short_per_trader',
        'bias'
    ]
    print(df[cols].to_string(index=False))

    if export_csv and csv_out:
        df[cols].to_csv(csv_out, index=False)
        print(f"Exported bias analysis to {csv_out}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='COT Bias Analysis: Average Commitment per Trader')
    parser.add_argument('csv', help='Input CSV file path')
    parser.add_argument('--export', help='Optional output CSV path')
    args = parser.parse_args()
    main(args.csv, export_csv=bool(args.export), csv_out=args.export)
