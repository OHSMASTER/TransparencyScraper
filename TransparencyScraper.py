import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tabulate import tabulate
from colorama import Fore, init

init(autoreset=True)

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--log-level=3")

    service = Service(log_path=os.devnull)
    return webdriver.Chrome(service=service, options=chrome_options)

def get_search_results(driver, term):
    url_search = (
        f"https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista?"
        f"termo={term}&pagina=1&tamanhoPagina=10"
    )
    driver.get(url_search)
    wait = WebDriverWait(driver, 10)

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.link-busca-nome")))
    except Exception as e:
        print(Fore.RED + f"Error loading search results: {e}")
        return []

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    results_list = []
    for a in soup.find_all("a", class_="link-busca-nome"):
        name = a.get_text(strip=True)
        href = a.get("href")
        if href.startswith("/"):
            href = "https://portaldatransparencia.gov.br" + href

        parent_div = a.parent
        sibling_divs = [sib for sib in parent_div.find_next_siblings("div") if sib.get_text(strip=True)]
        masked_cpf = sibling_divs[0].get_text(strip=True) if len(sibling_divs) >= 1 else ""
        additional_info = sibling_divs[1].get_text(strip=True) if len(sibling_divs) >= 2 else ""

        results_list.append((name, href, masked_cpf, additional_info))
    return results_list

def display_results(results_list):
    results_table = []
    for i, (name, _, cpf_val, info) in enumerate(results_list, start=1):
        results_table.append([i, name, cpf_val, info])
    print("\n" + Fore.GREEN + "Results found:")
    print(tabulate(results_table, headers=["Index", "Name", "CPF", "Status"], tablefmt="fancy_grid"))

def get_public_server_details(driver):
    try:
        wait = WebDriverWait(driver, 10)
        box_ficha = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.box-ficha__resultados"))
        )
        html_content = box_ficha.get_attribute("innerHTML")
        soup = BeautifulSoup(html_content, "html.parser")

        vinculos_div = soup.find("div", id="vinculos")
        if not vinculos_div:
            print(Fore.YELLOW + "No affiliation data found for Public Server.")
            return

        info_blocks = vinculos_div.find_all("div", class_="col-sm-12 col-md-6")
        details = []
        for block in info_blocks:
            strong_elem = block.find("strong")
            span_elem = block.find("span")
            if strong_elem and span_elem:
                label = strong_elem.get_text(strip=True).replace(":", "")
                value = span_elem.get_text(strip=True)
                details.append((label, value))

        link_detail = soup.find("a", id="urlServidor")
        if link_detail:
            href = link_detail.get("href", "")
            details.append(("URL Detail", href))

        print("\n" + Fore.CYAN + "========== Public Server Details ==========" + "\n")
        if details:
            print(tabulate(details, headers=["Information", "Detail"], tablefmt="fancy_grid"))
        else:
            print(Fore.YELLOW + "No additional information found.")
    except Exception as e:
        print(Fore.RED + f"Error fetching public server details: {e}")
    finally:
        print("\n" + Fore.CYAN + "=============================================" + "\n")

def get_beneficiary_details(driver):
    try:
        wait = WebDriverWait(driver, 10)
        box_ficha = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.box-ficha__resultados"))
        )
        html_ficha = box_ficha.get_attribute("innerHTML")
        soup_ficha = BeautifulSoup(html_ficha, "html.parser")

        direct_values = "Not found"
        span_gastos = soup_ficha.find("span", id="gastosDiretos")
        if span_gastos:
            direct_values = span_gastos.get_text(strip=True).split(":")[-1].strip()

        confidential_values = "Not found"
        span_confidential = soup_ficha.find("span", id="transferenciaRecurso")
        if span_confidential:
            confidential_values = span_confidential.get_text(strip=True).split(":")[-1].strip()

        data = [
            ("Federal Government Resource Beneficiary", ""),
            ("Received Amount", direct_values),
            ("Confidential Received Amount", confidential_values),
        ]

        print("\n" + Fore.CYAN + "========== Beneficiary Details ==========" + "\n")
        print(tabulate(data, headers=["Information", "Detail"], tablefmt="fancy_grid"))
    except Exception as e:
        print(Fore.RED + f"Error fetching beneficiary details: {e}")
    finally:
        print("\n" + Fore.CYAN + "=============================================" + "\n")

def get_benefit_details(driver):
    try:
        wait = WebDriverWait(driver, 10)
        content_div = wait.until(
            EC.presence_of_element_located((By.ID, "accordion-recebimentos-recursos"))
        )
        html_content = content_div.get_attribute("innerHTML")
        soup_det = BeautifulSoup(html_content, "html.parser")

        table = soup_det.find("table", id="tabela-visao-geral-sancoes")
        print("\n" + Fore.CYAN + "========== Benefit Details ==========" + "\n")
        if table:
            headers = []
            thead = table.find("thead")
            if thead:
                headers = [th.get_text(strip=True) for th in thead.find_all("th")]
            rows = []
            tbody = table.find("tbody")
            if tbody:
                for tr in tbody.find_all("tr"):
                    cols = [td.get_text(strip=True) for td in tr.find_all("td")]
                    rows.append(cols)
            if rows:
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            else:
                print(Fore.YELLOW + "No data found in the table.")
        else:
            print(Fore.YELLOW + "Table not found. Content:")
            print(soup_det.prettify())
    except Exception as e:
        print(Fore.RED + f"Error fetching benefit details: {e}")
    finally:
        print("\n" + Fore.CYAN + "=============================================" + "\n")

def get_pension_institutor_details(driver):
    try:
        wait = WebDriverWait(driver, 10)
        box_ficha = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.box-ficha__resultados"))
        )
        html_content = box_ficha.get_attribute("innerHTML")
        soup = BeautifulSoup(html_content, "html.parser")
        
        details = []
        
        vinculos_div = soup.find("div", id="vinculos-instituidor-pensao")
        if vinculos_div:
            info_blocks = vinculos_div.find_all("div", class_="col-sm-12 col-md-6")
            for block in info_blocks:
                strong_elem = block.find("strong")
                span_elem = block.find("span")
                if strong_elem and span_elem:
                    label = strong_elem.get_text(strip=True).replace(":", "")
                    value = span_elem.get_text(strip=True)
                    details.append((label, value))
        

        if not details:
            for strong in soup.find_all("strong"):
                text = strong.get_text(strip=True).lower()
                if "pensão" in text or "pensao" in text:
                    span_elem = strong.find_next("span")
                    if span_elem:
                        label = strong.get_text(strip=True).replace(":", "")
                        value = span_elem.get_text(strip=True)
                        details.append((label, value))
        

        link_elem = soup.find("a", id="urlInstituidorPensao")
        if link_elem:
            href = link_elem.get("href", "")
            details.append(("Pension Institutor Detail URL", href))
        
        print("\n" + Fore.CYAN + "========== Pension Institutor Details ==========" + "\n")
        if details:
            print(tabulate(details, headers=["Information", "Detail"], tablefmt="fancy_grid"))
        else:
            print(Fore.YELLOW + "No additional information found.")
    except Exception as e:
        print(Fore.RED + f"Error fetching pension institutor details: {e}")
    finally:
        print("\n" + Fore.CYAN + "=============================================" + "\n")

def main():
    driver = None
    try:
        driver = create_driver()

        term = input(Fore.CYAN + "Enter CPF or name to search: ").strip()
        if not term:
            print(Fore.RED + "Invalid input!")
            sys.exit(1)

        results_list = get_search_results(driver, term)
        if not results_list:
            print(Fore.RED + "No results found for the provided term.")
            sys.exit(0)

        display_results(results_list)

        choice = input(Fore.CYAN + "\nEnter the number of the result you want to open: ").strip()
        if not choice.isdigit():
            print(Fore.RED + "Invalid input!")
            sys.exit(1)

        index = int(choice)
        if index < 1 or index > len(results_list):
            print(Fore.RED + "Number out of result range!")
            sys.exit(1)

        chosen_name, chosen_href, _, status = results_list[index - 1]
        print(Fore.YELLOW + f"\nOpening page for {chosen_name}...")
        driver.get(chosen_href)


        if "Servidor Público" in status:
            get_public_server_details(driver)
        elif "Favorecido" in status or "Favorecido de Recursos" in status:
            get_beneficiary_details(driver)
        elif "Instituidor" in status or "Pensão" in status or "Pensao" in status:
            get_pension_institutor_details(driver)
        else:
            get_benefit_details(driver)

    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
