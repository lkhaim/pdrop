import urllib.request
from bs4 import BeautifulSoup

PHONE_SITE = 'http://khaimovich.name/test_page_1.html'
#PHONE_SITE = 'http://800notes.com/'

class PhoneNumberEntry(object):
    '''Formats phone number entry for pretty display. Currently not used.'''
    def __init__(self, phone_number, report_count, comment):
        self.area_code    = phone_number[:3]
        self.phone_number = phone_number
        self.report_count = report_count
        self.comment      = comment.replace('"', '\\"')

    def __unicode__(self):
        skeleton = u'{{ "area_code": "{}", "phone_number": "{}", "report_count": "{}", "comment": "{}" }}'
        return skeleton.format(self.area_code, self.phone_number, self.report_count, self.comment)

class Parser(object):
    '''
    Uses Beautiful Soup library (https://www.crummy.com/software/BeautifulSoup/)
    for parsing html code of 800notes.com pages.
    '''
    def __init__(self, html):
        '''Cretaes BeautifulSoup object from html code.'''
        self.soup = BeautifulSoup(html, 'html.parser')

    def _entry_parse(self, html):
        '''
        Parses entries created by parse() method and returns a tuple containing
        phone number, number of reports about this phone number, and comments
        about it.
        '''
        num_of_reports = html.find(class_='oos_previewSide').getText()
        number         = html.find(class_='oos_previewHeader').getText()
        comment        = html.find('div', class_='oos_previewBody').getText()
        return (number, num_of_reports, comment)

    def parse(self):
        '''
        Parses 800notes.com page into html chunks containing one entry
        and then uses _entry_parse helper method to return a list of tuples,
        each of which contains one phone number, number of reports about this
        phone number, and commentscabout it.
        '''
        latest_entries = self.soup.find('ul', id='previews').\
                                   find_all('li', class_='oos_listItem')

        return [self._entry_parse(entry) for entry in latest_entries]

## Main (used for debugging this module)

if __name__ == "__main__":
    with urllib.request.urlopen(PHONE_SITE) as response:
        html = response.read()
    parser = Parser(html)
    print(parser.parse())
