import urllib.request
import xml.etree.ElementTree as ET
import json


class ICPSRRecords:
    title = ''
    identifier = ''
    date = ''

    def __init__(self, title, identifier, date):
        self.title = title
        self.identifier = identifier
        self.date = date

    def __str__(self):
        return self.title + ", " + self.identifier + ", " + self.date


if __name__ == "__main__":
    requestUrl = "http://www.icpsr.umich.edu/" \
                 "icpsrweb/ICPSR/oai/studies?" \
                 "verb=ListRecords&" \
                 "metadataPrefix=oai_dc"

    # define namespaces used in the xml
    ns = {'oai': 'http://www.openarchives.org/OAI/2.0/',
          'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
          'schemaLocation': 'http://www.openarchives.org/OAI/2.0/ '
                            'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd',
          'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
          'dc': 'http://purl.org/dc/elements/1.1/'}

    resumptionToken = ''
    recordList = list()
    # simulate a do-while loop
    while True:
        response = urllib.request.urlopen(requestUrl + "&resumptionToken="
                                          + resumptionToken)

        root = ET.fromstring(response.read())
        titles = root.findall('.//dc:title', ns)
        identifiers = root.findall('.//dc:identifier', ns)
        dates = root.findall('.//dc:date', ns)
        num = len(root.findall('.//oai:ListRecords/*', ns)) - 1
        # ICPSR returns 50 records at a time
        for i in range(num):
            record = ICPSRRecords(titles[i].text, identifiers[i*2+1].text,
                                  dates[i].text)
            recordList.append(record)
        print(len(recordList))
        token = root.find(".//oai:resumptionToken", ns)
        if token is None:
            break
        else:
            resumptionToken = token.text
            print(resumptionToken)

    with open('ICPSR_metadata.json', 'w') as outfile:
        json.dump([obj.__dict__ for obj in recordList], fp=outfile, indent=4)
