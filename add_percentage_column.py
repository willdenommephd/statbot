import logging
import re


#This will be altered to also include rows. 
# Helper function to add percentage change column to data
def add_percentage_column(data_rows):
    """
    Add a percentage change column to CSV data.
    Finds the year header row and calculates percentage change from first to last year for each data row.
    
    Args:
        data_rows: List of lists representing CSV rows
        
    Returns:
        Modified data_rows with percentage column added
    """
    if not data_rows or len(data_rows) < 2:
        return data_rows
    
    # Debug: Log first few rows to see CSV structure
    logging.info(f"CSV has {len(data_rows)} total rows")
    for i in range(min(3, len(data_rows))):
        logging.info(f"CSV Row {i}: {data_rows[i][:10]}")  # First 10 cells
    
    # Find the year header row (contains year values like "2021", "2022", etc.)
    year_header_row_idx = None
    year_col_start = None
    year_col_end = None
    
    def is_year_value(val):
        """Check if a value looks like a year"""
        if not val:
            return False
        val_str = str(val).strip()
        # Match patterns like: 2021, 2021/2022, 2021-2022, Q1 2021, etc.
        return bool(re.match(r'^(\d{4})|(\d{4}[/-]\d{4})|([Q]\d\s*\d{4})$', val_str))
    
    for row_idx, row in enumerate(data_rows):
        # Check if this row contains year headers
        year_cols = [i for i, cell in enumerate(row) if is_year_value(cell)]
        if len(year_cols) >= 2:  # Need at least 2 years for percentage calc
            year_header_row_idx = row_idx
            year_col_start = year_cols[0]
            year_col_end = year_cols[-1]
            logging.info(f"Found year header row at index {row_idx}, years in columns {year_col_start} to {year_col_end}")
            break
    
    if year_header_row_idx is None:
        logging.info("Could not find year header row in CSV data, percentage column not added (will be calculated during update mode)")
        return data_rows
    
    # Add percentage change header to year header row
    data_rows[year_header_row_idx].append('Percentage change from earliest to latest')
    
    # Calculate percentage change for each data row after the header
    for row_idx in range(year_header_row_idx + 1, len(data_rows)):
        row = data_rows[row_idx]
        
        # Find first and last numeric values in year columns
        first_value = None
        last_value = None
        
        for col_idx in range(year_col_start, min(year_col_end + 1, len(row))):
            cell_value = row[col_idx] if col_idx < len(row) else ''
            if cell_value and str(cell_value).strip():
                try:
                    # Clean value: remove commas, spaces, percent signs
                    clean_val = str(cell_value).replace(',', '').replace(' ', '').replace('%', '')
                    num_val = float(clean_val)
                    if first_value is None:
                        first_value = num_val
                    last_value = num_val
                except (ValueError, AttributeError):
                    pass
        
        # Calculate percentage change
        if first_value is not None and last_value is not None and first_value != 0:
            pct_change = ((last_value - first_value) / first_value) * 100
            row.append(f"{pct_change:.2f}%")
        else:
            row.append('')
    
    logging.info("Added percentage change column to CSV data")
    return data_rows
