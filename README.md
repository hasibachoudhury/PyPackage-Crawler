# PyPackage-Crawler

usage: 
python request.py [-h] --action ACTION [--index INDEX] [--value VALUE]

optional arguments:
  -h, --help       show this help message and exit
  --action ACTION  allowed values - crawl / query
  --index INDEX    allowed values - name / version / abi / platform
  --value VALUE    value of selected index to be queried

****************************************************************************************************

Version: Python 3+
Packages required: grequests, argparse, sqlite3, re

First, we need to crawl the index of the website https://pypi.python.org/simple/ and then create the database with all the .whl files information. To do so:
> python request.py --action crawl

To query the created database, try the following: 
> python request.py --action query --index <column_name> --value <column_value> 
The allowed column_names are `name`, `version`, `abi` and `platform`. 

Since, we are storing everything in sqlite DB, we can directly connect to the DB and query using SQL commands for more filtered and custom queries.

All the information is stored in the `whl_files` table and the columns are `distribution`, `version`, `python_tag`, `abi_tag`, `platform`. 

You should have sqlite3 installed to run it from command line without using the script request.py - 
For macOS try - 
> brew install sqlite3 

To get to sqlite prompt run - 
> sqlite3 whl.db

Once you are inside sqlite prompt, you can run standard SQL commands. <br />
Example - <br />
sqlite> SELECT * FROM whl_files where platform = "any" and distribution = "airgram"; <br />
Output - <br />
airgram|0.1.0|py2.py3|none|any <br />
airgram|0.1.3|py2.py3|none|any <br />

****************************************************************************************************

There are approx 105k URLS to be crawled and I have used grequests to send parallel HTTP requets. And limited the concurrent connection to 200, beyond 700 grequest will break. The crawling takes some time (somewhere between 30 minutes to 1 hour) to fetch all the data.

I have also uploaded the DB file created by sqlite (whl.db)

One can directly use this file to go to sql prompt and use that instead of waiting.
