import PyPDF2
import re
from subprocess import call


pdfFileObj = open('/home/hong/Documents/Projects/'
                  'Dataset Citation/pdfs/547.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
# print(pdfReader.numPages)

page = pdfReader.getPage(0).extractText()

page2 = page.replace('\n', ' ')

print(page2)

abstract = re.findall(r'Abstract(.*?)INTRODUCTION', page2)

print(abstract)