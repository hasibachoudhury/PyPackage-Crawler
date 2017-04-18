import grequests
import re
import sqlite3
import argparse

URL = "https://pypi.python.org/simple/"
HREF_REGEX = r"<a href=\'(.*?)\'>"
# {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl .
WHL_REGEX = r">([\w\d.]+)-([\w\d.]+)-?[\w\d.]*?-([\w\d.]+)-([\w\d.]+)-([\w\d.]+)\.whl<"
CHUNK_SIZE = 200

# Create the table and indexes on all the columns
def create_table_and_indices(cursor):
  cursor.execute('DROP TABLE whl_files')
  cursor.execute('CREATE TABLE whl_files (distribution text, version text, python_tag text, abi_tag text, platform text)')
  cursor.execute('CREATE INDEX distribution_index ON whl_files (distribution)')
  cursor.execute('CREATE INDEX version_index ON whl_files (version)')
  cursor.execute('CREATE INDEX python_tag_index ON whl_files (python_tag)')
  cursor.execute('CREATE INDEX abi_tax_index ON whl_files (abi_tag)')
  cursor.execute('CREATE INDEX platform_index ON whl_files (platform)')

# Inserts records into the database given cursor
def insert_records(cursor, whl_file_records):
  cursor.executemany('INSERT INTO whl_files VALUES (?,?,?,?,?)', whl_file_records)

# Given a list of URLs, this will return a list of HTTP response body
def get_urls(urls):
  rs = (grequests.get(u) for u in urls)
  responses = grequests.map(rs)
  response_bodies = []
  for response in responses:
    if response is not None:
      response_bodies.append(response.text)
  return response_bodies

# Given the base URL, this function will return all the records.
def get_all_whl_file_records(url):
  response = get_urls([url])
  hrefs = re.findall(HREF_REGEX, response[0])

  child_urls = []
  for href in hrefs:
    child_urls.append(URL + href)

  print (len(child_urls), " packages found.")

  # Now let's fetch all the Child URL's
  responses = []
  for i in range(0, len(child_urls) // CHUNK_SIZE + 1):
    print ("Fetching data for ", i * CHUNK_SIZE, " to ", (i + 1) * CHUNK_SIZE)
    responses.extend(get_urls(child_urls[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]))

  whl_files = []
  for response in responses:
    whl_files.extend(re.findall(WHL_REGEX, response))

  return whl_files

def print_records(records):
  print ("NAME | PYTHON_VERSIONS | ABIs | PLATFORMS")
  for record in records:
    print(record[0], " | ", record[1], " | ", record[3], " | ", record[4])

def crawl_and_create_database(cursor):
  print("Starting crawling... This is going to be a while..")
  whl_files = get_all_whl_file_records(URL)
  print("Yay!! crawling done.", len(whl_files), " whl files found.")
  print("Creating database now, this should be a breeze..")
  create_table_and_indices(cursor)
  insert_records(cursor, whl_files)
  print("All records inserted!")

def query(cursor, column_name, column_value):
  if column_name in ['distribution', 'version', 'python_tag', 'abi_tag', 'platform']:
    print_records(cursor.execute('SELECT * FROM whl_files WHERE %s=:value' %column_name, {'value': column_value}))
  else:
    print("No records found !!")

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--action', type=str, required=True, help='allowed values - crawl / query')
  parser.add_argument('--index', type=str, help='allowed values - name / version / abi / platform')
  parser.add_argument('--value', type=str, help='value of selected index to be queried')
  args = parser.parse_args()

  conn = sqlite3.connect('whl.db')
  cursor = conn.cursor()

  indexToColumnName = {'name': 'distribution', 'version': 'version', 'abi': 'abi_tag', 'platform': 'platform'}

  if args.action == 'crawl':
    crawl_and_create_database(cursor)
    conn.commit()
    conn.close()
  elif args.action == 'query':
    if args.index is None or args.value is None:
      print ("Please supply the index and the value param(s)")
    elif args.index not in indexToColumnName.keys():
      print ("Allowed index values are - name / version / abi / platform")
    else:
      query(cursor, indexToColumnName[args.index], args.value)
      conn.close()
  else:
    print ("incorrect action, allowed values are - crawl / query")
