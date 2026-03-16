
# StatBot: Your Personal StatCan Data Extractor

StatBot.py is a Python-based program that automates the extraction and processing of StatCan data tables. It searches StatCan URLs (Uniform Resource Locator), applies one or more user-defined filters, and downloads the resulting tabular data directly into an Excel file.



## Authors

- [@willdenommephd](https://www.github.com/willdenommephd)



## Acknowledgements

AI‑assisted tools (Claude Sonnet 4.5 and GPT‑4.1) were used to support debugging, code validation, and improvements to coding hygiene. The author is responsible for all final code and design decisions.
## Support

For support, email willdenomme@outlook.com.


## Appendix

The following packages are required as dependencies:
- os
- platform
- argparse
- sys
- signal
- time
- beautifulsoup
- openpyxl
- selenium
- logging
- glob
- csv
- tempfile
- subprocess


## StatBot: User Manual

StatBot.py is a Python-based program that automates the extraction and processing of StatCan data tables. It searches StatCan URLs, applies one or more user-defined filters, and downloads the resulting tabular data directly into an Excel file.

The program organizes outputs automatically, creating a dedicated worksheet for each data source and including preloaded statistical analyses to support immediate use. StatBot also allows users to save and reuse filter configurations, apply pre-saved settings, and populate new columns in existing Excel files. It also calculates percentage change between the earliest and latest columns. 

Designed to reduce manual data extraction and analysis, StatBot helps automate recurring products and deliverables, freeing up staff time for higher-value tasks.

## Module 1: Installing StatBot
StatBot can be installed via pip install statbot onto your computer, or you can download its zip .tar.gz folder locally and using pip install . (path to StatBot).

## Module 2: Starting StatBot
StatBot runs directly in your IDE or Python interpreter’s terminal. After you install StatBot, you will be able to run it by typing "statbot" in your terminal, no matter the directory. One you start StatBot, you will be prompted with a welcome message. 

### Welcome message

Once you run the program, it will load the various libraries it requires, open a Google Chrome window, and will prompt you to respond with a welcome message. 
```
Hi! 👋 I'm StatBot, your personal StatCan data extraction assistant 🤖 

Just tell me what links you want to extract data from, and I'll help you get the data.
You can also save and load presets to streamline your workflow!

✨ Let's get started! ✨
```
## Module 3: Startup prompts and response options
Next, you will go through a series of prompts that will require your input. Here are the prompts and how to respond to them. 
1.	Enter the name of your output Excel file (without .xlsx extension): 
- Example: crime_data_2024
- What happens: StatBot will create “crime_data_2024.xlsx” with your extracted data. 
- Note: By default, the file will be saved to your working directory . If you wish to save the file in another folder, enter the path to the folder before the name of the output file. 
- Example: /C:/path/to/your/folder/crime_data_2024.xlsx
2.	Do you want to run a search and extract or just an extract? (search/extract):
- This prompt allows the user to define whether they wish to run an automated search and extract function (search mode) or an extract function with user-defined links (extract mode). 
- This prompt is answered by either typing search or extract. 

### Search mode
Search mode allows users to automatically extract any number of tables that are included in the search results in the following page: https://www150.statcan.gc.ca/n1/en/type/data?MM=1. StatBot will enter any keyword specified into the websites search box and extract the URLs of each table included in the search result and  the data from each individual table, with an Excel worksheet dedicated to each extracted link. 

Search mode follows when you type search in response to prompt 2 in Module 3. In search mode, you will receive the following prompt:
```
You have selected SEARCH AND EXTRACT. I will search for data tables matching your keyword(s) and extract the data to an Excel file.
  Tip: Use commas to run separate searches (e.g., crime, homicide)
  Tip: Use [brackets] to combine terms into one search (e.g. [crime, homicide])
```

After this prompt, you will be able to specify the search term(s) with the following prompt:
1.	Enter your search keyword(s):
- Specify the keywords you wish to use for a search. 
- The search protocol is very flexible, but the results of the search will depend on whether the keyword yields table results. 
- More specific keywords can be specified by placing it in quotation marks (e.g., “Incident-based crime statistics”). 
- Keywords separated by a comma will be treated as separate searches. This means that if you enter “crime, homicide”, a search will first be conducted for tables meeting the search criteria for “crime” – after which a data extraction will be conducted on those tables – followed by a second search for tables meeting the criteria for “homicide”.  
- To have a single search for multiple keywords, place the keywords in a square bracket (e.g., for a search of incident-based crime statistics in Atlantic regions, you can use [“Incident-based crime statistics”,Atlantic]). In addition, separate search can be conducted on combined keywords by separating two or more squared-brackets by a comma (e.g., [“Incident-based crime statistics”,Atlantic],[“Incident-based crime statistics”,Quebec]). 
- Once the keywords are specified, StatBot will extract the URLs that resulted from the search to a .txt file in your working directory. The file will be titled according to your keyword, followed by _tables.txt (e.g., Incident-based_crime_statistics_Atlantic_tables.txt). 
- StatBot will then prompt you with the filter configuration for the table(s)’s data extraction.

### Extract mode
Extract mode allows you to automatically extract data from URLs you already have. This can be particularly useful when you wish to update the results from an earlier data extraction done with Search mode, or if you had URLs for which you would like to extract the data. To update the results of an earlier data extraction, be sure to see Module 5: Update mode. 
Extract mode follows when you type extract in response to prompt 2 in Module.

In extract mode, you will be prompted with the following:
```
You have selected EXTRACT-ONLY. I will extract data to an Excel file based on your specified URLs.
```
After this prompt, you will be able to configure the URLs for processing by responding to the following prompts:
1.	Enter the path to your input file (or ‘manual’ for manual entry)
- Here you have the option to enter your URLs preloaded in an input file or in the terminal’s user interface directly. For each link, a separate worksheet will be created in the output Excel file. 
#### Links in a preloaded input file
If you wish to load an input file preloaded with your URL, follow these steps:
1. 	Open a text-editor program to create a .txt file. 
2.	In the file, dedicate one line per URL. 
3. 	Each line should be formatted as: URL (copy and pasted verbatim);worksheet title (the name that will be displayed at the top of the worksheet);worksheet name (the name of the worksheet’s tab in the Excel file). 
- Ensure that there are no spaces after the semi-colon “;”.
- Example: https://www150.statcan.gc.ca/t1/cv.action^pid=35100178801;Atlantic  regions;Atl_all
4.	Save the file as name.txt.
5.	In Module 3.2, Step 1 (above), enter the entire path verbatim to this input file. 
#### Manual link entry
If you type “manual”, you will be able to manually enter the URLs in the terminal’s user interface. You will have to answer three prompts in an open-ended format.
1.	Enter URL (or ‘done’ to finish): you can type or paste the URL.
2.	Enter table title for the URL: This is the worksheet name that will be displayed at the top of the worksheet. 
3.	Enter sheet title for the URL: This is the worksheet name that will be displayed on the tab in the Excel file. 
4.	Repeat these prompts and steps for as many URLs as you have, or type “done” when you have finished defining your URLs. 
5.	The link settings will be saved to a “manual_urls.txt” in the working directory. Therefore, if you were to run this program again, you can simply use this .txt file instead of completing the prompt process again.
####
After you define your URLs, you will be prompted:
1.	Enter batch size for processing URLs (default: 100). 
- Example: 50
- What happens: If you have a lot of URLs, StatBot processes the URLs in batches . Smaller batches, equating to a higher number of batches, requires less memory, but takes more time.
2.	Do you want to UPDATE an existing Excel file with a new year? (yes/no)
- This prompt is answered with either yes or no. 
- If you say no, StatBot will assume that the output file is new. If you answer yes, StatBot will assume that the output file is pre-existing and that it will overwrite the data. Based on how StatBot is configured, it could fail if it thinks it is working on a pre-existing file. 
- For more details, see Module 5: Update mode below. 

## Module 4: Filter settings
The following steps set up the filtration parameters for each URL. The filters are presets that are set up before StatBot searches through each URL to extract the data. This is done by navigating through the following prompts and responses. 
1.	Do you want to use a preset file for filter configuration? (yes/no)
- This prompt is answered with either a yes or a no. A preset file is a .txt file that will have the filter settings to be read by StatBot. The creation and formatting of the preset file is specified below. 
- If you say yes, you will receive the following prompt:
    - Enter the path to the preset file: here you can type or paste the path to your preset file, and StatBot will retrieve and read the file for you and apply the filters automatically. 
- If you say no, you will be required to enter the filters manually by continuing through the prompts in the following section. 

### Manual filter configuration
The filter configuration step is for when you wish to manually enter the filters for the data extraction (you selected no in Module 4 Step 1). It is where you can decide whether you want to apply the same filters to all URLs or individual filters to individual URLs. 

There are two types of filters that StatBot configures in StatCan’s data table website: fixed and middle filters. The fixed filters include Geography, which is always the first option; and reference period, for which you define the start and end of the reference period for which you wish to extract data from StatCan. Middle filters are user-defined. Different StatCan tables have various numbers of middle filters through which you must navigate. For middle filters, you would first define them with a name and proceed with the rest of the configuration that follows.  

You will define the method in which the filter is encoded to help StatBot find the filter. The method options include:
- Keyword: This will tell StatBot to search for a term that matches the characters entered. StatBot has some flexibility in terms of the keyword search, with the ability to overlook typos or to search for shorter versions of the terms (e.g., using “rate per 100” for “rate per 100,000 population). 
- Bracket_number: In StatCan tables, some filter options are coded with a number in square brackets (“[]”; e.g., in this table, one of the filtering options is “Violations”, which includes the option of “Total, all violations [0]”). You may find it simpler to use the bracket number instead of the actual term, which could also reduce the risk of errors or typos. 
- Level: StatCan’s filtering options are organized into parent-trees and expandable lists. For instance, in Geography, the first level would be displayed by default (i.e., Canada), but you can expand that level by clicking on a “+” symbol. In this expansion, you would see the “child” levels (also termed chid nodes) of the Canada level, which would be provinces/territories. You can then expand a child node at the second level (e.g., Ontario) to reveal the child nodes of the third level (individual Ontario communities). By selecting Level, you are selecting all child nodes under a level identified by a keyword. Therefore, if you type “Ontario”, all child nodes under Ontario will be selected and the data extracted. 
- Level_all: This option is almost identical to that of Level. This method will also include the data of the parent node identified per the keyword entry. Therefore, if you type “Ontario”, both Ontario and its child nodes will be selected. 

You can select multiple options in fixed and middle filters (except for the Reference Period). To do so, you simply separate each filter identifier by a comma (“,”). However, all entries must be according to the rule specified above (either a keyword, bracket_number, level, or level_all. Mixing two rules will not work). Note that if a keyword has a comma, StatBot will recognize this comma as a separator of two different entries, which can lead to failure. Fortunately, if a comma was present, you may just enter the characters before the comma, and StatBot’s search strategy will find the entirety of the keyword by itself. 

StatBot will converse with you to set up filters for all URLs either manually configured or loaded in a .txt file. By following these prompts, you will set up a seamless automated data extraction process. 
1.	Do you want to apply filters? (yes/no):
- You answer this prompt with either a yes or a no. If you answer no, then StatBot will extract the default data table loaded in the URL. If you answer yes, your answer is followed by another prompt. 
2.	Do you want to apply the same filters to all links? (yes/no)
- Answer the prompt with either a yes or a no. If you answer yes, then the filter configuration will only be prompted once, and the parameters will apply to all URLs you have defined. If you answer no, then StatBot will repeat the filter configuration prompts for each URL you define, labelled according to its worksheet name. 
For the following steps, let us assume that you selected no and that StatBot will apply different filters to two URLs. Note that if you answer yes, then the filters you define will be unanimously applied to all URLs. 

A series of prompts will follow under a timestamped log with the worksheet name for the defined URL. For the purposes of this example, the worksheet is named Test_1, and it will appear in your terminal as such: 
```
YYYY-MM-DD Time, - INFO – Settings for Test_1:
```
The first filter configuration will be geography. 
```
--- FIXED FILTER: Geography ---
```
3.	 Enter method for Geography (keyword/bracket_number/level/level_all): 
- Type the method through which you want StatBot to identify the filter option. The entry must be lower case and verbatim from the examples provided in the bracket (e.g., for “bracket_number”, you must type “bracket_number”. The alternatives, “bracketnumber” or “bracket number” will not be valid entries). 
4.	Enter value(s) for Geography (comma-separated for multiple): 
- Enter the values that StatBot will use to filter data by Geography values. Multiple entries are separated by a comma, and they must all correspond to the rule established in Module 4.1. Note that for keywords with a comma (e.g., “Rate per 100,000 population”), you should only enter the characters before the comma.

After you set up the rule for Geography, you will set up rules for the middle filters following this prompt: 
```
--- MIDDLE FILTERS (press Enter to skip any) ---
```
5.	How many middle filters would you like to configure? 
- 	You can specify any number, so long as it matches the number of middle filters on the StatCan URL. 

Afterwards, you will be able to configure each filter with the following three prompts, beginning with Filter 1: 

6.	Enter filter name (e.g., Violations, Offences, Statistics): 
- You can call this filter anything you would like, as StatBot will select the filter based on its position in the StatCan data table website instead of its specific term. 
7.	Enter method (keyword/bracket_number/level/level_all): 
- 	Type the method through which you want StatBot to identify the filter option. The entry must be lower case and verbatim from the examples provided in the bracket (e.g., for “bracket_number”, you must type “bracket_number”. The alternatives, “bracketnumber” or “bracket number” will not be valid entries). 
8.	Enter value(s) (comma-separated for multiple):
- Enter the values that StatBot will use to filter data by with the first middle filter. Multiple entries are separated by a comma, and they must all correspond to the rule established in Module 4.1. Step 7. Note that for keywords with a comma (e.g., “Rate per 100,000 population”), you should only enter the characters before the comma. 

You would repeat these three prompts for each middle filter you specified in Module 4.1. prompt 5. Each filter will be numbered in the terminal (Filter 1 through Filter x), and you can provide a name for each filter. 

After all middle filters are set up, you will specify the reference period following this prompt:
```
--- FIXED FILTER: Reference Period ---
Note: Enter the EXACT text as it appears in the dropdown
Examples: ‘2018/2019’, ‘2018-2019’, ‘2024’, ‘Q4 2024’, etc. 
```
9.	Enter start period (exact text from dropdown):
- StatCan tables usually provide data for multiple years. Here, you can set the earliest year, quarter, or other period indicator to start the reference period. Note that these reference period labels can vary between StatCan tables, and due to the complexity of the encoding, you must enter the exact coding for the year as it appears on the StatCan dropdown menu. 
10.	Enter end period (exact text from dropdown): 
- Here you set the latest year, quarter, or other period indicator to start the reference period. Note that these reference period labels can vary between StatCan tables, and due to the complexity of the encoding, you must enter the exact coding for the year as it appears on the StatCan dropdown menu. 
11.	Enter data type to extract (text/tables):
- StatBot is currently built to extract both text and data from tables. Extracting data from tables will force StatBot to extract data from the data tables., StatBot could potentially extract data from text (e.g., Juristats, The Daily articles), although this is experimental and untested. This feature may be improved or removed in the future. 
b.	For this prompt, you can answer either text or tables. For most cases, you can simply write “tables”. 
12.	   Do you want to save these settings as a preset for future use? (yes/no):
- This prompt calls for an answer of either yes or no. If you answer yes, the filter configurations you manually encoded above will be saved to a .txt file. If not, they will be discarded. 
- Saving these configurations can be a wise strategy and allow you to revisit the data extraction process and potentially repeat it. For instance, in Module 3 Step 3, you can add a new year to the beginning or end of an existing Excel sheet by using the same filter configurations saved in the preset file and specifying the new year to be added. This is further specified below (add URL to the section).  
- If you answer no, StatBot will begin the process of extracting data. If you answer yes, another prompt will follow.
13. Enter a name for the preset file (without extension): 
- You can name the file anything you would like and that name will be suffixed with a .txt. By default, the file will be saved in your working directory. If you wish to save it in another directory, specify the path in which you wish to save the file and add the file name without the .txt extension. 

These are the steps for which to manually configure StatBot to start the data extraction process. Afterwards, StatBot will begin to enter the URLs and extract the data. Details of this process are below. 

##### Layout configuration
By default, StatBot will apply the following layout to the data once extracted:
- Geography is organized by row.
- Middle filters are organized by row. 
- Reference period is organized by column. 

However, users can specify whether one or more middle filters can be organized into columns instead of rows. 
1. Enter the names of any middle filters you want as columns (comma-separated, leave blank for all as rows): 
- Specify the name of any middle filter, verbatim, that you wish to have its data organized by column instead of row. You can enter any number of middle filters. 

#### Preset file filter configuration
This filter configuration step is for when you wish to use a preset file to configure the filters automatically for StatBot. You specify that you wish to use a preset file and enter its path in Module 4 Step 1. Creating a preset file rather than using StatBot’s manual configuration option could streamline the process and reduce the risk of manual errors. 

The following instructions serve to create the preset file and load it into StatBot’s environment. 
1.	Open a text editor program and a new .txt file. It should be named something accessible, such as “preset.txt”. 
2.	The preset configuration is more flexible and open-ended than the manual configuration, but here are some important rules to implement to ensure StatBot accurately reads the preset file. 
3.	Filter configurations that would apply to all URLs are specified at the top under “[global]”. 
4.	Filter configurations that are URL specific are specified under a URL subsection, starting with “[url1_filters]”.
5.	Each URL is numerically numbered. 
6.	For each URL, you must specify as many filters as required for the URL. 
7.	Geography always needs to be specified and should be specified as the first filter for each URL (unless it is specified under [global]). 
8.	Reference period should be specified as separate lines, one for start_year and the other for end_year and should be as verbatim to the URL reference year specifications. The reference period can be specified at the end of each individual URL’s section, or in [global]. 
9.	The specification of method and values should be as strict as when using the manual entry configuration. 
####
Below is an example of what the preset file should look like for the following two URLs (saved in a separate .txt file). Each URL consists of two middle filters (Violations, Statistics). For middle filters, you specify the name of the filter, the method of data extraction, and the value in the same line, with a separate line for each middle filter. 
```
Links
https://www150.statcan.gc.ca/t1/cv.action^pid=35100178801;Atlantic  regions;Atl_all
https://www150.statcan.gc.ca/t1tbl1/en/cv.action?pid=3510018101;Manitoba;MB_all
Preset example
[global]
start_year = 2018
end_year = 2023

[url1_filters]
geography_method = level_all
geography_value = Newfoundland and Labrador,Prince Edward Island,Nova Scotia,New Brunswick
Violations = bracket_number:110,150
Statistics = keyword:Actual incidents

[url2_filters]
geography_method = level_all
geography_value = Manitoba
Violations = bracket_number:110,150
Statistics = keyword:Actual incidents
```
## Update mode
Update mode allows you to update a pre-existing file with the results of an earlier search with new data. This was created to be able to add new years to the Excel sheet. For instance, StatCan may release 2025 data for a table that only had data up to 2024 when first extracted. This update can be completed regardless of whether you configure the filters manually or use a preset file and it is intended to be a straightforward process to quickly add new data to your dataset. This may be particularly useful when wanting to update the results of a search conducted with Search mode (see above) using the links extracted from the search results. 

To update an existing Excel sheet (previously created by StatBot), follow these steps and prompts: 
1.	Start StatBot. 
2.	Enter the name for your output Excel file (without .xlsx extension): 
- Enter the path and name to the previously populated Excel file. 
3.	Do you want to run a search and extract or just an extract? (search/extract):
- Select extract. 
4.	Enter batch size for processing URLs (default 100): 
- Define your batch size. 
5.	Do you want to UPDATE an existing Excel file with a new year? (yes/no):
- This prompt is answered in a yes or no format. The following steps are for when you answer yes. 
6.	Do you want to use a preset file for filter configurations? (yes/no): 
- Answer yes so that you can update the file using all the same filter configurations you previously used. Note that this assumes you saved a preset file. 
7.	Enter the path to the preset file:
- Enter the same preset file previously used to conduct the initial data extraction. 

StatBot will process the URLs and presets and will prompt you with more questions to configure the update. 
```
--- UPDATE MODE: Add New Year ---
Note: Enter the EXACT text as it appears in the dropdown
Examples: ‘2025’, ‘2025/2026’, ‘2025-2026’, ‘Q4 2025’, etc. 
```
8.	What year would you like to add?: 
- Specify the year you wish to add to the Excel sheet. Note that it must be verbatim of the options in the reference period drop down menus. 
Next, you will have to specify where in the Excel file you would like to add the new data (at the beginning or the end). 
```
--- INSERT POSITION ---
```
9.	Insert new year at START or END of year columns? (start/end) [default: end]: 
- Specify where in the Excel file you would like to add the new data. If this field is empty, it will automatically be added to the end. 

## Automatic processing and output
Once you have addressed all user prompts, StatBot will start its automatic process. The automatic process is as follows – if it started with search mode:
1.	StatBot will open a Google Chrome window. 
2.	It will navigate to https://www150.statcan.gc.ca/n1/en/type/data?MM=1
3.	It will enter the search terms and navigate to the Tables tab of the results. 
4.	It will extract every table URL to a .txt file. Note that any URLs that do not belong to a table will be ignored by StatBot. 
5.	It will navigate to the first URL noted in the text file. 
- If you chose the Extract function, StatBot will begin the data extraction process by first navigating to the first URL in your links file or the first URL you manually enter. 
 
6.	It will detect whether it is already on a filter configuration page or the default table page in StatCan’s website. If it is on the default page, it will automatically navigate to the filter configuration page. 
7.	It will identify the Geography filter tab and expand the list of possible geographies to their further extent. 
8.	It will deselect any default selections to create a blank slate. 
9.	It will apply Geography filters. 
10.	It will navigate through the specified middle filters and repeat the same default deselection and filter selection as with Geography. 
11.	It will specify the reference period by altering the entries in the dropdown menu. 
12.	It will then customize the layout. By default, geographies and middle filter entries are organized by rows, with columns being dedicated to individual year. 
13.	It will attempt to download the CSV from StatCan’s website. If that fails, it will scrape the data table that is presented on StatCan’s website. 
14.	On the extracted Excel sheets, it will dedicate the furthest column to the right to a percentage change from the earliest to the latest year. This column will be blank if the value from the earliest or latest year is 0 or missing (missing can be either “…”, “na”, or “x”). 
15.	StatBot will repeat this process for as many links as it either extracts or you specify. 
16.	The Excel file will be saved per the configurations. 

## Errors and troubleshooting
### Problem: Chrome browser failed to start.

Solution: Make sure Google Chrome is installed on your computer and in a folder that can be accessed by your Python IDE or interpreter. 
### Problem: File does not exist
Solution: Make sure the file path is correct and without any typos and be sure to use the full path. If that fails, navigate to the folder as your working directory. 
### Problem: No data extracted
Solution: This error could have arisen due to numerous factors, and therefore, troubleshooting may require more steps. First, make sure that the StatCan page loads correctly and that StatBot can navigate through the page. If this fails, check your internet connection as well as whether there are any problems with the StatCan server. If these steps are completed, check the filters to make sure they can be accurately mapped onto the filtration and that data can match; check whether the URL used is accurate and free of typos; and try StatBot without filters to ensure it is not an issue with the program itself. 
## License

MIT License

Copyright (c) 2026 William James Denomme / @willdenommephd (https://www.github.com/willdenommephd)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

