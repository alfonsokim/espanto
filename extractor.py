
import os
from cStringIO import StringIO
import re

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter

# =============================================================================
HEADER_REGEXPS = [
    # TODO: Probar con un estado de cuenta de diciembre
    r'''Del\ (?P<start_day>\d+)[\ ]  # Dia de inicio del periodo 
        de\ (?P<start_month>\w+)[\ ] # Mes de inicio del periodo
        al\ (?P<end_day>\d+)[\ ]     # Dia de fin del periodo
        de\ (?P<end_month>\w+)[\ ]   # Mes de fin del periodo
        de\ (?P<stmt_year>\d+)       # Anio del periodo
    ''', # Del 16 de Julio al 16 de Agosto de 2016
]

RE_FLAGS = re.X | re.I
HEADERS = map(lambda r: re.compile(r, RE_FLAGS), HEADER_REGEXPS)


# =============================================================================
def get_statement_header(text):
    """ Parsea los datos generales del estado de cuenta
    """
    for regexp in HEADERS:
        print regexp.pattern
        match = regexp.match('CLASICADel 16 de Julio al 16 de Agosto de 2016,')
        if match:
            print match.groupdict()


# =============================================================================
def read_pfd(memory_file):
    """ Convierte un PDF a texto plano
    :param memory_file: El archivo PDF en memoria a convertir a texto
    :return: El texto parseable dentro del documento
    """
    builder = StringIO()
    document = PDFDocument(PDFParser(memory_file), os.environ.get('PDF_PASS'))
    if not document.is_extractable:
        raise utils.ExtractionError('PDF file is sealed')
    resource_manager = PDFResourceManager()
    device = TextConverter(resource_manager, builder)
    interpreter = PDFPageInterpreter(resource_manager, device)
    map(lambda page: interpreter.process_page(page), PDFPage.get_pages(memory_file, password=os.environ.get('PDF_PASS')))
    text = builder.getvalue()
    device.close()
    builder.close()
    return text


# =============================================================================
def extract():
    """
    """
    for dirpath, dir_names, file_names in os.walk('statements'):
        for pdf_file_name in filter(lambda f: f.split('.')[-1].lower() == 'pdf', file_names):
            pdf_path = os.path.join(dirpath, pdf_file_name)
            print pdf_path
            pdf_file = open(pdf_path, 'rb')
            text = read_pfd(pdf_file)
            pdf_file.close()
            headers = get_statement_header(text)


# =============================================================================
if __name__ == '__main__':
    extract()


