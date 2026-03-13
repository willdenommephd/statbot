from setuptools import setup, find_packages

setup(
    name="statbot",
    version="0.1.0",
    description="StatBot: Automated statistical data extraction and Excel reporting tool",
    author="willdenommephd",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "openpyxl",
        "bs4",
        "webdriver_manager"
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'statbot=main:main',
        ],
    },
)
