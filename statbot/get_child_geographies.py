import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Helper function to get all child geography names under a parent geography
def get_child_geographies(driver, parent_geography_name):
    """
    Navigate to the geography filter and extract all child geography names under the parent.
    Returns a list of child geography names (without bracket codes).
    """
    try:
        driver.get(driver.current_url)  # Refresh to reset state
        time.sleep(3)
        
        # Open geography filter
        try:
            geo_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "tree0-btn"))
            )
            geo_button.click()
            time.sleep(1)
        except:
            logging.warning("Could not click Geography panel to get children")
        
        # Expand tree nodes
        for level in range(1, 6):
            try:
                collapsed = driver.find_elements(By.XPATH, "//div[@id='tree0']//li[@aria-expanded='false' and @role='treeitem']")
                if not collapsed:
                    break
                logging.info(f"Expanding geography tree level {level}, found {len(collapsed)} collapsed nodes")
                for node in collapsed[:10]:  # Limit to avoid infinite loops
                    try:
                        ocl = node.find_element(By.CLASS_NAME, "jstree-ocl")
                        driver.execute_script("arguments[0].click();", ocl)
                        time.sleep(0.1)
                    except:
                        pass
                time.sleep(1)
            except:
                break
        
        # Find the parent geography node
        xpath_query = f"//div[@id='tree0']//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{parent_geography_name.lower()}')]"
        matching_anchors = driver.find_elements(By.XPATH, xpath_query)
        
        if not matching_anchors:
            logging.warning(f"Could not find parent geography: {parent_geography_name}")
            return []
        
        geo_anchor = matching_anchors[0]
        geo_li = geo_anchor.find_element(By.XPATH, './ancestor::li[1]')
        
        # Expand parent if needed
        try:
            li_class = geo_li.get_attribute('class') or ''
            if 'jstree-closed' in li_class:
                ocl = geo_li.find_element(By.CLASS_NAME, 'jstree-ocl')
                driver.execute_script("arguments[0].click();", ocl)
                time.sleep(1)
        except:
            pass
        
        # Get all child items
        all_descendants = geo_li.find_elements(By.XPATH, './descendant::li[@role="treeitem" or @role="checkbox"]')
        child_items = [item for item in all_descendants if item != geo_li]
        
        # Extract child geography names
        child_names = []
        for child in child_items:
            try:
                child_anchor = child.find_element(By.XPATH, './a')
                child_text = child_anchor.text.strip()
                
                # Skip "Select all" options
                if 'select all' in child_text.lower():
                    continue
                
                # Extract just the geography name (before the bracket code)
                # e.g., "Bathurst, New Brunswick, municipal [13001]" -> "Bathurst, New Brunswick, municipal"
                if '[' in child_text:
                    child_name = child_text.split('[')[0].strip()
                else:
                    child_name = child_text
                
                if child_name:
                    child_names.append(child_name)
            except:
                pass
        
        logging.info(f"Found {len(child_names)} child geographies under '{parent_geography_name}'")
        return child_names
        
    except Exception as e:
        logging.error(f"Error getting child geographies: {e}")
        return []