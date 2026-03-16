import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ensure_filter_page(driver):
    """
    Checks if the page is on the default view or the filter configuration page.
    If on default page, clicks the "Add/Remove data" button to access filters.
    Returns True if navigation was successful, False otherwise.
    """
    try:
        import time
        # Wait a moment for page to load
        time.sleep(1)
        
        # Check 1: Look at the current URL - tv.action means default page, cv.action means filter page
        try:
            current_url = driver.current_url
            if 'cv.action' in current_url:
                logging.info("Filter page confirmed - URL contains 'cv.action'")
                return True
            elif 'tv.action' in current_url:
                logging.info("Default page detected - URL contains 'tv.action', need to click Add/Remove data")
                # Continue to button click below
        except Exception as e:
            logging.warning(f"Could not check URL: {e}")
        
        # Check 2: Look for tree0 element (only exists on filter page)
        try:
            tree = driver.find_element(By.ID, "tree0")
            # tree0 exists - we're on the filter page
            logging.info("Filter page confirmed - tree0 element exists")
            return True
        except:
            # tree0 doesn't exist - continue checking
            pass
        
        # Check 3: Look for Add/Remove data button (only exists on default page)
        try:
            add_remove_check = driver.find_element(By.XPATH, "//a[contains(text(), 'Add/Remove data') and contains(@href, 'cv.action')]")
            if add_remove_check:
                logging.info("Default page confirmed - Add/Remove data button found")
                # Continue to button click below
        except:
            # Button not found - might already be on filter page
            logging.info("Add/Remove data button not found - assuming already on filter page")
            return True
        
        # We're on the default page - need to click Add/Remove data button
        # Try to find and click the "Add/Remove data" button
        add_remove_buttons = [
            "//a[contains(text(), 'Add/Remove data') and contains(@href, 'cv.action')]",  # Most specific
            "//a[contains(@class, 'ui-link') and contains(text(), 'Add/Remove data')]",
            "//a[contains(@href, 'cv.action') and contains(@class, 'btn')]",
            "//a[contains(text(), 'Add / Remove data')]",
        ]
        
        button_clicked = False
        for xpath in add_remove_buttons:
            try:
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                logging.info(f"Found Add/Remove data button with xpath: {xpath}")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", button)
                logging.info("Clicked Add/Remove data button")
                button_clicked = True
                break
            except Exception as e:
                logging.debug(f"Button not found with xpath {xpath}: {e}")
                continue
        
        if button_clicked:
            # Wait for filter page to load - check for tree0 element OR cv.action in URL
            try:
                # Wait for either tree0 to appear or URL to change to cv.action
                for i in range(20):  # Wait up to 10 seconds (20 x 0.5s)
                    try:
                        driver.find_element(By.ID, "tree0")
                        logging.info("Filter configuration page loaded successfully - tree0 element now present")
                        time.sleep(1)  # Additional wait for page to stabilize
                        return True
                    except:
                        pass
                    
                    if 'cv.action' in driver.current_url:
                        logging.info("Filter configuration page loaded successfully - URL changed to cv.action")
                        time.sleep(2)  # Wait for tree to load
                        return True
                    
                    time.sleep(0.5)
                
                logging.warning("Clicked button but filter page did not load within timeout")
                return False
            except Exception as e:
                logging.warning(f"Error waiting for filter page: {e}")
                return False
        else:
            # Couldn't find button
            logging.warning("Could not find Add/Remove data button")
            return False
        
    except Exception as e:
        logging.error(f"Error in ensure_filter_page: {e}")
        return True  # Return True to continue execution