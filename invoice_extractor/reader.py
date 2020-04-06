import pdfquery
from lxml import etree
from .formatter import formatter
from .writer import writer

class reader:
    """Reads table data from KPN mobile incoices"""

    def __init__(self, writer, table_names, first_column_names):
        self.writer = writer
        self.first_column_names = first_column_names
        self.requested_tables = table_names

    def load(self, file):
        self.file = file
        print('Loading %s' % str(self.file.split('\\')[-1:]))
        self.pdf = pdfquery.PDFQuery(self.file)
        page_count = len(self.pdf._pages)
        #self.pdf.load(list(range(2,page_count)))
        self.pdf.load()
        #self.write_tree_to_xml()

    def write_tree_to_xml(self):
        with open('xmltree.xml','wb') as f:
            f.write(etree.tostring(self.pdf.tree, pretty_print=True))
    
    @staticmethod
    def get_coordinates(query):
        assert 'x0' in query.attrib and 'y0' in query.attrib, 'querry doesn\'t contain coordinates'
        return { 'x' : float(query.attrib['x0']), 'y' : float(query.attrib['y0'])}

    @staticmethod
    def get_pageid(element) -> int:
        pageid = next(element.iterancestors('LTPage')).attrib['pageid']
        if pageid == '': raise ValueError('element doesn\'t have a ancestor with pageid')
        return int(pageid)

    def text_line_in_box_in_page(self, x0, y0, x1, y1, pageid, textbox = False):
        lines = self.pdf.pq('%s:in_bbox("%s, %s, %s, %s")' % ('LTTextBoxHorizontal' if textbox else 'LTTextLineHorizontal', x0, y0, x1, y1))
        output = [line for line in lines if reader.get_pageid(line) == pageid]
        return output

    def fix_boxvalue(self, line_results, coords, pageid_number):
        line_box_results = self.text_line_in_box_in_page(coords['x']+1, coords['y']-2, coords['x']+300, coords['y'] + 8, pageid_number, True)
        line_box_len = len(line_box_results)
        line_box_index = 0
        for i in range(0, len(line_results)):
            if line_box_index >= line_box_len: return line_results
            if line_results[i].text == '' and line_box_results[line_box_index].text != '': 
                line_results[i] = line_box_results[line_box_index]
                line_box_index += 1
        return line_results

    def read_table_line(self, first_element, header = False) -> str:
        formatter.remove_prefix(first_element)
        line_elements = []
        line_elements.append(first_element)
        coords = reader.get_coordinates(first_element)
        pageid_number = reader.get_pageid(first_element)
        line_results = self.text_line_in_box_in_page(coords['x']+1, coords['y']-2, coords['x']+300, coords['y'] + 8, pageid_number)
        if '' in [x.text for x in line_results]:
            line_results = self.fix_boxvalue(line_results , coords, pageid_number)
        line_elements += line_results
        line_elements = sorted(line_elements, key=lambda x: float(x.attrib['x0']))
        line = [element.text.strip() for element in line_elements]
        if header:
            self.line_buffer.append(formatter.concat_line(line))
        else:
            line = formatter.date_time_merger(line, self.invoice_date)
        return formatter.concat_line(line)

    def read_table_part(self, header):
        coords = reader.get_coordinates(header)
        last_label = None
        while True:
            label_number = self.text_line_in_box_in_page(coords['x'], coords['y']-10, coords['x']+80, coords['y'], reader.get_pageid(header))
            if len(label_number) == 0: break
            line = self.read_table_line(label_number[0])
            print(line[:-1])
            self.line_buffer.append(line)
            coords = reader.get_coordinates(label_number[0])
            last_label = label_number[0]
        return last_label

    def check_for_continuation(self, last_label, header_text):
        pageid_last_label = reader.get_pageid(last_label)
        coords_last_label = reader.get_coordinates(last_label)
        label_totaal = self.text_line_in_box_in_page(coords_last_label['x']  - 1, coords_last_label['y']-15, coords_last_label['x']+165, coords_last_label['y'], pageid_last_label, True)
        if len(label_totaal) != 0:
            if label_totaal[0].text[:6] == 'Totaal' : return None
        for label_vervolg in self.pdf.pq('LTTextLineHorizontal:contains("vervolg")'):
            coords = reader.get_coordinates(label_vervolg) 
            if not 700 < coords['y'] < 715: continue
            label_vervolg_page = reader.get_pageid(label_vervolg)
            if coords_last_label['x'] < 300:
                if label_vervolg_page != pageid_last_label: continue
                if coords['x'] < 300: continue
            else:
                if label_vervolg_page != pageid_last_label + 1: continue
                if coords['x'] > 300: continue
            label_header2 = self.text_line_in_box_in_page(coords['x'], coords['y']-12, coords['x']+150, coords['y'], label_vervolg_page)[0]
            if label_header2.text.strip() != header_text: continue
            return label_header2
        return None

    def read_table(self, label_header):
        label_start = label_header
        while True:
            last_label = self.read_table_part(label_start)
            if last_label is None: break
            label_start = self.check_for_continuation(last_label, label_header.text.strip())
            if label_start is None: break # No label matched
        return

    def read_table_data(self, table_name):
        for label_table_name in self.pdf.pq('LTTextLineHorizontal:contains("%s")' % table_name):
            self.line_buffer = []
            table_name_coords = reader.get_coordinates(label_table_name)
            label_header = self.text_line_in_box_in_page(table_name_coords['x'], table_name_coords['y']-10, table_name_coords['x']+75, table_name_coords['y'], reader.get_pageid(label_table_name))
            if len(label_header) == 0 : continue
            if label_header[0].text.strip() in self.first_column_names:
                self.read_table_line(label_header[0], True)
                self.read_table(label_header[0])
                self.writer.write_buffer_to_file(self.line_buffer, table_name)
                break
        return

    def get_invoice_date(self):
        date = self.text_line_in_box_in_page(440, 597, 519, 608, 1)[0]
        return date.text.strip()

    def read_pdf(self):
        print('Reading %s' % str(self.file.split('\\')[-1:]))
        self.invoice_date = self.get_invoice_date()
        for table_name in self.requested_tables:
            self.read_table_data(table_name)


    # in_bbox("x0,y0,x1,y1"): Matches only elements that fit entirely within the given bbox.
    # overlaps_bbox("x0,y0,x1,y1"): Matches any elements that overlap the given bbox.
