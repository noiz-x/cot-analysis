# COT Analysis

This project provides tools for analyzing Commitment of Traders (COT) data. It implements data cleaning, feature engineering, and signal generation for market sentiment analysis based on COT reports.

## Requirements

- Python 3.x
- pandas
- requests
- BeautifulSoup (bs4)

## Usage

To fetch and parse data into CSV:
```bash
python data.py <output_csv>
```

To generate signals from your COT data:
```bash
python main.py <input_csv>
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting issues, submitting feature requests, or contributing code.

## License

This project is licensed under the [MIT License](LICENSE).