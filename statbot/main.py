import os
import platform
import sys
import signal
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
import re

from .find_chrome import find_chrome
from .find_chromedriver import find_chromedriver
from .extract_data_to_excel import extract_data_to_excel, extract_data_to_excel_in_batches
from .handle_interrupt import handle_interrupt
from .open_file import open_file
from .read_urls_from_file import read_urls_from_file
from .run_statbot import run_statbot
from .update_excel_with_new_year import update_excel_with_new_year
from .get_filter_settings import get_filter_settings
from .get_data_type import get_data_type
from .save_preset_parameters import save_preset_parameters
from .load_preset_parameters import load_preset_parameters
from .apply_filters_exact import apply_filters_exact

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), 'statcan_downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
logging.info(f"Using download directory: {DOWNLOAD_DIR}")

signal.signal(signal.SIGINT, handle_interrupt)

# Main function to get user input and run the extraction
def main():
    global driver

    # Set up Chrome options to use custom download directory
    chrome_options = Options()
    # Set Chrome binary location - search for Chrome in common locations
    chrome_path = find_chrome()
    if chrome_path:
        chrome_options.binary_location = chrome_path
        logging.info(f"Using Chrome at: {chrome_path}")
    else:
        # Fallback to default locations if not found
        system = platform.system()
        if system == 'Darwin':  # macOS
            chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif system == 'Windows':
            chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        # Linux usually finds Chrome automatically, no need to set binary_location
        logging.info(f"Using default Chrome location for {system}")
    # Add arguments to prevent download prompts
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    # Add arguments to suppress Chrome error messages and warnings
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--silent")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0
    }
    chrome_options.add_experimental_option("prefs", prefs)
    #The safebrowing.enabled option is set to True to prevent Chrome from blocking downloads that it deems unsafe. Note that this is using Chrome's security standards, not PS or GC.
    
    # Initialize Selenium WebDriver with extended timeout and custom download directory
    print("Starting Chrome browser...")
    try:
        # Try to find local ChromeDriver, fall back to webdriver_manager
        local_chromedriver = find_chromedriver()
        
        if local_chromedriver:
            print(f"Using local ChromeDriver at: {local_chromedriver}")
            service = Service(local_chromedriver)
        else:
            print("Local ChromeDriver not found. Using webdriver_manager to download...")
            service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Force download behavior using Chrome DevTools Protocol (more reliable than prefs)
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": DOWNLOAD_DIR
        })
        
        # Set page load timeout to 5 minutes for large tables
        driver.set_page_load_timeout(300)
        #5 minutes was used as a timeout time because StatCan tables can be very large and take a long time to load.
        #Depending on your internet speed and the size of the table, you may want to adjust this value.
        print("Browser started successfully.\n")
    except Exception as e:
        print(f"Error: Could not start Chrome browser. Make sure Chrome is installed.")
        logging.error(f"Failed to initialize Chrome driver: {e}")
        sys.exit(1)

    # Display welcome message
    print("\n" + "="*60)
    print(" Hi! \U0001F44B I'm StatBot, your personal StatCan data extraction assistant \U0001F916" "\n")
    print(" Just tell me what links you want to extract data from, and I'll help you get the data.")
    print(" You can also save and load presets to streamline your workflow!")
    print("="*60 + "\n")

    # Display a let's get started message.
    print(" \u2728 Let's get started! \u2728")
    print("------------------------------------------------------------------")
    
    # Get output file name from user
    output_file = input("Enter the name for your output Excel file (without .xlsx extension): ").strip()
    if not output_file:
        print("Error: Output file name is required.")
        sys.exit(1)

    # Get the mode that the user wants to run the program in.
    mode = input("Do you want to run a search and extract or just an extract? (search/extract): ").strip().lower()
    if mode == 'search':
        print("\nYou have selected SEARCH AND EXTRACT. I will search for data tables matching your keyword(s) and extract the data to an Excel file.")
    else:
        print("\nYou have selected EXTRACT-ONLY. I will extract data to an Excel file based on your specified URLs.")   

    if mode == 'search':
        # ...existing code for search keyword and filter selection...
        print("  Tip: Use commas to run separate searches (e.g. crime, homicide)")
        print("  Tip: Use [brackets] to combine terms into one search (e.g. [crime, homicide])")
        keywords = input("Enter your search keyword(s): ").strip()
        if not keywords:
            print("Error: At least one search keyword is required.")
            sys.exit(1)
        keyword_list = []
        remaining = keywords
        last_end = 0
        for match in re.finditer(r'\[([^\]]+)\]', remaining):
            before = remaining[last_end:match.start()]
            for part in before.split(','):
                part = part.strip()
                if part:
                    keyword_list.append(part)
            inner_terms = [t.strip() for t in match.group(1).split(',') if t.strip()]
            keyword_list.append(' '.join(inner_terms))
            last_end = match.end()
        for part in remaining[last_end:].split(','):
            part = part.strip()
            if part:
                keyword_list.append(part)
        logging.info(f"Search mode selected with keywords: {keyword_list}")

        keyword_filters = {}
        if len(keyword_list) > 1:
            same_filters = input("Apply the same filters to all searches? (yes/no): ").strip().lower()
            if same_filters in ('yes', 'y'):
                preset_filters = get_filter_settings()
                preset_data_type = get_data_type()
                save_as_preset = input("Do you want to save these filter settings as a preset for future use? (yes/no): ").strip().lower()
                if save_as_preset in ('yes', 'y'):
                    preset_filename = input("Enter a name for the preset file (without extension): ").strip()
                    if preset_filename:
                        geo_method, geo_value, mid_filters, sy, ey = preset_filters
                        preset_path = f"{preset_filename}.txt"
                        save_preset_parameters(preset_path, None,
                                             url_filters_list=[(1, geo_method, geo_value, mid_filters or [], sy, ey, preset_data_type)],
                                             common_geography=(geo_method, geo_value),
                                             common_data_type=preset_data_type)
                        print(f"Preset saved to: {preset_path}")
                for keyword in keyword_list:
                    keyword_filters[keyword] = (preset_filters, preset_data_type)
            else:
                for keyword in keyword_list:
                    print(f"\n--- Filter settings for keyword: '{keyword}' ---")
                    preset_filters = get_filter_settings()
                    preset_data_type = get_data_type()
                    keyword_filters[keyword] = (preset_filters, preset_data_type)
        else:
            keyword = keyword_list[0]
            preset_filters = get_filter_settings()
            preset_data_type = get_data_type()
            keyword_filters[keyword] = (preset_filters, preset_data_type)
            save_as_preset = input("Do you want to save these filter settings as a preset for future use? (yes/no): ").strip().lower()
            if save_as_preset in ('yes', 'y'):
                preset_filename = input("Enter a name for the preset file (without extension): ").strip()
                if preset_filename:
                    geo_method, geo_value, mid_filters, sy, ey = preset_filters
                    preset_path = f"{preset_filename}.txt"
                    save_preset_parameters(preset_path, None,
                                         url_filters_list=[(1, geo_method, geo_value, mid_filters or [], sy, ey, preset_data_type)],
                                         common_geography=(geo_method, geo_value),
                                         common_data_type=preset_data_type)
                    print(f"Preset saved to: {preset_path}")

        # Prompt for middle filters as columns after all filters are specified, before update mode
        middle_filters_as_column = []
        col_filters_input = input("Enter the names of any middle filters you want as columns (comma-separated, leave blank for all as rows): ").strip()
        if col_filters_input:
            middle_filters_as_column = [name.strip() for name in col_filters_input.split(',') if name.strip()]

        # Delete existing output file so this run starts fresh (keywords within this run will append)
        xlsx_path = f"{output_file}.xlsx"
        if os.path.exists(xlsx_path):
            os.remove(xlsx_path)
            logging.info(f"Removed existing output file for fresh run: {xlsx_path}")

        xlsx_path = f"{output_file}.xlsx"
        output_dir = os.path.dirname(os.path.abspath(xlsx_path))
        for keyword in keyword_list:
            preset_filters, preset_data_type = keyword_filters[keyword]
            safe_keyword = keyword.replace('"', '').replace("'", '').replace(' ', '_')
            links_txt_path = os.path.join(output_dir, f"{safe_keyword}_tables.txt")
            run_statbot(driver, 'search', keyword=keyword, output_name=output_file,
                        preset_filters=preset_filters, preset_data_type=preset_data_type, file_path=links_txt_path, middle_filters_as_column=middle_filters_as_column)
        return


    if mode == 'extract':
        # Get input file from user (always ask for this)
        input_file = input("\nEnter the path to your input file (or 'manual' for manual entry): ").strip()
        if not input_file:
            logging.error("Input file path is required.")
            print("Please provide an input file path or type 'manual'.")
            return

        if input_file.lower() == 'manual':
            urls_titles_filters = []
            while True:
                url = input("Enter URL (or 'done' to finish): ").strip()
                if url.lower() == 'done':
                    break
                table_title = input("Enter table title for the URL: ").strip()
                sheet_title = input("Enter sheet title for the URL: ").strip()
                urls_titles_filters.append((url, table_title, sheet_title))

            # Save manually entered URLs to a file for future reference
            if urls_titles_filters:
                manual_file = "manual_urls.txt"
                try:
                    with open(manual_file, 'w', encoding='utf-8') as f:
                        for url, table_title, sheet_title in urls_titles_filters:
                            f.write(f"{url};{table_title};{sheet_title}\n")
                    input_file = manual_file
                    print(f"\nManually entered URLs saved to: {manual_file}")
                except Exception as e:
                    logging.warning(f"Could not save manual URLs to file: {e}")
                    input_file = None
        else:
            # User provided a file path
            if not os.path.exists(input_file):
                logging.error("File does not exist. Please check the path and try again.")
                return
            urls_titles_filters = read_urls_from_file(input_file)

    # Optional: Get batch size (or use default)
    batch_size_input = input("Enter batch size for processing URLs (default: 100): ").strip()
    batch_size = int(batch_size_input) if batch_size_input else 100

    try:
        # Check if user wants to update an existing file
        update_mode = input("\nDo you want to UPDATE an existing Excel file with a new year? (yes/no): ").strip().lower() == 'yes'

        # Check if user wants to use a preset file for filter configurations
        use_preset = input("\nDo you want to use a preset file for filter configurations? (yes/no): ").strip().lower() == 'yes'

        if use_preset:
            preset_file = input("Enter the path to the preset file: ").strip()
            if os.path.exists(preset_file):
                preset_data = load_preset_parameters(preset_file)
                if preset_data:
                    print(f"Loaded preset from: {preset_file}")

                    # Build filter configurations for each URL
                    default_filters = preset_data['default_filters']
                    url_specific = preset_data['url_specific_filters']
                    apply_filters = preset_data['apply_filters']

                    updated_urls_titles_filters = []
                    for idx, (url, table_title, sheet_title) in enumerate(urls_titles_filters):
                        # Start with default filters (use copy for lists to avoid mutation)
                        geography_method = default_filters['geography_method']
                        geography_value = default_filters['geography_value']
                        data_type = default_filters['data_type']
                        start_year = default_filters['start_year']
                        end_year = default_filters['end_year']

                        # Check for URL-specific overrides
                        url_filter_key = f"url{idx+1}_filters"
                        logging.info(f"Processing URL {idx+1}: {url[:80]}... Looking for section: {url_filter_key}")
                        if url_filter_key in url_specific:
                            overrides = url_specific[url_filter_key]
                            geography_method = overrides.get('geography_method', geography_method)
                            geography_value = overrides.get('geography_value', geography_value)

                            # Build middle_filters - support two formats:
                            # 1. filter_1_name, filter_1_method, filter_1_value (explicit format)
                            # 2. FilterName = method:value (compact format)
                            middle_filters = []

                            # First try explicit format
                            if any(k.startswith('filter_') and k.endswith('_name') for k in overrides):
                                filter_idx = 1
                                while f'filter_{filter_idx}_name' in overrides:
                                    middle_filters.append({
                                        'name': overrides[f'filter_{filter_idx}_name'],
                                        'method': overrides.get(f'filter_{filter_idx}_method', 'keyword'),
                                        'value': overrides.get(f'filter_{filter_idx}_value', '')
                                    })
                                    filter_idx += 1
                                logging.info(f"URL {idx+1}: Using {len(middle_filters)} URL-specific filters (explicit format): {[f['name'] for f in middle_filters]}")
                            else:
                                # Try compact format (FilterName = method:value)
                                reserved_keys = {'geography_method', 'geography_value', 'data_type', 'start_year', 'end_year'}
                                has_compact_filters = False
                                for key, value in overrides.items():
                                    if key not in reserved_keys and not key.startswith('filter_') and ':' in str(value):
                                        try:
                                            method, filter_value = value.split(':', 1)
                                            middle_filters.append({
                                                'name': key,
                                                'method': method.strip(),
                                                'value': filter_value.strip()
                                            })
                                            has_compact_filters = True
                                        except ValueError:
                                            logging.warning(f"Could not parse filter format for {key} = {value}")

                                if has_compact_filters:
                                    logging.info(f"URL {idx+1}: Using {len(middle_filters)} URL-specific filters (compact format): {[f['name'] for f in middle_filters]}")
                                else:
                                    # No URL-specific filters at all, use defaults
                                    middle_filters = [f.copy() for f in default_filters['middle_filters']]
                                    logging.info(f"URL {idx+1}: No URL-specific filters found, using {len(middle_filters)} default filters")

                            data_type = overrides.get('data_type', data_type)
                            start_year = overrides.get('start_year', start_year)
                            end_year = overrides.get('end_year', end_year)
                        else:
                            # No URL-specific section, use all defaults including middle_filters
                            middle_filters = [f.copy() for f in default_filters['middle_filters']]
                            logging.info(f"URL {idx+1}: No [{url_filter_key}] section found, using {len(middle_filters)} default filters")

                        updated_urls_titles_filters.append((url, table_title, sheet_title, data_type, geography_method, geography_value, middle_filters, start_year, end_year))

                    # If in update mode, ask for the new year and update filters
                    if update_mode:
                        print("\n--- UPDATE MODE: Add New Year ---")
                        print("Note: Enter the EXACT text as it appears in the dropdown")
                        print("Examples: '2025', '2025/2026', '2025-2026', 'Q4 2025', etc.")
                        new_year = input("What year would you like to add? ").strip()

                        print("\n--- INSERT POSITION ---")
                        insert_position = input("Insert new year at START or END of year columns? (start/end) [default: end]: ").strip().lower()
                        if insert_position not in ['start', 'end']:
                            insert_position = 'end'

                        # Update all entries to use the new year
                        updated_with_new_year = []
                        for url, table_title, sheet_title, data_type, geo_method, geo_value, mid_filters, _, _ in updated_urls_titles_filters:
                            updated_with_new_year.append((url, table_title, sheet_title, data_type, geo_method, geo_value, mid_filters, new_year, new_year))
                        updated_urls_titles_filters = updated_with_new_year
                else:
                    logging.error("Failed to load preset. Exiting.")
                    return
            else:
                logging.error(f"Preset file does not exist: '{preset_file}'")
                logging.error(f"Current working directory: {os.getcwd()}")
                print(f"\nCould not find preset file: {preset_file}")
                print(f"Make sure the file exists and the path is correct.")
                return
        else:
            # No preset - will prompt for filters
            apply_filters = input("Do you want to apply filters? (yes/no): ").strip().lower() == 'yes'
            apply_same_filters = False

            # Initialize filter variables
            geography_method = geography_value = middle_filters = None
            start_year = end_year = None
            data_type = 'tables'
            insert_position = 'end'  # Default for update mode

            if apply_filters:
                apply_same_filters = input("Do you want to apply the same filters to all links? (yes/no): ").strip().lower() == 'yes'

                # If applying same filters to all, get them once upfront
                if apply_same_filters:
                    filter_result = get_filter_settings(update_mode=update_mode)
                    if update_mode:
                        geography_method, geography_value, middle_filters, start_year, end_year, insert_position = filter_result
                    else:
                        geography_method, geography_value, middle_filters, start_year, end_year = filter_result
                        insert_position = None
                    data_type = get_data_type()

                    # Ask if user wants to save this as a preset
                    save_as_preset = input("Do you want to save these settings as a preset for future use? (yes/no): ").strip().lower() == 'yes'
                    if save_as_preset:
                        preset_filename = input("Enter a name for the preset file (without extension): ").strip()
                        preset_path = f"{preset_filename}.txt"
                        url_filters_list = [
                            (idx+1, geography_method, geography_value, middle_filters, start_year, end_year, data_type)
                            for idx in range(len(urls_titles_filters))
                        ]
                        save_preset_parameters(preset_path, input_file, url_filters_list,
                                               common_geography=(geography_method, geography_value),
                                               common_data_type=data_type)

            updated_urls_titles_filters = []
            for url, table_title, sheet_title in urls_titles_filters:
                logging.info(f"Settings for {sheet_title}:")

                # If applying filters but not same filters for all, prompt for each URL
                if apply_filters and not apply_same_filters:
                    filter_result = get_filter_settings(update_mode=update_mode)
                    if update_mode:
                        geography_method, geography_value, middle_filters, start_year, end_year, insert_position = filter_result
                    else:
                        geography_method, geography_value, middle_filters, start_year, end_year = filter_result
                        insert_position = None
                    data_type = get_data_type()

                updated_urls_titles_filters.append((url, table_title, sheet_title, data_type, geography_method, geography_value, middle_filters, start_year, end_year))

            # After all filters are set, ask if user wants to save as preset
            if apply_filters and not apply_same_filters:
                save_as_preset = input("\nDo you want to save these settings as a preset for future use? (yes/no): ").strip().lower() == 'yes'
                if save_as_preset:
                    preset_filename = input("Enter a name for the preset file (without extension): ").strip()
                    preset_path = f"{preset_filename}.txt"
                    url_filters_list = []
                    for idx, entry in enumerate(updated_urls_titles_filters):
                        url_filters_list.append((idx+1, entry[4], entry[5], entry[6], entry[7], entry[8], entry[3]))

                    all_geo = [(entry[4], entry[5]) for entry in updated_urls_titles_filters]
                    common_geography = all_geo[0] if len(set(all_geo)) == 1 else None
                    all_data_types = [entry[3] for entry in updated_urls_titles_filters]
                    common_data_type = all_data_types[0] if len(set(all_data_types)) == 1 else 'tables'
                    save_preset_parameters(preset_path, input_file, url_filters_list, common_geography, common_data_type)

        # Prompt for middle filters as columns after all filters are specified
        col_filters_input = input("\nEnter the names of any middle filters you want as columns (comma-separated, leave blank for all as rows): ").strip()
        middle_filters_as_column = [name.strip() for name in col_filters_input.split(',') if name.strip()] if col_filters_input else []

        output_excel = output_file + ".xlsx"

        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath(output_excel))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        if update_mode:
            # Update mode: add new year to existing file
            if updated_urls_titles_filters:
                new_year = updated_urls_titles_filters[0][7]  # start_year is the new year
                success = update_excel_with_new_year(driver, output_excel, updated_urls_titles_filters, new_year, insert_position, middle_filters_as_column=middle_filters_as_column)
                if success:
                    open_file(output_excel)
            else:
                print("No URLs to process.")
        else:
            # Normal mode: create new file or overwrite
            if os.path.exists(output_excel):
                os.remove(output_excel)
                logging.info(f"Removed existing output file for fresh run: {output_excel}")
            if len(updated_urls_titles_filters) > batch_size:
                extract_data_to_excel_in_batches(driver, updated_urls_titles_filters, output_excel, batch_size, middle_filters_as_column=middle_filters_as_column)
            else:
                extract_data_to_excel(driver, updated_urls_titles_filters, output_excel, middle_filters_as_column=middle_filters_as_column)

            # Open the Excel file automatically
            open_file(output_excel)
    except KeyboardInterrupt:
        print("\n\nProgram cancelled by user.")
        logging.info("Program cancelled by user via keyboard interrupt")
        try:
            if driver is not None:
                driver.quit()
        except Exception:
            pass
        sys.exit(0)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        try:
            if driver is not None:
                driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        handle_interrupt()