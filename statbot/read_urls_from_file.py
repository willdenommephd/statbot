import logging

# Function to read URLs, titles, and filter settings from a file
def read_urls_from_file(file_path):
    logging.info(f"Reading URLs from file: {file_path}")
    urls_titles_filters = []
    url_counter = 1
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                parts = line.split(';')
                if len(parts) == 3:
                    url, table_title, sheet_title = parts
                    urls_titles_filters.append((url.strip(), table_title.strip(), sheet_title.strip()))
                elif len(parts) == 2:
                    url, table_title = parts
                    sheet_title = table_title.strip()  # Use table title as sheet title
                    urls_titles_filters.append((url.strip(), table_title.strip(), sheet_title))
                    logging.debug(f"Parsed URL: '{url.strip()}', Title: '{table_title.strip()}'")
                elif len(parts) == 1:
                    url = parts[0]
                    table_title = f"Table_{url_counter}"
                    sheet_title = f"Sheet_{url_counter}"
                    urls_titles_filters.append((url.strip(), table_title, sheet_title))
                    url_counter += 1
                else:
                    logging.warning(f"Skipping invalid line: {line}")
    except Exception as e:
        logging.error(f"Error reading file: {e}")
    return urls_titles_filters