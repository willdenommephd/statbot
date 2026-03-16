from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="statbot",
    version="0.1.0",
    description="StatBot: Automated statistical data extraction and Excel reporting tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="William James Denomme",
    author_email="willdenomme@outlook.com",
    url="https://github.com/willdenommephd/statbot",
    license="MIT",
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
            'statbot=statbot.main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
