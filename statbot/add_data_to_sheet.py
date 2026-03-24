import logging

def add_data_to_sheet(sheet, data, table_title, middle_filters_as_column=None):
    """
    Append a titled table of rows to a sheet.

    This function mutates `sheet` by appending:
    1) a single-cell title row containing `table_title`,
    2) a blank separator row,
    3) each row from `data`,
    4) a trailing blank separator row.

    Args:
        sheet: A worksheet-like object supporting `append(row: list)`.
            For example, a gspread Worksheet or any adapter with an `append` method.
        data: Iterable of rows to append. Each row should be a sequence (e.g., list/tuple)
            of cell values compatible with `sheet.append`.
        table_title: Title to place in the first appended row (single cell).
        middle_filters_as_column: Unused. Present for API compatibility / future extension.

    Returns:
        None

    Notes:
        - No header row is added despite the function name/comment; if you need headers,
          include them as the first row in `data` or extend the function.
        - If `data` is empty, only the title row and blank separator rows are appended.
    """    
    logging.info(f"Adding data to sheet: {table_title}")
    sheet.append([table_title])
    sheet.append([])  # Add empty row as separator
    for row in data:
        sheet.append(row)
    sheet.append([])
