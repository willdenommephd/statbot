from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

from .apply_filters_exact import apply_filters_exact
from .ensure_filter_page import ensure_filter_page

def extract_text_data(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=None):
        """
    Extract paragraph text from a target page after optionally applying geography and time filters.

    This is a thin wrapper around `extract_text_data_single()` that logs the operation and
    performs the extraction using the provided Selenium WebDriver session.

    Parameters
    ----------
    driver : selenium.webdriver.remote.webdriver.WebDriver
        Active Selenium WebDriver used to navigate to the page and retrieve HTML.
    url : str
        Target URL to load (if not already on the page).
    geography_method : Any
        Geography filter method passed through to `apply_filters_exact` (e.g., type of geography selector).
    geography_value : Any
        Geography filter value passed through to `apply_filters_exact` (e.g., state/county/city name or code).
    middle_filters : Any
        Additional filters passed through to `apply_filters_exact` (often category/series filters).
    start_year : Any
        Start year for a time-range filter passed through to `apply_filters_exact`.
    end_year : Any
        End year for a time-range filter passed through to `apply_filters_exact`.
    middle_filters_as_column : Any, optional
        Passed through to `apply_filters_exact`; controls whether middle filters are represented
        as a column (exact behavior defined by `apply_filters_exact`).

    Returns
    -------
    list[list[str]]
        A list of single-item rows, where each row contains the stripped text of one `<p>` element
        from the rendered page, e.g. `[[paragraph1], [paragraph2], ...]`.
    """
    logging.info(f"Extracting text data from {url}")
    
    # Text extraction doesn't use CSV download - extract normally
    return extract_text_data_single(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=middle_filters_as_column)

# Helper function to extract text data for a single geography
def extract_text_data_single(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=None):
     """
    Load a page (if needed), optionally apply filters, then scrape and return all paragraph text.

    The function:
    1) Verifies the Selenium session is valid by accessing `driver.current_url`.
    2) Navigates to `url` if not already there and ensures the filter UI is accessible.
    3) Applies geography/middle/year filters via `apply_filters_exact` when any are provided.
    4) Waits until at least one `<p>` element is present, then parses the HTML and extracts text.

    Parameters
    ----------
    driver : selenium.webdriver.remote.webdriver.WebDriver
        Active Selenium WebDriver used to navigate to the page and retrieve HTML.
    url : str
        Target URL to load (if not already on the page).
    geography_method : Any
        Geography filter method passed through to `apply_filters_exact`.
    geography_value : Any
        Geography filter value passed through to `apply_filters_exact`.
    middle_filters : Any
        Additional filters passed through to `apply_filters_exact`.
    start_year : Any
        Start year for a time-range filter passed through to `apply_filters_exact`.
    end_year : Any
        End year for a time-range filter passed through to `apply_filters_exact`.
    middle_filters_as_column : Any, optional
        Passed through to `apply_filters_exact`; controls whether middle filters are represented
        as a column (exact behavior defined by `apply_filters_exact`).

    Returns
    -------
    list[list[str]]
        A list of single-item rows, where each row contains the stripped text of one `<p>` element
        from the rendered page.

    Raises
    ------
    Exception
        Re-raises any exception encountered when checking `driver.current_url`, which indicates
        the driver session may be invalid and extraction cannot continue.
    """
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
