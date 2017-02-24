'''
An application, which is using RESTful API implemented in Flask framework,
for organizing and reporting information from 800notes.com website.

It requires installation of Flask, Beautiful Soup v.4, and SQLite v.3.
The application is written in Python 3.5.4.

The application is using data.py module for persisting data. data.py, in turn,
is importing webpage scraper from scraper.py.

To configure the application:
1) Set the value of DB on the top of notes_reporter.py file
   to determine the name of the file used as SQLite database;
2) Turn the debugging mode on or off in the "app.run(debug=True)"
   line at the bottom of notes_reporter.py file;
3) Set the value of PHONE_SITE on the top of scraper.py file
   to determine the URL of pages to use as data source.

To start the app: "python notes_reporter.py".
It will be running on http://127.0.0.1:5000/ .
To quit: CTRL+C.

Four types of reports are implemented using the following RESTful API:

- http://localhost:5000/api/v1.0/results to get up to 60 results;
- http://localhost:5000/api/v1.0/results/<n> to get <n> results.
  If <n> is larger than the number of available results--both freshly scraped
  from the webpage and stored in the DB--the message at WARNING
  will be logged to the console;
- http://localhost:5000/api/v1.0/resultsForArea/<area_code> to
  get all results for the area code <area_code> from the 60 latest entries;
- http://localhost:5000/api/v1.0/resultsForArea/<area_code>/<n>
  to get <n> results for the area code <area_code>. If <n> is larger
  than the number of available results, the message at WARNING
  will be logged to the console;

Current implementation's limitations:
- The database table containing the results is re-created every time
  the application is restarted;
- In data._get_db_entries() there is a hardcoded limit of 60 results
   to be returned when <n> is not provided.
'''
from flask import Flask
import logging
import data
import pdb

# print log messages to console if at INFO and higher
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# create a Flask application
app  = Flask(__name__)

# Database to be used by data.PhoneDataLayer() to persist the scraped data
DB = 'numbers.db'
data = data.PhoneDataLayer(DB)

def get_results(area_code=None, n=None):
    '''Get results according to <area_code> and <n> values given
       in reporting instructions and format them for displaying.
    '''
    # separate all entries for just one area code,if requested
    if area_code:
        es = data.get_entries(None)
        entries = [entry for entry in es if entry[0][:3] == area_code]
        # Pick only n first entries, if n is provided
        if n != None:
            entries_length = len(entries)
            # Log a warning, if there is less entries available than requested
            if n > entries_length:
                warn_msg = 'Asking to display %d results, ' +\
                           'but only %d results with %s area code were found.'
                logging.warning(warn_msg %(n, entries_length, area_code))
            entries = entries[:n]
    else:
        # obtain n or all entries (when n=None)
        # created by scraping 800notes.com and saved in numbers.db
        entries = data.get_entries(n)
        #pdb.set_trace()
    output = ('Showing a total of %d results.<br>' %len(entries))

    # combine all results in one string to be displayed
    for entry in entries:
        output += '[' + u', '.join(entry) + ']<br>'

    return output

@app.route('/api/v1.0/results', methods=['GET'])
def results():
    '''Display all available results.'''
    return get_results()

@app.route('/api/v1.0/results/<int:number>', methods=['GET'])
def results_with_limit(number):
    '''Display <n> results.'''
    return get_results(n=number)

@app.route('/api/v1.0/resultsForArea/<string:area_code>', methods=['GET'])
def results_by_area(area_code):
    '''Display all available results for area code <area_code>.'''
    return get_results(area_code=area_code)

@app.route('/api/v1.0/resultsForArea/<string:area_code>/<int:number>', methods=['GET'])
def results_by_area_with_limit(area_code, number):
    '''Display <number> results for area code <area_code>.'''
    return get_results(area_code=area_code, n=number)

if __name__ == '__main__':
    # run Flask application
    app.run(debug=False)
