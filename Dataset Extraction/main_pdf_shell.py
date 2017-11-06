import PyPDF2
import re
from subprocess import getoutput


page = getoutput('pdftotext -layout -f 1 -l 1 /home/hong/Documents/Projects/'
                 'Dataset\ Citation/pdfs/544.pdf -')

page2 = page.replace('\n', ' ')

print(page2)

abstract = re.findall(r'Abstract(.*?)©', page2)

print(abstract)