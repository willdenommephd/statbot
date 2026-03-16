import os
import time
import tempfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import glob
import csv
from bs4 import BeautifulSoup

from .add_percentage_column import add_percentage_column
from .apply_filters_exact import apply_filters_exact
from .ensure_filter_page import ensure_filter_page

# Set up download directory (same as main.py)
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), 'statcan_downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to extract table data and return it
def extract_table_data(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=None):
    logging.info(f"Extracting table data from {url}")
    logging.info(f"Filters to apply: geography={geography_value}, middle_filters={[f['name'] for f in middle_filters]}, years={start_year}-{end_year}")
    
    # CSV download method handles all data automatically - no need to split by geography
    return extract_table_data_single(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=middle_filters_as_column)

# Helper function to download CSV and extract all data (bypasses display limit)
def extract_via_download(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=None):
    """
    Download the full CSV from StatCan to bypass the 148-row display limit.
    Returns data in the same format as extract_table_data_single.
    """
    try:
        # Navigate and apply filters
        driver.get(url)
        driver.implicitly_wait(10)
        
        # Check if we need to click "Add/Remove data" button to access filter page
        ensure_filter_page(driver)
        
        if geography_method or geography_value or middle_filters or start_year or end_year:
            apply_filters_exact(driver, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=middle_filters_as_column)
        
        # Wait for table to render
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        time.sleep(3)
        
        # Find and click the Download Options button (two-step process)
        logging.info("Clicking Download Options button to get full dataset...")
        try:
            # Wait for page to be fully loaded (StatCan is slow)
            time.sleep(5)
            
            # Step 1: Click "Download options" button using exact ID
            download_options_button = None
            selectors = [
                (By.ID, "downloadOverlayLink"),  # Exact ID from HTML
                (By.XPATH, "//a[@id='downloadOverlayLink']"),
                (By.XPATH, "//a[contains(@onclick, 'openDownloadOverlay')]"),
                (By.XPATH, "//a[contains(text(), 'Download options')]"),
            ]
            
            for by, selector in selectors:
                try:
                    download_options_button = driver.find_element(by, selector)
                    if download_options_button and download_options_button.is_displayed():
                        logging.info(f"Found Download Options button with selector: {selector}")
                        break
                    else:
                        download_options_button = None
                except Exception as e:
                    logging.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not download_options_button:
                logging.warning("Could not find Download Options button, falling back to table scraping")
                return None
            
            # Scroll button into view and click it
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_options_button)
            time.sleep(1)
            
            # Try clicking with JavaScript first (more reliable)
            try:
                driver.execute_script("arguments[0].click();", download_options_button)
                logging.info("Clicked Download Options button (JavaScript)")
            except:
                # Fallback to regular click
                download_options_button.click()
                logging.info("Clicked Download Options button (regular)")
            
            # Wait for overlay to appear (StatCan is slow)
            time.sleep(5)
            
            # Step 2: Click "Download as displayed" CSV option using exact ID
            csv_option = None
            csv_selectors = [
                (By.ID, "downloadAsDisplay"),  # Exact ID from HTML
                (By.XPATH, "//a[@id='downloadAsDisplay']"),
                (By.XPATH, "//a[contains(@href, '.csv') and contains(text(), 'Download as displayed')]"),
                (By.XPATH, "//section[@id='downloadButtonOverlay']//a[contains(@href, '.csv')]"),
            ]
            
            for by, selector in csv_selectors:
                try:
                    csv_option = driver.find_element(by, selector)
                    if csv_option and csv_option.is_displayed():
                        logging.info(f"Found CSV option with selector: {selector}")
                        break
                    else:
                        csv_option = None
                except Exception as e:
                    logging.debug(f"CSV selector {selector} failed: {e}")
                    continue
            
            if not csv_option:
                logging.warning("Could not find CSV download option, falling back to table scraping")
                return None
            
            # Use the global download directory configured in Chrome options
            download_dir = DOWNLOAD_DIR
            logging.info(f"Monitoring download directory: {download_dir}")
            
            # Get list of CSV files before download
            before_files = set(glob.glob(os.path.join(download_dir, "*.csv")))
            
            # Click CSV download option
            driver.execute_script("arguments[0].click();", csv_option)
            logging.info("Clicked CSV download option, waiting for JavaScript to generate CSV...")
            
            # Wait a few seconds for JavaScript to process and trigger download
            time.sleep(3)
            
            # Wait for new CSV file to appear (max 180 seconds - StatCan can be very slow)
            new_file = None
            logging.info("Waiting up to 180 seconds for CSV download to complete...")
            for i in range(180):
                time.sleep(1)
                if i % 15 == 0 and i > 0:
                    logging.info(f"Still waiting for download... {i} seconds elapsed")
                
                # Check for .crdownload files (download in progress)
                crdownload_files = glob.glob(os.path.join(download_dir, "*.crdownload"))
                if crdownload_files:
                    logging.debug(f"Download in progress... (.crdownload file detected)")
                
                # Check for new CSV files
                after_files = set(glob.glob(os.path.join(download_dir, "*.csv")))
                new_files = after_files - before_files
                if new_files:
                    potential_file = list(new_files)[0]
                    # Make sure file exists and is not a partial download
                    if os.path.exists(potential_file) and not potential_file.endswith(('.crdownload', '.tmp', '.part')):
                        # Extra check: make sure file size is stable (download complete)
                        try:
                            initial_size = os.path.getsize(potential_file)
                            time.sleep(0.5)
                            final_size = os.path.getsize(potential_file)
                            if initial_size == final_size and final_size > 0:
                                new_file = potential_file
                                logging.info(f"Download completed after {i+1} seconds: {os.path.basename(new_file)}")
                                break
                        except:
                            continue
            
            if not new_file:
                logging.warning("Download timed out, falling back to table scraping")
                return None
            
            logging.info(f"Downloaded CSV: {new_file}")
            
            # Parse the CSV file
            data_rows = []
            with open(new_file, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    data_rows.append(row)
            
            # Delete the downloaded file
            try:
                os.remove(new_file)
                logging.info(f"Deleted temporary download: {new_file}")
            except:
                pass
            
            logging.info(f"Extracted {len(data_rows)} rows from CSV download")
            
            # Add percentage change column to CSV data
            data_rows = add_percentage_column(data_rows)
            
            return data_rows
            
        except Exception as e:
            logging.warning(f"Error during download: {e}, falling back to table scraping")
            return None
            
    except Exception as e:
        logging.error(f"Error in extract_via_download: {e}")
        return None
    

# Helper function to extract data for a single geography (or combined if not level_all)
def extract_table_data_single(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=None):
    # Try downloading CSV first to bypass display limit
    downloaded_data = extract_via_download(driver, url, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=middle_filters_as_column)
    if downloaded_data:
        logging.info(f"Successfully extracted {len(downloaded_data)} rows via CSV download")
        return downloaded_data
    
    # Fall back to HTML table scraping if download fails
    logging.info("Falling back to HTML table scraping...")
    
    # Check if driver session is still valid
    try:
        current_url = driver.current_url
    except Exception as e:
        logging.error(f"Driver session invalid, cannot continue: {e}")
        raise
    
    # Always navigate to URL to ensure fresh page
    logging.debug(f"About to navigate to URL: '{url}' (type: {type(url)})")
    driver.get(url)
    driver.implicitly_wait(10)
    
    # Check if we need to click "Add/Remove data" button to access filter page
    ensure_filter_page(driver)
    
    # Apply filters if provided
    if geography_method or geography_value or middle_filters or start_year or end_year:
        apply_filters_exact(driver, geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=middle_filters_as_column)
    
    # Wait for the page to load - longer timeout for level_all method
    wait_timeout = 30 if geography_method in ['level', 'level_all'] else 10
    WebDriverWait(driver, wait_timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    
    # For level/level_all methods with multiple geographies, wait longer and scroll through table
    if geography_method in ['level', 'level_all']:
        logging.info("Multiple geographies selected - waiting for full table to render (extended wait time)...")
        time.sleep(10)  # Increased from 3 to 10 seconds
        
        # Scroll to bottom of page to trigger any lazy-loading of table rows
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        except Exception as e:
            logging.warning(f"Could not scroll page: {e}")
        
        # Count table rows to verify all geographies are present
        try:
            table = driver.find_element(By.ID, 'simpleTable')
            rows = table.find_elements(By.TAG_NAME, 'tr')
            logging.info(f"Final table has {len(rows)} rows before extraction")
            
            # Debug: Save table HTML to file
            table_html = table.get_attribute('outerHTML')
            debug_file = 'debug_table.html'
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(table_html)
            logging.info(f"Saved table HTML to {debug_file} for inspection")
            
            # Also save full page source
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logging.info("Saved full page HTML to debug_page.html")
        except Exception as e:
            logging.warning(f"Could not count final rows: {e}")
    
    # Get the updated page source after filters are applied
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tables = soup.find_all('table')

    data = []
    data_rows = []  # Store tuples of (row_data, pending_headers_used) for alignment logic
    year_header_row_idx = None
    
    # Define year header detection function once, outside the loop
    def is_year_header(cell):
        if not cell:
            return False
        # Remove extra spaces for consistent matching
        cell = cell.strip()
        # Simple 4-digit year: 2018, 2024
        if cell.isdigit() and len(cell) == 4 and cell.startswith('20'):
            return True
        # Fiscal year with slash (with or without spaces): 2018/2019, 2018 / 2019
        if '/' in cell:
            parts = cell.replace(' ', '').split('/')
            if any(part.isdigit() and len(part) == 4 and part.startswith('20') for part in parts):
                return True
        # Fiscal year with hyphen (with or without spaces): 2018-2019, 2018 - 2019
        if '-' in cell:
            parts = cell.replace(' ', '').split('-')
            if any(part.isdigit() and len(part) == 4 and part.startswith('20') for part in parts):
                return True
        # Quarter format: Q1 2024, Q4 2023
        if cell.startswith('Q') and '20' in cell:
            return True
        return False
    
    for table in tables:
        rows = table.find_all('tr')
        pending_header_ths = []  # Store intermediate header row labels
        main_geography_header = []  # Store the main geography+violation header row
        
        for row_idx, row in enumerate(rows):
            # Extract <th> and <td> separately to maintain structure
            ths = [th.get_text().strip() for th in row.find_all('th')]
            tds = [td.get_text().strip() for td in row.find_all('td')]
            
            # Debug: Log first 20 rows to understand structure
            if row_idx < 20:
                logging.info(f"Row {row_idx}: ths={ths}, tds={tds[:5] if tds else []}")
            
            # Skip empty rows (no th and no td content)
            if not ths and not tds:
                continue
            
            # Handle rows that have only headers but no data values (intermediate header rows)
            # These appear when multiple geographies are selected
            # Instead of skipping, add them as rows with empty data, then the next row will fill the data
            if ths and not tds and not any(is_year_header(cell) for cell in ths):
                logging.debug(f"Found intermediate header row {row_idx}: {ths}")
                # Check if this is a main geography header (has geography name) or sub-header
                # Main headers have non-empty first element, sub-headers start with empty
                if ths and ths[0] and ths[0].strip():  # Non-empty first element = main header
                    main_geography_header = ths
                    logging.debug(f"Stored main geography header: {main_geography_header}")
                # Store as pending for next row
                pending_header_ths = ths
                continue
            
            # Check if ANY cell contains multiple year patterns (years mixed with other text)
            # This happens when StatCan puts everything in one cell separated by commas
            has_mixed_content = False
            for cell in ths + tds:
                if cell and ',' in cell and any(is_year_header(part.strip()) for part in cell.split(',')):
                    has_mixed_content = True
                    break
            
            if has_mixed_content:
                # Split the cell content by commas and separate years from non-years
                logging.info(f"Found mixed content row. Splitting cells...")
                year_headers = []
                
                for cell in ths + tds:
                    if cell:
                        parts = [p.strip() for p in cell.split(',')]
                        for part in parts:
                            if is_year_header(part):
                                year_headers.append(part)
                
                if year_headers:
                    logging.info(f"Extracted {len(year_headers)} years from mixed content: {year_headers}")
                    year_header_row_idx = len(data_rows)
                    # Year header row: empty columns A, B, C, then year headers starting at D
                    row_data = ['', '', ''] + year_headers + ['Percentage change from earliest to latest']
                    data_rows.append((row_data, []))  # Store with empty pending headers
                    continue
            
            # Check if this row contains year headers (years in th cells OR td cells)
            has_year_headers_in_th = any(is_year_header(cell) for cell in ths)
            has_year_headers_in_td = any(is_year_header(cell) for cell in tds)
            has_year_headers = has_year_headers_in_th or has_year_headers_in_td
            
            if has_year_headers:
                # Log what we found
                logging.info(f"Year header row detected. th cells: {ths[:10]}")
                logging.info(f"Year header row detected. td cells: {tds[:10]}")
                
                # This is the year header row
                year_header_row_idx = len(data_rows)  # Track which row is the header row
                # Separate non-year headers from year headers
                year_headers = []
                
                # Check both th and td cells for years
                all_cells = ths + tds
                for cell in all_cells:
                    if is_year_header(cell):
                        year_headers.append(cell)
                
                logging.info(f"Detected year header row with {len(year_headers)} years: {year_headers}")
                
                # Year header row: Need to add empty columns for filter labels first
                # Count non-year headers (filter labels) in this row
                non_year_headers = [cell for cell in all_cells if cell and not is_year_header(cell)]
                num_filter_columns = len(non_year_headers)
                
                logging.info(f"Found {num_filter_columns} filter columns before year data")
                
                # Create empty columns for filter labels, then add years
                row_data = [''] * num_filter_columns + year_headers + ['Percentage change from earliest to latest']
                data_rows.append((row_data, []))  # Store with empty pending headers
                pending_header_ths = []  # Clear any pending headers
            elif ths and tds:
                # Data row with labels and values
                # If we have pending headers from previous row, combine them
                pending_headers_used = []
                if pending_header_ths:
                    # Combine pending and current headers into a list (not a string)
                    # IMPORTANT: Keep empty labels to maintain structure for repeated geography detection
                    all_labels = pending_header_ths + ths
                    logging.debug(f"Combined pending headers {pending_header_ths} with current ths {ths} = {all_labels}")
                    pending_headers_used = list(pending_header_ths)  # Store copy for comparison
                    pending_header_ths = []  # Clear pending headers after use
                else:
                    # Keep th elements as separate items (don't combine into one string)
                    # IMPORTANT: Keep empty labels to maintain structure for repeated geography detection
                    all_labels = ths
                
                # Each label gets its own column, then data follows
                row_data = all_labels + tds
                data_rows.append((row_data, pending_headers_used))  # Store with pending headers
            elif ths:
                # Only headers (non-year), keep them as separate columns
                # IMPORTANT: Keep empty labels to maintain structure
                all_labels = ths
                row_data = all_labels
                data_rows.append((row_data, []))  # Store with empty pending headers
            else:
                # Only data cells - shouldn't happen with the new structure
                row_data = tds
                data_rows.append((row_data, []))  # Store with empty pending headers
    
    # Extract data list from tuples for processing
    data = [row_data for row_data, _ in data_rows]
    
    # Calculate percentage change for ALL data rows that have numeric values
    # Add percentage change column to all rows
    for idx in range(len(data)):
        row = data[idx]
        
        # Skip if row is too short
        if len(row) < 2:
            row.append('')
            continue
        
        # Find where numeric data starts (first column with a numeric value)
        data_start_idx = None
        for col_idx, val in enumerate(row):
            if val and val != '' and val != 'Percentage change from earliest to latest':
                # Treat "...", "..", "x", "X", "F", "E" and similar suppression symbols as data, not labels
                if str(val).strip() in ['...', '..', 'x', 'X', 'F', 'E', 'r', 'R']:
                    data_start_idx = col_idx
                    break  # This is data (suppressed value marker)
                try:
                    clean_val = str(val).replace(',', '').replace(' ', '')
                    float(clean_val)
                    data_start_idx = col_idx
                    break
                except (ValueError, AttributeError):
                    pass
        
        # If no numeric data found, skip percentage calculation
        if data_start_idx is None:
            row.append('')
            continue
        
        # Data values start at data_start_idx
        # Find first and last non-empty numeric values
        data_values = row[data_start_idx:]
        
        first_value = None
        last_value = None
        
        for val in data_values:
            if val and val != '' and val != 'Percentage change from earliest to latest':
                # Try to parse as number (remove commas if present)
                try:
                    clean_val = str(val).replace(',', '').replace(' ', '')
                    num_val = float(clean_val)
                    if first_value is None:
                        first_value = num_val
                    last_value = num_val
                except (ValueError, AttributeError):
                    pass
        
        # Calculate percentage change
        if first_value is not None and last_value is not None and first_value != 0:
            pct_change = ((last_value - first_value) / first_value) * 100
            data[idx].append(f"{pct_change:.2f}%")
        else:
            data[idx].append('')
    
    # Align all rows so data starts at the same column
    # AND align label types (e.g., all "Statistics" labels in the same column)
    # Find the maximum number of label columns (non-numeric columns at the start)
    max_label_columns = 0
    for row in data:
        label_count = 0
        for val in row:
            if val and val != '' and val != 'Percentage change from earliest to latest':
                # Treat "...", "..", "x", "F", "E" and similar suppression symbols as data, not labels
                if str(val).strip() in ['...', '..', 'x', 'X', 'F', 'E', 'r', 'R']:
                    break  # This is data (suppressed value marker)
                try:
                    clean_val = str(val).replace(',', '').replace(' ', '')
                    float(clean_val)
                    break  # Found first numeric value
                except (ValueError, AttributeError):
                    label_count += 1
            else:
                if val == '':
                    label_count += 1
        max_label_columns = max(max_label_columns, label_count)
    
    logging.info(f"Maximum label columns across all rows: {max_label_columns}")
    
    # For rows with repeated geography, align labels by keeping only the last (rightmost) label
    # and filling earlier positions with empty strings
    # Strategy: Track the last full geography row, detect short rows or matching rows
    previous_full_geography = None
    for idx in range(len(data_rows)):
        row_data, pending_headers_used = data_rows[idx]
        row = data[idx]
        
        # Count current label columns
        current_labels = []
        data_start_idx = None
        for col_idx, val in enumerate(row):
            if val and val != '' and val != 'Percentage change from earliest to latest':
                # Treat "...", "..", "x", "X", "F", "E" and similar suppression symbols as data, not labels
                if str(val).strip() in ['...', '..', 'x', 'X', 'F', 'E', 'r', 'R']:
                    data_start_idx = col_idx
                    break  # This is data (suppressed value marker)
                try:
                    clean_val = str(val).replace(',', '').replace(' ', '')
                    float(clean_val)
                    data_start_idx = col_idx
                    break  # Found first numeric value
                except (ValueError, AttributeError):
                    current_labels.append(val)
            else:
                # Empty label column - add it to maintain structure for repeated geography detection
                current_labels.append('')
        
        if data_start_idx is None:
            data_start_idx = len(row)
        
        if idx < 10:  # Log first 10 rows for debugging
            logging.info(f"Row {idx}: current_labels={current_labels}")
        
        # Strategy: Track the last "full" geography row (with 4 labels)
        # Rows with only 2 labels are likely sub-statistics under the same geography
        # If current row has same length as previous and first 2 labels match, it's repeated
        # If current row is shorter (2 labels vs 4), it's under the previous geography
        # NEW: Also check if first 2 labels are empty - this indicates repeated geography
        is_repeated_geography = False
        
        # Count non-empty labels to determine row type
        non_empty_labels = [label for label in current_labels if label and label.strip()]
        
        # Check if first 2 labels are empty (but we have labels after that)
        first_two_empty = (len(current_labels) >= 2 and 
                          not current_labels[0] and 
                          not current_labels[1] and
                          len(non_empty_labels) > 0)
        
        if first_two_empty:
            # First 2 columns are empty but has data after - this is repeated geography
            is_repeated_geography = True
            logging.info(f"Row {idx}: Empty geography columns detected (first 2 empty), treating as repeated geography")
        elif len(non_empty_labels) == 2 and previous_full_geography and len([l for l in previous_full_geography if l]) >= 2:
            # Short row (2 non-empty labels) - likely a sub-statistic under previous geography
            is_repeated_geography = True
            logging.info(f"Row {idx}: Short row detected (2 non-empty labels), treating as sub-statistic under previous geography")
        elif (previous_full_geography and 
              len(current_labels) >= 2 and 
              len(previous_full_geography) >= 2 and
              current_labels[0] == previous_full_geography[0] and
              current_labels[1] == previous_full_geography[1] and
              current_labels[0] and current_labels[1]):  # Both must be non-empty to match
            # Same length, same first 2 labels - definitely repeated
            is_repeated_geography = True
            logging.info(f"Row {idx}: Repeated geography detected (same geo+violation in full row)")
        
        if is_repeated_geography:
            logging.info(f"Row {idx}: Repeated geography - ensuring geography+violation columns are empty")
            # This is a repeated geography - ensure the geography+violation columns are empty
            # Check if first 2 columns are already empty
            if len(current_labels) >= 2 and not current_labels[0] and not current_labels[1]:
                # First 2 columns already empty - keep structure as is
                new_labels = current_labels
                logging.debug(f"Row {idx}: First 2 columns already empty, keeping structure")
            elif len(current_labels) == 2:
                # Short row with no empty prefix: add empty | empty | label1 | label2
                new_labels = ['', ''] + current_labels
                logging.debug(f"Row {idx}: Short row, adding empty prefix")
            else:
                # Full row with matching geo+violation: empty first 2, keep rest
                new_labels = ['', ''] + current_labels[2:]
                logging.debug(f"Row {idx}: Full row, replacing first 2 with empty")
            # Pad to max_label_columns
            if len(new_labels) < max_label_columns:
                new_labels += [''] * (max_label_columns - len(new_labels))
            data[idx] = new_labels + row[data_start_idx:]
        else:
            # Not a repeated geography - pad to max_label_columns normally
            if len(current_labels) < max_label_columns:
                padding_needed = max_label_columns - len(current_labels)
                data[idx] = current_labels + [''] * padding_needed + row[data_start_idx:]
                logging.debug(f"Padded row {idx} with {padding_needed} empty columns")
            # Update previous tracking - only for "full" rows with 4+ labels and non-empty geography
            # A "full" row has geography+violation in first 2 columns
            if len(current_labels) >= 4 and current_labels[0] and current_labels[1]:
                previous_full_geography = current_labels
                logging.debug(f"Row {idx}: Stored as previous_full_geography")

    
    logging.info(f"Extracted {len(data)} rows from table")
    return data
