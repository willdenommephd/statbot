import sys

def handle_interrupt(driver, sig=None, frame=None):
    print("\n\nCancelled by user. Closing browser...")
    try:
        if driver is not None:
            driver.quit()
    except Exception:
        pass  # Silently ignore any errors when closing the browser
    finally:
        sys.exit(0)