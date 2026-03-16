from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import logging

#This can be altered, but based on testing, this is the most reliable way to select filters on StatCan's website.
def apply_filters_exact(driver,geography_method, geography_value, middle_filters, start_year, end_year, middle_filters_as_column=None):
    """
    Apply filters using anchor-based positional system:
    - Position 0 (Fixed): Geography
    #Geography was always the first one in testing. 
    - Position 1-N (Variable): Middle filters (determined by middle_filters list)
    - Position -2 (Fixed): Reference period
    - Position -1 (Fixed): Customize layout
    
    Args:
        geography_method: Method for Geography filter
        geography_value: Value(s) for Geography filter
        middle_filters: List of dicts with 'name', 'method', 'value' for middle filters
        start_year: Start year for reference period
        end_year: End year for reference period
        middle_filters_as_column: List of middle filter names to set as column (otherwise row)
    """
    logging.info(f"Applying anchor-based filters: geography_method={geography_method}, geography_value={geography_value}, middle_filters={middle_filters}, start_year={start_year}, end_year={end_year}")
    
    if middle_filters_as_column is None:
        middle_filters_as_column = []
        
    import time
    try:
        # Wait for page to fully load. If you are having problems, you can increase this time. Its effectiveness kind of depends on the server's traffic and your internet connection. 
        time.sleep(5)
        
        # Select the Geography options if provided (supports multiple selections - just separate them with a comma)
        if geography_method and geography_value:
            geography_values = [v.strip() for v in geography_value.split(',')]
            
            # StatBot clicks on Geography filter panel to ensure it's open and active
            try:
                geo_link = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Geography') or @id='panel16061-lnk']")) #based on the HTML code (the identifier for Geography)
                )
                driver.execute_script("arguments[0].click();", geo_link)
                time.sleep(2)
                logging.info("Opened Geography filter panel")
            except Exception as e:
                logging.info(f"Could not click Geography panel: {e}")

            # StatCan data is organized into trees, with parent nodes and child nodes. This part expands the entire tree out to select something. 
            # First, expand the tree to make all options visible. This will allow the visibility of, say, all provinces under Canada, and all municipalities under provinces. 
            try:
                for iteration in range(9):  # Expand up to 9 levels
                    collapsed_nodes = driver.find_elements(By.XPATH, "//div[@id='tree0']//li[contains(@class, 'jstree-closed')]") #Took forever to figure this out. 
                    if not collapsed_nodes:
                        break  # Stop if no more nodes to expand
                    logging.info(f"Expanding geography tree level {iteration + 1}, found {len(collapsed_nodes)} collapsed nodes")
                    for node in collapsed_nodes:
                        try:
                            expand_icon = node.find_element(By.CLASS_NAME, 'jstree-ocl')
                            driver.execute_script("arguments[0].click();", expand_icon)
                            time.sleep(0.1)
                        except:
                            pass
                    time.sleep(1)  # Wait for page to update after each level. I find this helped me really track what was happening during Selenium's processing. 
                logging.info("Expanded Geography tree nodes")
                time.sleep(2)  # Wait for final stabilization
            except Exception as e:
                logging.warning(f"Could not expand Geography tree: {e}")
            
            # Every StatCan page has numerous filters selected by default. This removes all defaults and creates a blank slate for StatBot. 
            try:
                # Helper to ensure a given li is unselected with retries. Sometimes the list would reselect, so I added this to ensure the blank slate is given. Future generations may not need this. 
                def ensure_geo_unselected(li_elem, max_tries=3):
                    tries = 0
                    while tries < max_tries:
                        try:
                            if li_elem.get_attribute('aria-selected') != 'true':
                                return True
                            checkbox = li_elem.find_element(By.CLASS_NAME, 'jstree-checkbox')
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                            time.sleep(0.1)
                            driver.execute_script("arguments[0].click();", checkbox)
                            time.sleep(0.2)
                        except Exception:
                            pass
                        tries += 1
                    return li_elem.get_attribute('aria-selected') != 'true'
                
                selected_geos = driver.find_elements(By.XPATH, "//div[@id='tree0']//li[@aria-selected='true']")
                if selected_geos:
                    logging.info(f"Deselecting {len(selected_geos)} default geography items")
                    deselected_count = 0
                    for geo_li in selected_geos:
                        try:
                            if ensure_geo_unselected(geo_li):
                                deselected_count += 1
                            time.sleep(0.05)
                        except Exception:
                            pass
                    logging.info(f"Deselected {deselected_count} geography items")
                    time.sleep(1)
                    
                    # Verify and retry if needed. Again, this is purely due to troubleshooting issues, and might be overkill. 
                    still_selected = driver.find_elements(By.XPATH, "//div[@id='tree0']//li[@aria-selected='true']")
                    if still_selected:
                        logging.warning(f"WARNING: {len(still_selected)} geography items still selected after first pass")
                        logging.info("Running second deselection pass...")
                        for li in still_selected:
                            try:
                                checkbox = li.find_element(By.CLASS_NAME, 'jstree-checkbox')
                                driver.execute_script("arguments[0].click();", checkbox)
                                time.sleep(0.1)
                            except Exception:
                                pass
                        time.sleep(1)
            except Exception as e:
                logging.warning(f"Could not deselect default geography: {e}")
            
            # Now select the geography options specified in the UI. 
            for geo_val in geography_values:
                try:
                    logging.info(f"Searching for geography: '{geo_val}'")
                    
                    # Build XPath query - search by anchor text
                    if geography_method == 'keyword':
                        # Search anchor text containing the keyword (case-insensitive)
                        xpath_query = f"//div[@id='tree0']//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{geo_val.lower()}')]"
                    elif geography_method == 'bracket_number':
                        # Search anchor text for a number surrounded by square brackets (e.g., [35]). This is a pretty handy feature StatCan includes with its nodes. 
                        xpath_query = f"//div[@id='tree0']//a[contains(text(), '[{geo_val}]')]"
                    elif geography_method == 'level' or geography_method == 'level_all':
                        # Find parent by keyword, then select all children. Level selects all children, level_all selects all children and the parent. 
                        xpath_query = f"//div[@id='tree0']//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{geo_val.lower()}')]"
                    
                    # Try to find all matching anchor elements
                    matching_anchors = driver.find_elements(By.XPATH, xpath_query)
                    if not matching_anchors:
                        logging.warning(f"No geography items found matching '{geo_val}'")
                        continue
                    
                    # Use the first match
                    geo_anchor = matching_anchors[0]
                    geo_li = geo_anchor.find_element(By.XPATH, './ancestor::li[1]')
                    label = geo_anchor.get_attribute('aria-label') or geo_anchor.text
                    logging.info(f"Found geography anchor: {label}")
                    
                    # Handle 'level' method: select all children under this node
                    if geography_method == 'level' or geography_method == 'level_all':
                        # First, expand the parent node if it's collapsed
                        try:
                            # Check if node has children and is collapsed
                            li_class = geo_li.get_attribute('class') or ''
                            if 'jstree-closed' in li_class:
                                # Node is collapsed, expand it
                                expand_icon = geo_li.find_element(By.CLASS_NAME, 'jstree-ocl')
                                driver.execute_script("arguments[0].click();", expand_icon)
                                logging.info(f"Expanded parent node: {label}")
                                time.sleep(1)  # Wait for expansion
                            else:
                                logging.info(f"Parent node already expanded or is a leaf: {label}")
                        except Exception as e:
                            logging.debug(f"Could not expand parent (may already be expanded): {e}")
                        
                        # Handle pagination/lazy loading: Click "show more" buttons to load all children. The "show more" button is an arrow. 
                        # First, try scrolling to trigger lazy loading
                        try:
                            child_ul = geo_li.find_element(By.XPATH, './ul')
                            # Get initial child count
                            initial_children = child_ul.find_elements(By.XPATH, './li')
                            initial_count = len(initial_children)
                            logging.info(f"Initial child count: {initial_count}")
                            
                            # Scroll through children to trigger lazy loading
                            if initial_count > 0:
                                last_child = initial_children[-1]
                                driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", last_child)
                                time.sleep(1)
                                
                                # Check if more children loaded
                                updated_children = child_ul.find_elements(By.XPATH, './li')
                                if len(updated_children) > initial_count:
                                    logging.info(f"Lazy loading triggered: {len(updated_children)} children now (was {initial_count})")
                        except Exception as e:
                            logging.debug(f"Could not trigger lazy loading via scroll: {e}")
                        
                        # Now try clicking pagination buttons
                        max_pagination_clicks = 20  # Prevent infinite loops. Otherwise, StatBot will search forever. 
                        pagination_clicks = 0
                        while pagination_clicks < max_pagination_clicks:
                            try:
                                # Look for pagination/show more buttons within this node
                                # Try multiple selectors for pagination buttons
                                pagination_button = None
                                
                                # Try 1: jstree-paginate class
                                try:
                                    pagination_button = geo_li.find_element(By.XPATH, './/a[contains(@class, "jstree-paginate")]')
                                    logging.info("Found pagination button with class 'jstree-paginate'")
                                except:
                                    pass
                                
                                # Try 2: Look for any link with down arrow or "more" text in the child ul
                                if not pagination_button:
                                    try:
                                        child_ul = geo_li.find_element(By.XPATH, './ul')
                                        pagination_button = child_ul.find_element(By.XPATH, './/a[contains(@class, "paginate") or contains(text(), "more") or contains(@title, "more")]')
                                        logging.info("Found pagination button in child ul")
                                    except:
                                        pass
                                
                                # Try 3: Look for span or div with pagination indicators
                                if not pagination_button:
                                    try:
                                        pagination_button = geo_li.find_element(By.XPATH, './/*[contains(@class, "paginate")]//a')
                                        logging.info("Found pagination button via paginate class in child element")
                                    except:
                                        pass
                                
                                if pagination_button:
                                    logging.info(f"Found pagination button, clicking to load more children...")
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination_button)
                                    time.sleep(0.2)
                                    driver.execute_script("arguments[0].click();", pagination_button)
                                    time.sleep(1.5)  # Wait for items to load
                                    pagination_clicks += 1
                                else:
                                    break
                            except Exception as e:
                                # No more pagination buttons found
                                if pagination_clicks > 0:
                                    logging.info(f"Loaded all paginated children ({pagination_clicks} page loads)")
                                else:
                                    logging.info("No pagination button found - may use lazy loading instead")
                                break
                                              
                        # If level_all, first select the parent node itself
                        if geography_method == 'level_all':
                            anchor_class = geo_anchor.get_attribute('class') or ''
                            if 'jstree-checked' not in anchor_class:
                                checkbox = geo_li.find_element(By.CLASS_NAME, 'jstree-checkbox')
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                                time.sleep(0.2)
                                driver.execute_script("arguments[0].click();", checkbox)
                                logging.info(f"Selected parent node: {label}")
                                time.sleep(0.3)
                        
                        # Find all descendant li elements (children at any depth)
                        # In jsTree, children are in: <li> -> <ul> -> <li> (children)
                        # StatCan uses role="checkbox" for child items instead of role="treeitem"
                        # Use descendant axis but exclude the parent itself
                        all_descendants = geo_li.find_elements(By.XPATH, './descendant::li[@role="treeitem" or @role="checkbox"]')
                        
                        # Filter out the parent itself from the list
                        child_items = [item for item in all_descendants if item != geo_li]
                        
                        logging.info(f"Found {len(child_items)} potential child items under '{label}'")
                        
                        # If no children found, try alternative approach - look in following siblings under parent's ul
                        if len(child_items) == 0:
                            logging.info("No descendants found, checking for children in nested ul...")
                            try:
                                # Look for ul that's a direct child of this li
                                nested_ul = geo_li.find_element(By.XPATH, './ul')
                                child_items = nested_ul.find_elements(By.XPATH, './li[@role="treeitem" or @role="checkbox"]')
                                logging.info(f"Found {len(child_items)} direct children in nested ul")
                            except:
                                logging.warning("No nested ul found either")
                        
                        # Click the first child item, which will be either:
                        # - "Select All" option if multiple children exist
                        # - The single child option if only one child exists
                        if child_items and len(child_items) > 0:
                            try:
                                first_child = child_items[0]
                                first_anchor = first_child.find_element(By.XPATH, './a')
                                first_label = first_anchor.get_attribute('aria-label') or first_anchor.text
                                
                                logging.info(f"Clicking first child option: {first_label}")
                                
                                # Simply click the checkbox without checking selection state
                                first_checkbox = first_child.find_element(By.CLASS_NAME, 'jstree-checkbox')
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_checkbox)
                                time.sleep(0.2)
                                driver.execute_script("arguments[0].click();", first_checkbox)
                                logging.info(f"Clicked '{first_label}' - all children should now be selected")
                                time.sleep(0.5)
                            except Exception as e:
                                logging.warning(f"Could not click first child: {e}")
                        else:
                            logging.warning(f"No children found to select under '{label}'")
                        
                        # Done with level/level_all - move to next geography
                        continue
                    else:
                        # Standard single selection
                        # Check if it's already selected (jsTree sets 'jstree-checked' on the anchor when using checkbox plugin)
                        anchor_class = geo_anchor.get_attribute('class') or ''
                        is_selected = 'jstree-checked' in anchor_class
                        
                        if is_selected:
                            logging.info(f"Geography '{label}' already selected, skipping")
                        else:
                            # Find and click the checkbox inside this item
                            checkbox = geo_li.find_element(By.CLASS_NAME, 'jstree-checkbox')
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                            time.sleep(0.2)
                            driver.execute_script("arguments[0].click();", checkbox)
                            
                            # Wait until anchor reflects checked state
                            try:
                                WebDriverWait(driver, 10).until(lambda d: 'jstree-checked' in (geo_anchor.get_attribute('class') or ''))
                            except Exception:
                                pass
                            logging.info(f"Selected geography: {label}")
                            time.sleep(0.5)
                except Exception as e:
                    logging.warning(f"Could not select geography '{geo_val}': {e}")
        
        # Process middle filters dynamically (filters between Geography and Reference Period). You can have as many as you'd like!
        for idx, filter_config in enumerate(middle_filters, 1):
            filter_name = filter_config['name']
            filter_method = filter_config['method']
            filter_value = filter_config['value']
            tree_id = f'tree{idx}'  # tree1, tree2, tree3...
            
            if not filter_method or not filter_value:
                logging.info(f"Skipping filter '{filter_name}' - no method or value provided")
                continue
            
            filter_values = [v.strip() for v in filter_value.split(',')]
            
            # Click on filter tab/link to open the tree
            try:
                filter_link = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{filter_name}')]"))
                )
                driver.execute_script("arguments[0].click();", filter_link)
                time.sleep(2)
                logging.info(f"Opened {filter_name} filter panel")
            except Exception as e:
                logging.warning(f"Could not open {filter_name} panel: {e}")
                continue
            
            # Expand tree nodes to reveal nested items (up to 9 levels deep)
            try:
                for iteration in range(9):
                    collapsed_nodes = driver.find_elements(By.XPATH, f"//div[@id='{tree_id}']//li[contains(@class, 'jstree-closed')]")
                    if not collapsed_nodes:
                        break
                    logging.info(f"Expanding {filter_name} tree level {iteration + 1}, found {len(collapsed_nodes)} collapsed nodes")
                    for node in collapsed_nodes:
                        try:
                            expand_icon = node.find_element(By.CLASS_NAME, 'jstree-ocl')
                            driver.execute_script("arguments[0].click();", expand_icon)
                            time.sleep(0.1)
                        except:
                            pass
                    time.sleep(1)
                logging.info(f"Expanded {filter_name} tree nodes")
                time.sleep(2)  # Extra wait for tree state to stabilize after expansion
            except Exception as e:
                logging.warning(f"Could not expand {filter_name} tree: {e}")
            
            # Deselect all items first (they may be selected by default)
            # This needs to be done AFTER expansion to catch all nested items
            try:
                # Helper to ensure a given li is unselected with retries
                def ensure_li_unselected(li_elem, max_tries=3):
                    tries = 0
                    while tries < max_tries:
                        try:
                            if li_elem.get_attribute('aria-selected') != 'true':
                                return True
                            checkbox = li_elem.find_element(By.CLASS_NAME, 'jstree-checkbox')
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                            time.sleep(0.1)
                            driver.execute_script("arguments[0].click();", checkbox)
                            time.sleep(0.2)
                        except Exception:
                            pass
                        tries += 1
                    return li_elem.get_attribute('aria-selected') != 'true'
                
                all_selected = driver.find_elements(By.XPATH, f"//div[@id='{tree_id}']//li[@aria-selected='true']")
                if all_selected:
                    logging.info(f"Deselecting {len(all_selected)} default selected items in {filter_name}")
                    deselected_count = 0
                    for li in all_selected:
                        try:
                            if ensure_li_unselected(li):
                                deselected_count += 1
                            time.sleep(0.05)
                        except:
                            pass
                    logging.info(f"Deselected {deselected_count} items in {filter_name}")
                    time.sleep(1)
                    
                    # Verify deselection worked - if items still selected, try again
                    still_selected = driver.find_elements(By.XPATH, f"//div[@id='{tree_id}']//li[@aria-selected='true']")
                    if still_selected:
                        logging.warning(f"WARNING: {len(still_selected)} items still selected after first pass in {filter_name}")
                        logging.info("Running second deselection pass...")
                        for li in still_selected:
                            try:
                                checkbox = li.find_element(By.CLASS_NAME, 'jstree-checkbox')
                                driver.execute_script("arguments[0].click();", checkbox)
                                time.sleep(0.1)
                            except Exception:
                                pass
                        time.sleep(1)
            except Exception as e:
                logging.warning(f"Could not deselect defaults in {filter_name}: {e}")
            
            # Now select the specific items requested
            for item_val in filter_values:
                try:
                    logging.info(f"Searching for {filter_name}: {item_val}")
                    
                    # Build XPath query based on method
                    if filter_method == 'keyword':
                        xpath_query = f"//div[@id='{tree_id}']//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{item_val.lower()}')]"
                    elif filter_method == 'bracket_number':
                        xpath_query = f"//div[@id='{tree_id}']//a[contains(text(), '[{item_val}]')]"
                    elif filter_method == 'level' or filter_method == 'level_all':
                        # Find parent by keyword, then select all children
                        xpath_query = f"//div[@id='{tree_id}']//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{item_val.lower()}')]"
                    else:
                        logging.warning(f"Unknown filter method: {filter_method}")
                        continue
                    
                    # Find matching anchor elements
                    matching_anchors = driver.find_elements(By.XPATH, xpath_query)
                    
                    if not matching_anchors:
                        logging.warning(f"No {filter_name} found matching '{item_val}'")
                        all_items = driver.find_elements(By.XPATH, f"//div[@id='{tree_id}']//li[@role='treeitem']")
                        logging.warning(f"Showing 10 sample {filter_name} labels:")
                        for i, item in enumerate(all_items[:10]):
                            try:
                                anchor = item.find_element(By.XPATH, ".//a")
                                logging.info(f"  Sample {i}: {anchor.text}")
                            except:
                                pass
                        continue
                    
                    # Use the first match
                    item_anchor = matching_anchors[0]
                    item_li = item_anchor.find_element(By.XPATH, './ancestor::li[1]')
                    label = item_anchor.get_attribute('aria-label') or item_anchor.text
                    logging.info(f"Found {filter_name} anchor: {label}")
                    
                    # Handle 'level' method: select all children under this node
                    if filter_method == 'level' or filter_method == 'level_all':
                        # First, expand the parent node if it's collapsed
                        try:
                            # Check if node has children and is collapsed
                            li_class = item_li.get_attribute('class') or ''
                            if 'jstree-closed' in li_class:
                                # Node is collapsed, expand it
                                expand_icon = item_li.find_element(By.CLASS_NAME, 'jstree-ocl')
                                driver.execute_script("arguments[0].click();", expand_icon)
                                logging.info(f"Expanded parent node: {label}")
                                time.sleep(1)  # Wait for expansion
                        except Exception as e:
                            logging.debug(f"Could not expand parent (may already be expanded): {e}")
                        
                        # Handle pagination/lazy loading: Click "show more" buttons to load all children
                        max_pagination_clicks = 20  # Prevent infinite loops
                        pagination_clicks = 0
                        while pagination_clicks < max_pagination_clicks:
                            try:
                                # Look for pagination/show more buttons within this node
                                # Try multiple selectors for pagination buttons
                                pagination_button = None
                                
                                # Try 1: jstree-paginate class
                                try:
                                    pagination_button = item_li.find_element(By.XPATH, './/a[contains(@class, "jstree-paginate")]')
                                    logging.info("Found pagination button with class 'jstree-paginate'")
                                except:
                                    pass
                                
                                # Try 2: Look for any link with down arrow or "more" text in the child ul
                                if not pagination_button:
                                    try:
                                        child_ul = item_li.find_element(By.XPATH, './ul')
                                        pagination_button = child_ul.find_element(By.XPATH, './/a[contains(@class, "paginate") or contains(text(), "more") or contains(@title, "more")]')
                                        logging.info("Found pagination button in child ul")
                                    except:
                                        pass
                                
                                # Try 3: Look for span or div with pagination indicators
                                if not pagination_button:
                                    try:
                                        pagination_button = item_li.find_element(By.XPATH, './/*[contains(@class, "paginate")]//a')
                                        logging.info("Found pagination button via paginate class in child element")
                                    except:
                                        pass
                                
                                if pagination_button:
                                    logging.info(f"Found pagination button, clicking to load more children...")
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination_button)
                                    time.sleep(0.2)
                                    driver.execute_script("arguments[0].click();", pagination_button)
                                    time.sleep(1.5)  # Wait for items to load
                                    pagination_clicks += 1
                                else:
                                    break
                            except Exception as e:
                                # No more pagination buttons found
                                if pagination_clicks > 0:
                                    logging.info(f"Loaded all paginated children ({pagination_clicks} page loads)")
                                else:
                                    logging.info("No pagination button found")
                                break
                        
                        # Find all descendant li elements (children at any depth)
                        # In jsTree, children are in: <li> -> <ul> -> <li> (children)
                        # StatCan uses role="checkbox" for child items instead of role="treeitem"
                        # Use descendant axis but exclude the parent itself
                        all_descendants = item_li.find_elements(By.XPATH, './descendant::li[@role="treeitem" or @role="checkbox"]')
                        
                        # Filter out the parent itself from the list
                        child_items = [item for item in all_descendants if item != item_li]
                        
                        logging.info(f"Found {len(child_items)} potential child items under '{label}'")
                        
                        # If no children found, try alternative approach - look in following siblings under parent's ul
                        if len(child_items) == 0:
                            logging.info("No descendants found, checking for children in nested ul...")
                            try:
                                # Look for ul that's a direct child of this li
                                nested_ul = item_li.find_element(By.XPATH, './ul')
                                child_items = nested_ul.find_elements(By.XPATH, './li[@role="treeitem" or @role="checkbox"]')
                                logging.info(f"Found {len(child_items)} direct children in nested ul")
                            except:
                                logging.warning("No nested ul found either")
                        
                        # Click the first child item, which will be either:
                        # - "Select All" option if multiple children exist
                        # - The single child option if only one child exists
                        if child_items and len(child_items) > 0:
                            try:
                                first_child = child_items[0]
                                first_anchor = first_child.find_element(By.XPATH, './a')
                                first_label = first_anchor.get_attribute('aria-label') or first_anchor.text
                                
                                logging.info(f"Clicking first child option: {first_label}")
                                
                                # Simply click the checkbox without checking selection state
                                first_checkbox = first_child.find_element(By.CLASS_NAME, 'jstree-checkbox')
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_checkbox)
                                time.sleep(0.2)
                                driver.execute_script("arguments[0].click();", first_checkbox)
                                logging.info(f"Clicked '{first_label}' - all children should now be selected")
                                time.sleep(0.5)
                            except Exception as e:
                                logging.warning(f"Could not click first child: {e}")
                        else:
                            logging.warning(f"No children found to select under '{label}'")
                        
                        # Done with level/level_all - move to next filter
                        continue
                    else:
                        # Standard single selection
                        # Check if already selected
                        anchor_class = item_anchor.get_attribute('class') or ''
                        is_selected = 'jstree-checked' in anchor_class
                        
                        if is_selected:
                            logging.info(f"{filter_name} '{label}' already selected, skipping")
                        else:
                            checkbox = item_li.find_element(By.CLASS_NAME, 'jstree-checkbox')
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                            time.sleep(0.2)
                            driver.execute_script("arguments[0].click();", checkbox)
                            try:
                                WebDriverWait(driver, 10).until(lambda d: 'jstree-checked' in (item_anchor.get_attribute('class') or ''))
                            except Exception:
                                pass
                            logging.info(f"Selected {filter_name}: {label}")
                            time.sleep(0.5)
                except Exception as e:
                    logging.warning(f"Could not select {filter_name} '{item_val}': {e}")
        
        # Handle Reference period using dropdown menus (not tree)
        # Default is 2020-2024, so only change if user specifies different years
        if start_year or end_year:
            try:
                # Click on Reference Period panel to open it (if needed)
                try:
                    ref_link = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Reference period') or @id='panel16064-lnk']"))
                    )
                    driver.execute_script("arguments[0].click();", ref_link)
                    time.sleep(2)
                    logging.info("Opened Reference Period panel")
                except Exception as e:
                    logging.info(f"Reference Period panel may already be open: {e}")
                
                # Select the start year using dropdown
                if start_year:
                    try:
                        start_dropdown = driver.find_element(By.ID, 'startYear')
                        select_start = Select(start_dropdown)
                        current_start = select_start.first_selected_option.text
                        if current_start != start_year:
                            try:
                                # Try standard selection first
                                select_start.select_by_visible_text(start_year)
                                logging.info(f"Changed start year from {current_start} to {start_year}")
                            except:
                                # Fall back to JavaScript if option is invisible
                                driver.execute_script(f"arguments[0].value = '{start_year}'; arguments[0].dispatchEvent(new Event('change'));", start_dropdown)
                                logging.info(f"Changed start year from {current_start} to {start_year} (via JavaScript)")
                        else:
                            logging.info(f"Start year already set to {start_year}")
                        time.sleep(1)
                    except Exception as e:
                        logging.warning(f"Could not select start year '{start_year}': {e}")
                
                # Select the end year using dropdown
                if end_year:
                    try:
                        end_dropdown = driver.find_element(By.ID, 'endYear')
                        select_end = Select(end_dropdown)
                        current_end = select_end.first_selected_option.text
                        if current_end != end_year:
                            try:
                                # Try standard selection first
                                select_end.select_by_visible_text(end_year)
                                logging.info(f"Changed end year from {current_end} to {end_year}")
                            except:
                                # Fall back to JavaScript if option is invisible
                                driver.execute_script(f"arguments[0].value = '{end_year}'; arguments[0].dispatchEvent(new Event('change'));", end_dropdown)
                                logging.info(f"Changed end year from {current_end} to {end_year} (via JavaScript)")
                        else:
                            logging.info(f"End year already set to {end_year}")
                        time.sleep(1)
                    except Exception as e:
                        logging.warning(f"Could not select end year '{end_year}': {e}")
            except Exception as e:
                logging.warning(f"Could not handle Reference period: {e}")

        # Handle Customize layout settings
        try:
            # Click on Customize layout panel to open it
            try:
                layout_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Customize layout') or contains(@id, 'layout')]"))
                )
                driver.execute_script("arguments[0].click();", layout_link)
                time.sleep(2)
                logging.info("Opened Customize layout panel")
            except Exception as e:
                logging.info(f"Customize layout panel may already be open: {e}")

            # Set Display Geography as: Row (layout3)
            try:
                geo_row_radio = driver.find_element(By.XPATH, "//input[@type='radio' and @name='dimLayoutList[0]' and @value='layout3']")
                if not geo_row_radio.is_selected():
                    driver.execute_script("arguments[0].click();", geo_row_radio)
                    logging.info("Set Display Geography as: Row")
                    time.sleep(0.3)
            except Exception as e:
                logging.warning(f"Could not set Geography layout: {e}")

            # Dynamically set all middle filters as Row (layout3) or Column (layout2)
            try:
                num_middle = len(middle_filters)
                for i, filter_config in enumerate(middle_filters, 1):
                    filter_name = filter_config.get('name', '')
                    layout_value = 'layout2' if filter_name in middle_filters_as_column else 'layout3'
                    try:
                        radio = driver.find_element(By.XPATH, f"//input[@type='radio' and @name='dimLayoutList[{i}]' and @value='{layout_value}']")
                        if not radio.is_selected():
                            driver.execute_script("arguments[0].click();", radio)
                            logging.info(f"Set middle filter '{filter_name}' as: {'Column' if layout_value == 'layout2' else 'Row'}")
                            time.sleep(0.3)
                    except Exception as e:
                        logging.warning(f"Could not set middle filter '{filter_name}' layout: {e}")
            except Exception as e:
                logging.warning(f"Could not set middle filters layout: {e}")

            # Set Reference period as: Column (layout2)
            try:
                ref_col_radio = driver.find_element(By.XPATH, f"//input[@type='radio' and @name='dimLayoutList[{1 + num_middle}]' and @value='layout2']")
                if not ref_col_radio.is_selected():
                    driver.execute_script("arguments[0].click();", ref_col_radio)
                    logging.info("Set Display Reference period as: Column")
                    time.sleep(0.3)
            except Exception as e:
                logging.warning(f"Could not set Reference period layout: {e}")

            logging.info("Customize layout settings applied")
        except Exception as e:
            logging.warning(f"Could not configure Customize layout: {e}")
        
        # Click Apply button to apply filters and reload table
        if geography_method or middle_filters or start_year or end_year:
            try:
                # Try to find and click the Apply button
                apply_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply') or contains(@class, 'apply') or @id='apply']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", apply_button)
                time.sleep(0.3)
                # Get initial table state before clicking Apply
                try:
                    initial_table = driver.find_element(By.ID, 'simpleTable')
                    initial_html = initial_table.get_attribute('outerHTML')
                    logging.info("Captured initial table state")
                except Exception:
                    initial_html = None
                
                driver.execute_script("arguments[0].click();", apply_button)
                logging.info("Clicked Apply button")
                
                # Wait for loading indicator to appear and disappear
                try:
                    # First wait for loading indicator to appear (if present)
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'loading') or contains(@class, 'spinner') or contains(@class, 'loader')]"))
                    )
                    logging.info("Loading indicator appeared")
                    time.sleep(0.5)
                    
                    # Then wait for it to disappear
                    WebDriverWait(driver, 30).until(
                        EC.invisibility_of_element_located((By.XPATH, "//*[contains(@class, 'loading') or contains(@class, 'spinner') or contains(@class, 'loader')]"))
                    )
                    logging.info("Loading indicator disappeared")
                except Exception as e:
                    logging.info("No loading indicator detected or already gone")
                
                # Wait for table to actually change (be replaced/updated)
                if initial_html:
                    try:
                        def table_changed(driver):
                            try:
                                current_table = driver.find_element(By.ID, 'simpleTable')
                                current_html = current_table.get_attribute('outerHTML')
                                return current_html != initial_html
                            except:
                                return False
                        
                        WebDriverWait(driver, 20).until(table_changed)
                        logging.info("Table content updated with filtered data")
                    except Exception as e:
                        logging.warning(f"Table may not have changed: {e}")
                
                # Additional wait for table to stabilize (row count stops changing)
                # Extended wait time for level_all which selects many geographies
                max_wait = 60 if geography_method in ['level', 'level_all'] else 10
                logging.info(f"Waiting up to {max_wait}s for table to fully render with all selected geographies...")
                
                # Wait for row count to stabilize (check every 2 seconds)
                stable_count = 0
                last_row_count = 0
                for i in range(max_wait // 2):
                    try:
                        table = driver.find_element(By.ID, 'simpleTable')
                        current_rows = len(table.find_elements(By.TAG_NAME, 'tr'))
                        
                        if current_rows == last_row_count and current_rows > 0:
                            stable_count += 1
                            if stable_count >= 2:  # Stable for 4 seconds (2 checks)
                                logging.info(f"Table stabilized at {current_rows} rows after {(i+1)*2} seconds")
                                break
                        else:
                            stable_count = 0
                            last_row_count = current_rows
                        
                        time.sleep(2)
                    except Exception as e:
                        logging.warning(f"Error checking table stability: {e}")
                        break
                
                # Check how many rows were rendered
                try:
                    table = driver.find_element(By.ID, 'simpleTable')
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    logging.info(f"Table rendered with {len(rows)} total rows")
                except Exception as e:
                    logging.warning(f"Could not count table rows: {e}")
            except Exception as e:
                logging.warning(f"Could not find or click Apply button: {e}. Waiting for auto-apply...")
                time.sleep(5)
    except Exception as e:
        logging.error(f"Error applying filters: {e}")
        try:
            driver.quit()
        except:
            pass
        raise
