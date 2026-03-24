import logging

def get_reference_period():
    """
    Prompt the user to enter a start and end year for a reference period.

    This function reads two values from standard input (start year and end year),
    strips leading/trailing whitespace from each, logs the selected range at INFO
    level, and returns the values as a tuple.

    Returns:
        tuple[str, str]: A 2-tuple of (start_year, end_year) as entered by the user.

    Side Effects:
        - Prompts the user via `input()`.
        - Writes an INFO log message in the form:
          "Reference period: <start_year> to <end_year>".
    """
    start_year = input("Enter start year for the reference period: ").strip()
    end_year = input("Enter end year for the reference period: ").strip()
    logging.info(f"Reference period: {start_year} to {end_year}")
    return start_year, end_year
