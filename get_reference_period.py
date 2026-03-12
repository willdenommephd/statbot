import logging

def get_reference_period():
    start_year = input("Enter start year for the reference period: ").strip()
    end_year = input("Enter end year for the reference period: ").strip()
    logging.info(f"Reference period: {start_year} to {end_year}")
    return start_year, end_year