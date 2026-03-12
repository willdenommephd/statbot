import logging

def get_data_type():
    data_type = input("Enter data type to extract (text/tables): ").strip().lower()
    while data_type not in ['text', 'tables']:
        logging.warning("Invalid data type. Please enter 'text' or 'tables'.")
        data_type = input("Enter data type to extract (text/tables): ").strip().lower()
    logging.info(f"Data type: {data_type}")
    return data_type