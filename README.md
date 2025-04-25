# COT Analysis & Signal Generator

This project offers an updated suite of tools for analyzing Commitment of Traders (COT) data. In addition to data parsing and cleaning, it now includes advanced bias generation for improved market sentiment analysis based on the latest COT reports.

## Requirements

- Python 3.x
- pandas
- requests
- BeautifulSoup (bs4)

## Usage

To fetch and parse the latest COT data into a CSV file:
```bash
python data.py <output_csv>
```

To generate trading bias from your cleaned COT CSV data:
```bash
python main.py <input_csv>
```

## Contributing

Contributions are welcome! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting issues, submitting feature requests, or contributing improvements.

## License

This project is licensed under the [MIT License](LICENSE).