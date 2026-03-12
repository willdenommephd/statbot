from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

from .apply_filters_exact import apply_filters_exact
from .ensure_filter_page import ensure_filter_page

# Function to extract text data and return it
def extract_text_data(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=None):
    logging.info(f"Extracting text data from {url}")
    
    # Text extraction doesn't use CSV download - extract normally
    return extract_text_data_single(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=middle_filters_as_column)

# Helper function to extract text data for a single geography
def extract_text_data_single(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=None):
    # Check if driver session is still valid
    try:
        current_url = driver.current_url
    except Exception as e:
        logging.error(f"Driver session invalid, cannot continue: {e}")
        raise
    
    # Only navigate to URL if we're not already there
    if current_url != url:
        driver.get(url)
        driver.implicitly_wait(10)
        
        # Check if we need to click "Add/Remove data" button to access filter page
        ensure_filter_page(driver)
    
    # Apply filters if provided
    if geography_method or geography_value or middle_filters or start_year or end_year:
        apply_filters_exact(driver, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=middle_filters_as_column)
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "p"))
    )
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    paragraphs = soup.find_all('p')

    data = []
    for paragraph in paragraphs:
        data.append([paragraph.get_text().strip()])
    return data