import sys
import pandas as pd

def load_and_clean(csv_path):
    df = pd.read_csv(csv_path, parse_dates=['date'], infer_datetime_format=True)
    # Clean numeric columns by stripping non-numeric characters
    num_cols = [
        'open_interest', 'total_traders',
        'commit_noncom_long', 'change_noncom_long',
        'commit_noncom_short', 'change_noncom_short',
        'commit_noncom_spreads', 'change_noncom_spreads',
        'commit_com_long', 'change_com_long',
        'commit_com_short', 'change_com_short',
        'commit_tot_long', 'change_tot_long',
        'commit_tot_short', 'change_tot_short',
        'commit_nonrep_long', 'change_nonrep_long',
        'commit_nonrep_short', 'change_nonrep_short'
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = (
                df[c]
                .astype(str)
                .str.replace(r"[^\d\.-]", "", regex=True)
                .replace('', pd.NA)
                .astype(float)
            )
    return df.sort_values('date').reset_index(drop=True)


def compute_cot_signal(df):
    # Calculate net positions and weekly changes for commercials
    df['net_com'] = df['commit_com_long'] - df['commit_com_short']
    df['delta_net_com'] = df['change_com_long'] - df['change_com_short']
    df['bias'] = df['delta_net_com'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

    # New: calculate commercial activity and normalized bias score
    df['comm_activity'] = df['commit_com_long'] + df['commit_com_short']
    df['bias_score'] = df.apply(
        lambda row: (row['delta_net_com'] / row['comm_activity']) if row['comm_activity'] > 0 else 0,
        axis=1
    )
    return df


def main(csv_path):
    df = load_and_clean(csv_path)
    df = compute_cot_signal(df)
    # Select relevant columns for output
    cols = ['date',
            'instrument' if 'instrument' in df.columns else None,
            'net_com', 'delta_net_com', 'bias', 'bias_score']
    cols = [c for c in cols if c]
    print(df[cols].to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <input_csv>")
        sys.exit(1)
    main(sys.argv[1])
