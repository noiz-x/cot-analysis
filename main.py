import sys
import pandas as pd

def load_and_clean(csv_path):
    df = pd.read_csv(csv_path, parse_dates=['date'], infer_datetime_format=True)
    num_cols = [
        'open_interest', 'total_traders',
        'commit_noncom_long', 'change_noncom_long', 'percent_noncom_long',
        'commit_noncom_short', 'change_noncom_short', 'percent_noncom_short',
        'commit_noncom_spreads', 'change_noncom_spreads', 'percent_noncom_spreads',
        'commit_com_long', 'change_com_long', 'percent_com_long',
        'commit_com_short', 'change_com_short', 'percent_com_short',
        'commit_tot_long', 'change_tot_long', 'percent_tot_long',
        'commit_tot_short', 'change_tot_short', 'percent_tot_short',
        'commit_nonrep_long', 'change_nonrep_long', 'percent_nonrep_long',
        'commit_nonrep_short', 'change_nonrep_short', 'percent_nonrep_short',
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = (
                df[c]
                .astype(str)
                .str.replace(r'[^\d\.-]', '', regex=True)
                .replace('', pd.NA)
                .astype(float)
            )
    return df.sort_values('date').reset_index(drop=True)

def engineer_features(df, ma_window=13, z_lookback=260):
    df['pct_net_com']    = df['percent_com_long']     - df['percent_com_short']
    df['pct_net_noncom'] = df['percent_noncom_long']  - df['percent_noncom_short']
    df['pct_net_nonrep'] = df['percent_nonrep_long']  - df['percent_nonrep_short']
    df['smoothed_pct_net_com'] = (
        df['pct_net_com']
        .rolling(window=ma_window, min_periods=1)
        .mean()
    )
    roll_mean = df['pct_net_com'].rolling(window=z_lookback, min_periods=2).mean()
    roll_std  = df['pct_net_com'].rolling(window=z_lookback, min_periods=2).std()
    df['z_com'] = (df['pct_net_com'] - roll_mean) / roll_std
    df['pctl_net_com']    = df['pct_net_com'].rank(pct=True) * 100
    df['pctl_net_noncom'] = df['pct_net_noncom'].rank(pct=True) * 100
    df['pctl_net_nonrep'] = df['pct_net_nonrep'].rank(pct=True) * 100
    bins   = [0, 20, 40, 60, 80, 100]
    labels = [1, 2, 3, 4, 5]
    df['scale_com']     = pd.cut(df['pctl_net_com'], bins=bins, labels=labels, include_lowest=True).astype(int)
    df['scale_noncom']  = pd.cut(df['pctl_net_noncom'], bins=bins, labels=labels, include_lowest=True).astype(int)
    df['scale_nonrep']  = 6 - pd.cut(df['pctl_net_nonrep'], bins=bins, labels=labels, include_lowest=True).astype(int)
    def map_bias(s):
        if s >= 4:
            return 'Bullish'
        if s == 3:
            return 'Neutral'
        return 'Bearish'
    df['bias_com']     = df['scale_com'].apply(map_bias)
    df['bias_noncom']  = df['scale_noncom'].apply(map_bias)
    df['bias_nonrep']  = df['scale_nonrep'].apply(map_bias)
    return df

def generate_signals(df, z_thresh=1.0):
    df = df.copy()
    df['signal'] = 0
    df.loc[df['z_com'] < -z_thresh, 'signal'] = +1
    df.loc[df['z_com'] > +z_thresh, 'signal'] = -1
    return df

def main(csv_path):
    df = load_and_clean(csv_path)
    df = engineer_features(df, ma_window=13, z_lookback=260)
    df = generate_signals(df, z_thresh=1.0)
    cols = [
        'date',
        'instrument',
        'pct_net_com', 'scale_com', 'bias_com',
        'pct_net_noncom', 'scale_noncom', 'bias_noncom',
        'pct_net_nonrep', 'scale_nonrep', 'bias_nonrep',
        'signal'
    ]
    print(df[cols].to_string(index=False))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <input_csv>")
        sys.exit(1)
    main(sys.argv[1])
