import locale
import threading

from re import search
from datetime import datetime
from contextlib import contextmanager

class formatter:

    # source setlocale = https://stackoverflow.com/questions/18593661/how-do-i-strftime-a-date-object-in-a-different-locale
    LOCALE_LOCK = threading.Lock()

    @staticmethod
    @contextmanager
    def setlocale(name):
        with formatter.LOCALE_LOCK:
            saved = locale.setlocale(locale.LC_ALL)
            try:
                yield locale.setlocale(locale.LC_ALL, name)
            finally:
                locale.setlocale(locale.LC_ALL, saved)

    @staticmethod
    def date_time_merger(line, invoice_date):
        with formatter.setlocale('nl_NL.UTF-8'):
            invoice_datetime = datetime.strptime(invoice_date, '%d %B %Y')
        invoice_year = invoice_datetime.year - 1 if invoice_datetime.month == 1 else invoice_datetime.year
        date = [x for x in line if search("\d{2} \w{3}",x)]
        time = [x for x in line if search("\d{2}:\d{2}",x)]
        if len(date) < 1 or len(time) < 1: 
            print("Warning: Could not find date and time in {0}".format(line))
            return line
        datetime_string = '{0} {1}'.format(date[0], time[0])
        with formatter.setlocale('nl_NL.UTF-8'):
            linedate = datetime.strptime(datetime_string, '%d %b %H:%M').replace(year = invoice_year)
        datestring = linedate.strftime('%Y-%m-%d %H:%M:%S')
        return [line[0], datestring] +line[3:]

    @staticmethod
    def remove_prefix(element):
        element_text = element.text
        if len(element_text) < 5: return
        if element_text[3] == ' ':
            element.text = element_text[4:]
        return

    @staticmethod
    def concat_line(line):
        return ''.join([element + ';' for element in line])[:-1] + '\n'