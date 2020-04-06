# Invoice-Extractor
This is a purpose-built project to extract the tabluar data from Dutch KPN Mobile invoices.
It is heavily relying on the [PDFQuery](https://github.com/jcushman/pdfquery) package.

## Compatibility
This package has been tested on invoices dating from 2016 until 2019, but will probably work with older and more recent invoices.

## Installation
At this moment this package does not exist in PyPI, and has to be put into the python package directory manually. For windows this is usually `C:Program Files (x86)\Python<version>\Lib\`

## Usage

It is possible to extract the data from just one pdf file, or a directory containing compatable pdf files.

### Usage example
```python
import invoice_extractor

pdf_file = <somefilepath>
pfd_directory = <somefilepath>
output_directory = <somepath>


invoice_extractor.extract(pfd_file, output_directory)
invoice_extractor.extract(pfd_directory, output_directory)
```


(This repo is automatically synced from [Gitea](https://git.sciuro.org/burathar/invoice-extractor/))