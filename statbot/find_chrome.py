import os
import platform
import logging


def find_chrome():
    """
    Search for Chrome executable in common locations.
    Returns the path if found, None otherwise.
    """
    system = platform.system()
    
    if system == 'Windows':
        chrome_name = 'chrome.exe'
        # Check specific paths first (portable/local Chrome installations)
        specific_paths = [
            os.path.join(os.path.expanduser('~'), 'Documents', 'chromedriver', 'chrome-win64', chrome_name),
            os.path.join(os.path.expanduser('~'), 'Documents', 'chrome-win64', chrome_name),
            os.path.join(os.path.expanduser('~'), 'Downloads', 'chrome-win64', chrome_name),
            os.path.join(os.path.expanduser('~'), 'Downloads', 'chromedriver', 'chrome-win64', chrome_name),
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        ]
        
        # Check specific paths first
        for chrome_path in specific_paths:
            if os.path.isfile(chrome_path):
                logging.info(f"Found Chrome at: {chrome_path}")
                return chrome_path
        
        # If not found, do broader search
        search_paths = [
            os.path.join(os.path.expanduser('~'), 'Documents'),
            os.path.join(os.path.expanduser('~'), 'Downloads'),
            os.path.join(os.path.expanduser('~'), 'Desktop'),
            os.path.expanduser('~'),
            'C:\\Program Files\\Google\\Chrome\\Application',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application',
        ]
    elif system == 'Darwin':  # macOS
        # macOS has a standard location, but check Downloads/Documents first in case of custom install
        chrome_name = 'Google Chrome'
        specific_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            os.path.expanduser('~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
        ]
        
        for chrome_path in specific_paths:
            if os.path.isfile(chrome_path):
                logging.info(f"Found Chrome at: {chrome_path}")
                return chrome_path
        
        search_paths = [
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Documents'),
        ]
    else:  # Linux
        chrome_name = 'chrome'
        specific_paths = [
            '/usr/bin/google-chrome',
            '/usr/local/bin/google-chrome',
            '/usr/bin/chrome',
            '/usr/local/bin/chrome',
            '/opt/google/chrome/chrome',
        ]
        
        for chrome_path in specific_paths:
            if os.path.isfile(chrome_path):
                logging.info(f"Found Chrome at: {chrome_path}")
                return chrome_path
        
        search_paths = [
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~'),
        ]
    
    # Search for chrome in common locations (with depth limit)
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        
        # Check if chrome is directly in this directory
        direct_path = os.path.join(search_path, chrome_name)
        if os.path.isfile(direct_path):
            logging.info(f"Found Chrome at: {direct_path}")
            return direct_path
        
        # Search subdirectories (limit depth to 3 levels to avoid slow searches)
        try:
            for root, dirs, files in os.walk(search_path):
                # Calculate depth relative to search_path
                depth = root[len(search_path):].count(os.sep)
                if depth >= 3:
                    dirs[:] = []  # Don't go deeper
                    continue
                
                if chrome_name in files:
                    found_path = os.path.join(root, chrome_name)
                    logging.info(f"Found Chrome at: {found_path}")
                    return found_path
        except (PermissionError, OSError):
            # Skip directories we don't have permission to access
            continue
    
    return None

# Initialize driver as None - will be created in main() to avoid crashes during import
driver = None
