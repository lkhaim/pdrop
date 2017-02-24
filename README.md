# pdrop
An application, which is using RESTful API implemented in Flask framework, Beautiful Soup, and SQLite, for organizing and reporting information from 800notes.com website. Includes notes_reporter_test.py - a first stab at creating Selenium-based unittest testing module.

It requires installation of Flask, Beautiful Soup v.4, and SQLite v.3. The application is written in Python 3.5.4.

The application is using data.py module for persisting data. data.py, in turn, is importing webpage scraper from scraper.py.

TO CONFIGURE THE APPLICATION:
1) Set the value of DB on the top of notes_reporter.py file to determine the name of the file used as SQLite database;
2) Turn the debugging mode on or off in the "app.run(debug=True)" line at the bottom of notes_reporter.py file;
3) Set the value of PHONE_SITE on the top of scraper.py file to determine the URL of pages to use as data source.

TO START THE APPLICATION:
<python notes_reporter.py>
It will be running on http://127.0.0.1:5000/ .

TO QUIT:
Press CTRL+C.

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
   to be returned when <n> is not provided;
- The web security used by 800notes.com may start blocking this application
  with the following error: HTTP Error 403: Forbidden
