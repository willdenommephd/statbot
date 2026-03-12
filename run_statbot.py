import logging

from .apply_filters_exact import apply_filters_exact
from .extract_data_to_excel import extract_data_to_excel
from .read_urls_from_file import read_urls_from_file
from .statbotsearch import statbotsearch

#Function to run StatBot in either 'search' or 'extract' mode. This is the main function that orchestrates the entire process of searching for data tables and extracting them based on user input and filter settings.
def run_statbot(driver, mode, output_name=None, keyword=None, url=None, geography_method=None, geography_value=None, middle_filters=None, start_year=None, end_year=None, preset_filters=None, preset_data_type=None, file_path=None, middle_filters_as_column=False):
    """
    Main function to run StatBot in either 'search' or 'extract' mode.
    
    Args:
        mode: 'search' to perform search and extract links, 'extract' to apply filters and download data.
        keyword: Search term for 'search' mode.
        url: URL of the data table for 'extract' mode.
        geography_method: Method for selecting geography filter (e.g., 'keyword', 'bracket_number', 'level', 'level_all').
        geography_value: Value(s) for geography filter (format depends on method).
        middle_filters: List of dicts with 'name', 'method', 'value' for additional filters.
        start_year: Start year for reference period filter.
        end_year: End year for reference period filter.
        preset_filters: Pre-collected (geography_method, geography_value, middle_filters, start_year, end_year) tuple to skip prompting.
        preset_data_type: Pre-collected data type string to skip prompting.
        middle_filters_as_column: Boolean indicating whether middle filters should be added as columns in the Excel output.
    """
    if mode == 'search':
        if not keyword:
            logging.error("Keyword is required for search mode")
            return
        safe_keyword = keyword.replace('"', '').replace("'", '').replace(' ', '_')
        xlsx_name = f"{output_name or safe_keyword}.xlsx"
        # Determine .txt output path
        if file_path is not None:
            txt_name = file_path
        else:
            txt_name = f"{safe_keyword}_tables.txt"
        statbotsearch(driver, keyword, file_path=txt_name, existing_driver=driver)
        urls_titles_filters = read_urls_from_file(txt_name)
        if not urls_titles_filters:
            logging.warning(f"No search results found for keyword: '{keyword}'. Skipping extraction.")
            print(f"\nNo tables found for '{keyword}'. Skipping.")
            return
        # Extract filters from preset_filters tuple (must be provided by caller)
        if preset_filters is None:
            logging.error("preset_filters is required but was not provided")
            print("Error: Filter settings must be provided to run_statbot")
            return
        geography_method, geography_value, middle_filters, start_year, end_year = preset_filters
        data_type = preset_data_type if preset_data_type is not None else 'tables'
        updated = [
            (url, title, sheet, data_type, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column)
                for url, title, sheet in urls_titles_filters   # read_urls_from_file returns 3-tuples
            ]
        extract_data_to_excel(driver, updated, xlsx_name, middle_filters_as_column=middle_filters_as_column)
    elif mode == 'extract':
        if not url:
            logging.error("URL is required for extract mode")
            return
        # Navigate to the URL and apply filters
        try:
            driver.get(url)
            apply_filters_exact(driver, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=middle_filters_as_column)
            # After applying filters, you would add code here to click the download button and handle the downloaded file
        except Exception as e:
            logging.error(f"Error during extraction: {e}")
    else:
        logging.error("Invalid mode. Use 'search' or 'extract'.")