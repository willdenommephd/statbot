import logging

# Function to add data to a sheet with a title and header
def add_data_to_sheet(sheet, data, table_title, middle_filters_as_column=None):
    logging.info(f"Adding data to sheet: {table_title}")
    sheet.append([table_title])
    sheet.append([])  # Add empty row as separator
    for row in data:
        sheet.append(row)
    sheet.append([])  # Add empty row as separator