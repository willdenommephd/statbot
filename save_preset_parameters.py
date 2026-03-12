import logging

def save_preset_parameters(file_path, urls_file, url_filters_list=None, common_geography=None, common_data_type='tables'):
    """
    Save filter parameters to a preset file.
    
    Args:
        file_path: Path to save the preset file
        urls_file: Path to the URLs file
        url_filters_list: List of tuples (url_index, geography_method, geography_value, middle_filters, start_year, end_year, data_type)
        common_geography: Tuple of (method, value) if same geography for all URLs
        common_data_type: Common data type if same for all URLs
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("# StatCan Web Scraper Preset Parameters (Anchor-Based System)\n")
            file.write("# Lines starting with # are comments\n\n")
            file.write("# Global Settings\n")
            file.write("apply_filters=yes\n")
            file.write(f"urls_file={urls_file or ''}\n\n")
            
            # If common geography exists, save it as default
            if common_geography:
                file.write("# Fixed Filters (Common to All URLs)\n")
                file.write(f"geography_method={common_geography[0] or ''}\n")
                file.write(f"geography_value={common_geography[1] or ''}\n")
                file.write(f"data_type={common_data_type or 'tables'}\n\n")
            else:
                file.write("# No common filters - all filters defined per URL below\n")
                file.write("geography_method=\n")
                file.write("geography_value=\n")
                file.write(f"data_type={common_data_type or 'tables'}\n\n")
            
            # Save URL-specific filters
            if url_filters_list:
                file.write("# ============================================================================\n")
                file.write("# PER-URL FILTER CONFIGURATIONS\n")
                file.write("# ============================================================================\n\n")
                
                for idx, geo_method, geo_value, middle_filters, start_year, end_year, data_type in url_filters_list:
                    file.write(f"[url{idx}_filters]\n")
                    
                    # Only write geography if different from common
                    if not common_geography or (geo_method, geo_value) != common_geography:
                        file.write(f"geography_method={geo_method or ''}\n")
                        file.write(f"geography_value={geo_value or ''}\n")
                    
                    # Write middle filters
                    for i, mf in enumerate(middle_filters, 1):
                        file.write(f"filter_{i}_name={mf.get('name', '')}\n")
                        file.write(f"filter_{i}_method={mf.get('method', 'keyword')}\n")
                        file.write(f"filter_{i}_value={mf.get('value', '')}\n")
                    
                    # Write reference period
                    file.write(f"start_year={start_year or ''}\n")
                    file.write(f"end_year={end_year or ''}\n")
                    
                    # Write data type if different from common
                    if data_type != common_data_type:
                        file.write(f"data_type={data_type or 'tables'}\n")
                    
                    file.write("\n")
            
        logging.info(f"Saved preset parameters to {file_path}")
        print(f"Preset saved to: {file_path}")
    except Exception as e:
        logging.error(f"Error saving preset file: {e}")