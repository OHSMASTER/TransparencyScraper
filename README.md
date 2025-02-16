# About This Project

## Transparency Portal Scraper

This project is a web scraper built using Python, Selenium, and BeautifulSoup to search and extract public data from the Brazilian Transparency Portal (`portaldatransparencia.gov.br`). The scraper automates searches for individuals, retrieving details related to public service employment, benefits, and financial transactions.

## Features
- Searches for individuals using CPF or name.
- Extracts public service employment details if applicable.
- Retrieves financial benefits or transactions involving the searched individual.
- Uses Selenium to navigate and scrape dynamically loaded content.
- Displays results in a structured table format using `tabulate`.

## Technologies Used
- **Python**: Core programming language.
- **Selenium**: Web automation framework for navigating the Transparency Portal.
- **BeautifulSoup**: HTML parsing and data extraction.
- **Tabulate**: Formats output tables for readability.
- **Colorama**: Adds color to terminal output for better user experience.

## How to Use
1. Install dependencies using `pip install -r requirements.txt`.
2. Run the script with `python scraper.py`.
3. Enter the CPF or name of the person to search.
4. Choose from the displayed results to extract further details.

## License
This project is open-source and licensed under the MIT License.

## Contribution
Contributions are welcome! Feel free to open an issue or submit a pull request.

## Disclaimer
This tool is intended for educational and research purposes only. The extracted data is publicly available on the Transparency Portal, and no private information is accessed beyond what is openly published.

