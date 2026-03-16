import logging

#Debating deleting this. 

def get_data_type():
       """
    Prompt the user to choose a data type to extract and validate the input.

    This function repeatedly prompts the user (via `input()`) to enter a data
    type selection, normalizes the response by stripping whitespace and
    lowercasing it, and validates that it is one of the allowed options:
    `"text"` or `"tables"`. If the user enters an invalid option, a warning is
    logged and the user is prompted again. Once a valid option is provided, the
    selected data type is logged at INFO level and returned.

    Returns
    -------
    str
        The validated data type selection: either `"text"` or `"tables"`.

    Notes
    -----
    - This function is interactive and blocks waiting for user input.
    - Logging is performed using the module-level `logging` configuration.

    Examples
    --------
    >>> # User enters: text
    >>> get_data_type()
    'text'
    """
    data_type = input("Enter data type to extract (text/tables): ").strip().lower()
    while data_type not in ['text', 'tables']:
        logging.warning("Invalid data type. Please enter 'text' or 'tables'.")
        data_type = input("Enter data type to extract (text/tables): ").strip().lower()
    logging.info(f"Data type: {data_type}")
    return data_type
