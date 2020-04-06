import os

from .reader import reader
from .formatter import formatter
from .writer import writer

table_names = ['Bellen binnen Nederland', 'Bellen in het buitenland', 'Bellen naar het buitenland', 'Ontvangen gesprekken in het buitenland', 'Servicenummers - dienst', 'Servicenummers - verkeer', 'Servicenrs btw-vrij - dienst', 'Servicenrs btw-vrij - verkeer', 'Sms-berichten', 'Sms-en in het buitenland']
first_column_names = ['Gekozen nummer', 'Land en nummer', 'Bestemming', 'Land en bestemming']

writer = writer()
reader = reader(writer, table_names, first_column_names)

def extract(path, save_dir = os.getcwd()):
    writer.set_save_dir(save_dir)
    if path[-4:] == '.pdf':
        reader.load(path)
        reader.read_pdf()
    elif os.path.isfile(path):
        print('please parse a pdf file or folder with pdf files.')
        return
    else:
        for filename in sorted(os.listdir(path)):
            if filename[-4:] == '.pdf':
                reader.load(os.path.join(path, filename))
                reader.read_pdf()