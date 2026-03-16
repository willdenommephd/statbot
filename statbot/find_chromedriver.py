import os
import platform
import logging

#For most cases, this will have very little impact. But if you have some security or permission issues, this will allow you to select a different driver that your Python terminal, or StatBot, can access. 

def find_chromedriver():
    """
    Search for ChromeDriver executable in common locations.
    Returns the path if found, None otherwise.
    """
    system = platform.system()
    
    if system == 'Windows':
        chromedriver_name = 'chromedriver.exe'
        search_paths = [
            os.path.join(os.path.expanduser('~'), 'Documents'),
            os.path.join(os.path.expanduser('~'), 'Downloads'),
            os.path.join(os.path.expanduser('~'), 'Desktop'),
            os.path.expanduser('~'),
            'C:\\Program Files',
            'C:\\Program Files (x86)',
            'C:\\',
        ]
    elif system == 'Darwin':  # macOS
        chromedriver_name = 'chromedriver'
        search_paths = [
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~'),
            '/usr/local/bin',
            '/opt/homebrew/bin',
        ]
    else:  # Linux
        chromedriver_name = 'chromedriver'
        search_paths = [
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~'),
            '/usr/local/bin',
            '/usr/bin',
        ]
    
    # Search for chromedriver in common locations (with depth limit)
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        
        # Check if chromedriver is directly in this directory
        direct_path = os.path.join(search_path, chromedriver_name)
        if os.path.isfile(direct_path):
            logging.info(f"Found ChromeDriver at: {direct_path}")
            return direct_path
        
        # Search subdirectories (limit depth to 3 levels to avoid slow searches)
        try:
            for root, dirs, files in os.walk(search_path):
                # Calculate depth relative to search_path
                depth = root[len(search_path):].count(os.sep)
                if depth >= 3:
                    dirs[:] = []  # Don't go deeper
                    continue
                
                if chromedriver_name in files:
                    found_path = os.path.join(root, chromedriver_name)
                    logging.info(f"Found ChromeDriver at: {found_path}")
                    return found_path
        except (PermissionError, OSError):
            # Skip directories we don't have permission to access
            continue
    
    return None
