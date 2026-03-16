import os
import platform
import logging
import subprocess

def open_file(filepath):
    """
    Opens a file using the default application for the operating system.
    Works on Windows, macOS, and Linux.
    """
    try:
        system = platform.system()
        if system == 'Darwin':  # macOS
            subprocess.call(['open', filepath])
        elif system == 'Windows':
            os.startfile(filepath)
        else:  # Linux and other Unix-like systems
            subprocess.call(['xdg-open', filepath])
    except Exception as e:
        logging.warning(f"Could not open file automatically: {e}")
        print(f"File created successfully but could not open automatically: {filepath}")
