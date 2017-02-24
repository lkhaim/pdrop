import sqlite3 as lite
import urllib.request
import scraper
import logging
from functools import wraps # optional, but simplifies debugging of decorated fuctions

# print log messages to console if at INFO and higher
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

class PhoneDataLayer(object):
    '''
    Creates and populates the table in the database with phone data extracted
    by scraping 800notes.com pages (PHONE_SITE in scraper.py points to the URL)
    Each entry contains:
    * phone number
    * count of entries with this phone number
    * comment about this phone number
    
    Serves these data as a list of tuples.
    '''
    
    def __init__(self, DB):
        ''' Connects to the database and recreates the table Numbers in it. '''
        self.DB = DB
        # recreate table Numbers in the DB
        self._recreate_db_table()

    def get_entries(self, n=None):
        ''' Returns n or all (if n=None) tuples with entries consisting of
            phone number, number of entries with this number, and comment.
        '''
        # get the entries by scraping webpages (PHONE_SITE points to the URL)
        with urllib.request.urlopen(scraper.PHONE_SITE) as response:
            html = response.read()
        entries = scraper.Parser(html).parse()

        # store entries in the DB
        self._insert_db_entries(entries)

        # depending on the number of requested entries (n), return 60 of them
        # or first n of them. Go to the database for additional results,
        # if necessary
        entries_length = len(entries)

        if n is None:
            self._get_db_entries()# _get_db_entries() sets n to 60 by default
            return self.entries
        elif n <= entries_length:
            return entries[:n]
        elif n > entries_length:
            warn_msg = 'Asking to display %d results, ' +\
                       'but only %d results found on the page. ' +\
                       'Looking for more results in the database.'
            logging.warning(warn_msg %(n, entries_length))
            self._get_db_entries(n)

            return self.entries

    def _dbconnect(func):
        ''' A decorator for connecting to the database self.DB. '''
        @wraps(func)
        def dbconnected(self, *args, **kwargs):
            con = None
            try:
                con = lite.connect(self.DB)
                with con:
                    self.cur = con.cursor()
                    func(self, *args, **kwargs)
            except lite.Error as e:
                raise e
            finally:
                if con:
                    con.close()
        return dbconnected

    @_dbconnect
    def _recreate_db_table(self):
        ''' Recreate table Numbers in the database self.DB. '''
        # ATTENTION! Do we need to preserve table Numbers between the runs of this application?
        #+ If yes, how do we ensure that the table's rows are not duplicated?
        self.cur.execute("DROP TABLE IF EXISTS Numbers")
        self.cur.execute("CREATE TABLE Numbers(number TEXT primary key not null, count INT, comment TEXT, date TEXT)")

    @_dbconnect
    def _insert_db_entries(self, entries):
        ''' Takes a list of tuples and inserts them as records into the database '''
        sql_string = 'INSERT OR REPLACE INTO' + \
                     ' Numbers(number, count, comment, date)' + \
                     ' VALUES (?, ?, ?, CURRENT_TIMESTAMP);'
        for entry in entries:
            self.cur.execute(sql_string, [entry[0], entry[1], entry[2]])

    @_dbconnect
    def _get_db_entries(self, n=60):
        ''' Gets "n" records from the database and returns relevant data as a list of tuples '''

        # open database connection and select n records from the database DB
        self.cur.execute('SELECT * FROM Numbers ORDER BY date LIMIT {}'.format(n))
        rows = self.cur.fetchall()

        # Create "entries" list of tuples. Each tuple contains:
        #+  * phone number, which is retrieved from row[0]
        #+  * count of entries with this phone number, which is retrieved from row[1]
        #+  * comment about this phone number, which is retrieved from row[2]
        entries = []
        for row in rows:
            entries.append((row[0], str(row[1]), row[2])) # sqlite3 bug requires casting row[1] to string

        self.entries = entries