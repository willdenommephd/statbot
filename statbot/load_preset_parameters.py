import logging

def load_preset_parameters(file_path):
    """
    Load comprehensive preset parameters from a file.
    
    Expected format (NEW ANCHOR-BASED SYSTEM):
    # Global settings
    apply_filters=yes
    urls_file=demo_links.txt
    # OR list URLs directly:
    # url1=https://example.com;Table1;Sheet1
    # url2=https://example2.com;Table2;Sheet2
    
    # Fixed Filters (Always Present)
    geography_method=keyword
    geography_value=Quebec
    
    # Middle Filters (Variable - add as many as needed)
    filter_1_name=Violations
    filter_1_method=keyword
    filter_1_value=Total
    
    filter_2_name=Statistics
    filter_2_method=keyword
    filter_2_value=Number
    
    # Fixed end filters (use exact text from dropdown)
    # Examples: '2018/2019', '2024', 'Q4 2024', etc.
    start_year=2019
    end_year=2024
    data_type=tables
    
    # Per-URL overrides
    [url1_filters]
    filter_1_name=Offences
    filter_1_value=Violent crimes
    """
    try:
        params = {}
        url_specific_filters = {}
        current_section = None
        urls_list = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                
                # Check for section headers like [url1_filters]
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    if current_section != 'global':
                        url_specific_filters[current_section] = {}
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip() if value.strip() else None
                    
                    # Handle URL entries (only keys like "url1", "url2", etc. - not url1_filters or geography_method)
                    # This should only match keys that are exactly "url" + number with nothing after
                    if key.startswith('url') and key != 'urls_file' and '_' not in key:
                        if value:
                            urls_list.append(value)
                    elif current_section and current_section != 'global':
                        # Add to section-specific filters
                        url_specific_filters[current_section][key] = value
                    else:
                        # Add to global params
                        params[key] = value
        
        # Extract global parameters
        apply_filters = params.get('apply_filters', 'yes').lower() == 'yes'
        urls_file = params.get('urls_file', None)
        
        # Extract fixed filters
        geography_method = params.get('geography_method', None)
        geography_value = params.get('geography_value', None)
        data_type = params.get('data_type', 'tables')
        start_year = params.get('start_year', None)
        end_year = params.get('end_year', None)
        
        # Extract middle filters - support two formats:
        # 1. filter_1_name, filter_1_method, filter_1_value (explicit format)
        # 2. FilterName = method:value (compact format)
        middle_filters = []
        
        # First try explicit format (filter_1_name, etc.)
        filter_index = 1
        while True:
            filter_name = params.get(f'filter_{filter_index}_name', None)
            if not filter_name:
                break
            filter_method = params.get(f'filter_{filter_index}_method', 'keyword')
            filter_value = params.get(f'filter_{filter_index}_value', None)
            
            middle_filters.append({
                'name': filter_name,
                'method': filter_method,
                'value': filter_value
            })
            filter_index += 1
        
        # If no explicit filters found, look for compact format (FilterName = method:value)
        if not middle_filters:
            reserved_keys = {'apply_filters', 'urls_file', 'geography_method', 'geography_value', 
                           'data_type', 'start_year', 'end_year'}
            for key, value in params.items():
                if key not in reserved_keys and not key.startswith('filter_') and not key.startswith('url') and ':' in str(value):
                    # Parse compact format: FilterName = method:value
                    try:
                        method, filter_value = value.split(':', 1)
                        middle_filters.append({
                            'name': key,
                            'method': method.strip(),
                            'value': filter_value.strip()
                        })
                    except ValueError:
                        logging.warning(f"Could not parse filter format for {key} = {value}")
        
        logging.info(f"Loaded preset parameters from {file_path}")
        
        return {
            'apply_filters': apply_filters,
            'urls_file': urls_file,
            'urls_list': urls_list,
            'default_filters': {
                'geography_method': geography_method,
                'geography_value': geography_value,
                'middle_filters': middle_filters,
                'data_type': data_type,
                'start_year': start_year,
                'end_year': end_year
            },
            'url_specific_filters': url_specific_filters
        }
    except Exception as e:
        logging.error(f"Error loading preset file: {e}")
        return None