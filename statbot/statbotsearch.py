import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from .find_chrome import find_chrome
from .find_chromedriver import find_chromedriver
from selenium.webdriver.support.ui import WebDriverWait

def statbotsearch(driver, search_term, file_path="output_links.txt", existing_driver=None):
    """
    This function takes a search term, navigates to the StatCan website, performs the search, and extracts the relevant data.
    """
    _owns_driver = existing_driver is None
    if existing_driver is not None:
        driver = existing_driver
    else:
        # Setup Chrome options for headless operation
        chrome_options = Options()
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')

        # Find local Chrome and ChromeDriver
        chromedriver_path = find_chromedriver()
        chrome_path = find_chrome()
        if chrome_path:
            chrome_options.binary_location = chrome_path
        if chromedriver_path:
            driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
        else:
            # Fallback to ChromeDriverManager if not found locally
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        driver.get("https://www150.statcan.gc.ca/n1/en/type/data?MM=1")

        # Step 2: Enter the search term and submit the search.
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)  # Simulate pressing Enter to submit the search

        # Step 3: Navigate through the search results tabs to select the Tables tab.
        for _ in range(3):
            try:
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "tables-lnk"))
                )
                driver.find_element(By.ID, "tables-lnk").click()
                break
            except StaleElementReferenceException:
                time.sleep(1)
        else:
            print("Could not click tables-lnk due to repeated staleness.")
        time.sleep(2)  # Wait for the tables tab to load

        # Step 4: Extract the relevant links to the data tables from the search results.
        results = []
        scraped_links = set()
        while True:
            try:
                tables_details = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "tables"))
                )
                table_items = tables_details.find_elements(By.CSS_SELECTOR, "li.ndm-item a")
                for link in table_items:
                    try:
                        href = link.get_attribute("href")
                        title = link.text.strip()
                        worksheet = ""
                        if href and "/t1/tbl1/en/" in href and href not in scraped_links:
                            scraped_links.add(href)
                            results.append(f"{href};{title};{worksheet}")
                    except StaleElementReferenceException:
                        continue  # Skip stale links
            except StaleElementReferenceException:
                time.sleep(1)
                continue
            except Exception:
                break

            # Pagination logic
            try:
                next_btn = tables_details.find_element(By.CSS_SELECTOR, 'a[rel="next"]')
                if not next_btn.is_displayed() or not next_btn.is_enabled():
                    break
            except StaleElementReferenceException:
                time.sleep(1)
                continue
            except Exception:
                break

            time.sleep(2)
            try:
                next_btn.click()
            except StaleElementReferenceException:
                continue
            # Re-fetch table_items after clicking next
            WebDriverWait(driver, 30).until(
                lambda d: d.find_element(By.ID, "tables").find_elements(By.CSS_SELECTOR, "li.ndm-item a")
            )
            time.sleep(2)

        # Step 5: Write the extracted results to a .txt file.
        with open(file_path, 'w', encoding='utf-8') as f:
            for i, result in enumerate(results, 1):
                url_part, title_part, _ = result.split(';', 2)
                f.write(f"{url_part};{title_part};Sheet {i}\n")

        print(f"Saved {len(results)} table links to {file_path}")
        if _owns_driver:
            driver.quit()
    except Exception as e:
        print(e)
    finally:
        if _owns_driver:
            driver.quit()