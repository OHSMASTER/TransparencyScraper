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
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--log-level=3")

    service = Service(log_path=os.devnull)
    return webdriver.Chrome(service=service, options=chrome_options)

def get_search_results(driver, term):
    search_url = (
        "https://portaldatransparencia.gov.br/pessoa-fisica/busca/"
        f"lista?termo={term}&pagina=1&tamanhoPagina=10"
    )
    driver.get(search_url)
    wait = WebDriverWait(driver, 10)
    
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.link-busca-nome")))
    except:
        print(Fore.RED + "No results found on the search page.")
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
        sibling_divs = [
            sib for sib in parent_div.find_next_siblings("div")
            if sib.get_text(strip=True)
        ]
        
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

def get_server_details(driver):
    try:
        wait = WebDriverWait(driver, 10)
        info_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.box-ficha__resultados"))
        )
        html_content = info_box.get_attribute("innerHTML")
        soup = BeautifulSoup(html_content, "html.parser")
        links_div = soup.find("div", id="vinculos")
        
        if not links_div:
            print(Fore.YELLOW + "No linkage data found in HTML.")
            return
        
        info_blocks = links_div.find_all("div", class_="col-sm-12 col-md-6")
        details = []
        for block in info_blocks:
            strong_elem = block.find("strong")
            span_elem = block.find("span")
            if strong_elem and span_elem:
                label = strong_elem.get_text(strip=True).replace(":", "")
                value = span_elem.get_text(strip=True)
                details.append((label, value))
        
        print("\n" + Fore.CYAN + "========== Public Server Details ==========" + "\n")
        if details:
            print(tabulate(details, headers=["Information", "Detail"], tablefmt="fancy_grid"))
        else:
            print(Fore.YELLOW + "No additional information found.")
    except Exception as e:
        print(Fore.RED + f"An error occurred while fetching server details: {e}")

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
            print(Fore.RED + "No results found for the entered term.")
            sys.exit(0)
        
        display_results(results_list)
        choice = input(Fore.CYAN + "\nEnter the number of the result you want to open: ").strip()
        if not choice.isdigit():
            print(Fore.RED + "Invalid input!")
            sys.exit(1)
        
        index = int(choice)
        if index < 1 or index > len(results_list):
            print(Fore.RED + "Number out of range!")
            sys.exit(1)
        
        chosen_name, chosen_href, _, status = results_list[index - 1]
        print(Fore.YELLOW + f"\nOpening the page of {chosen_name}...")
        driver.get(chosen_href)
        
        if "Servidor Público" in status:
            get_server_details(driver)
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
