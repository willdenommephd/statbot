import sys
import logging

def get_filter_settings(update_mode=False):
    try:
        print("\n--- FIXED FILTER: Geography ---")
        geography_method = input("Enter method for Geography (keyword/bracket_number/level/level_all): ").strip().lower()
        geography_value = input("Enter value(s) for Geography (comma-separated for multiple): ").strip()
        
        print("\n--- MIDDLE FILTERS (press Enter to skip any) ---")
        num_filters = input("How many middle filters would you like to configure? ").strip()
        try:
            num_filters = int(num_filters)
        except ValueError:
            num_filters = 0
        
        middle_filters = []
        for i in range(num_filters):
            print(f"\nFilter {i+1}:")
            filter_name = input(f"  Enter filter name (e.g., Violations, Offences, Statistics): ").strip()
            if not filter_name:
                continue
            filter_method = input(f"  Enter method (keyword/bracket_number/level/level_all): ").strip().lower()
            filter_value = input(f"  Enter value(s) (comma-separated for multiple): ").strip()
            
            middle_filters.append({
                'name': filter_name,
                'method': filter_method,
                'value': filter_value
            })
        
        if update_mode:
            print("\n--- ADD NEW YEAR ---")
            print("Note: Enter the EXACT text as it appears in the dropdown")
            print("Examples: '2024', '2024/2025', '2024-2025', 'Q4 2024', etc.")
            new_year = input("What year would you like to add? ").strip()
            start_year = new_year
            end_year = new_year
            
            print("\n--- INSERT POSITION ---")
            insert_pos = input("Insert new year at START or END of year columns? (start/end) [default: end]: ").strip().lower()
            if insert_pos not in ['start', 'end']:
                insert_pos = 'end'
            return geography_method, geography_value, middle_filters, start_year, end_year, insert_pos
        else:
            print("\n--- FIXED FILTER: Reference Period ---")
            print("Note: Enter the EXACT text as it appears in the dropdown")
            print("Examples: '2018/2019', '2018-2019', '2024', 'Q4 2024', etc.")
            start_year = input("Enter start period (exact text from dropdown): ").strip()
            end_year = input("Enter end period (exact text from dropdown): ").strip()
            insert_pos = None  # Not used in non-update mode
        
        logging.info(f"Filter settings: geography_method={geography_method}, geography_value={geography_value}, middle_filters={middle_filters}, start_year={start_year}, end_year={end_year}")
        if update_mode:
            return geography_method, geography_value, middle_filters, start_year, end_year, insert_pos
        else:
            return geography_method, geography_value, middle_filters, start_year, end_year
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)