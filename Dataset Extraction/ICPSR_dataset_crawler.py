from lxml import html


class IcpsrDatasetCrawler(object):

    @staticmethod
    def get_dataset(pages):

        dataset = list()
        for i in range(pages):
            tree = html.parse("http://www.icpsr.umich.edu/icpsrweb/ICPSR/"
                              "studies?q=&sortBy=9&paging.startRow="
                              + str(1+i*50))
            txt = tree.xpath("//a[following-sibling::strong[@class='studyNo']]"
                             "/strong/text()")
            # print("For page [" + str(i) + "] there are " + str(len(txt))
            #       + " elements")
            dataset.extend(txt)
        return dataset
