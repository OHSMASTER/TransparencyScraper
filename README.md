# Transparency Portal Scraper

## Description
This project is a web scraper built using Python, Selenium, and BeautifulSoup to search and extract public data from the Brazilian Transparency Portal (`portaldatransparencia.gov.br`). The scraper automates searches for individuals, retrieving details related to public service employment, benefits, and financial transactions.

## Features
- Searches for individuals using CPF or name.
- Extracts public service employment details when applicable.
- Retrieves financial benefits or transactions involving the searched individual.
- Uses Selenium to navigate and scrape dynamically loaded content.
- Displays results in a structured table format using `tabulate`.

## Technologies Used
- **Python**: Core programming language.
- **Selenium**: Web automation framework.
- **BeautifulSoup**: HTML parsing and data extraction.
- **Tabulate**: Formats output tables for readability.
- **Colorama**: Adds color to terminal output for a better user experience.

## Getting Started with Transparency Portal Scraper

### Prerequisites
Before you begin, ensure that you have:
- Python (preferably version 3.6+)
- All required libraries installed via pip:

  ```bash
  pip install -r requirements.txt
  ```

### Installation and Execution

#### Install Dependencies
Run the following command to install the necessary libraries:

```bash
pip install -r requirements.txt
```

#### Run the Script
Execute the scraper using:

```bash
python TransparencyScraper.py
```

### Input Query
When prompted, enter the CPF or name of the individual you wish to search for. Then, select from the displayed results to extract further details.

## License
This project is open-source and licensed under the MIT License.

## Contribution
Contributions are welcome! Feel free to open an issue or submit a pull request.

## Disclaimer
This tool is intended for educational and research purposes only. The extracted data is publicly available on the Transparency Portal, and no private information is accessed beyond what is openly published.
