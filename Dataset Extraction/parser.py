from lxml import html
import re


class DatasetNamesParser(object):


    def findCapitalizedWords(self, paragraphs):
        s = set()

        if not paragraphs:
            return s

        SMALL = "a an and as at but by en for if in of on or the to".split()
        HOT_WORDS = "Survey Program Project Study".split()

        for item in paragraphs:
            # s.update(re.findall('([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+)+)', item))
            words = item.split()
            term = ""
            article = ""
            i = 0
            while words:
                word = words.pop(0)
                if word.lower() not in SMALL:
                    if word[0].isupper():
                        term += article + word + ' '
                        article = ""
                        i += 1
                        if word[-1] in [',', '.', '?', '!'] and i > 1:
                            if any(word in term for word in HOT_WORDS):
                                s.add(term.strip())
                            term = ""
                            article = ""
                            i = 0
                    elif i > 1:
                        if any(word in term for word in HOT_WORDS):
                            s.add(term.strip())
                        term = ""
                        article = ""
                        i = 0
                    else:
                        term = ""
                        article = ""
                        i = 0
                elif i > 0:
                    article += word + ' '

        return s

    def findDatasetNames(self, path):
        tree = html.parse(path)

        title = tree.xpath('//h1[@class="svTitle"]/text()')
        doi = tree.xpath('//a[@class="S_C_ddDoi"]/text()')
        abstract = tree.xpath('//div[@class="abstract svAbstract "]/*/text()')
        legend = tree.xpath('//p[@class="legend"]/../*/text()')
        intro = tree.xpath("//p[preceding-sibling::h2[1]"
                           "[text()[contains(.,'Introduction')]]]/text()")

        # print("LEGEND: ", legend)

        dataset = set()
        dataset = dataset.union(self.findCapitalizedWords(abstract))
        dataset = dataset.union(self.findCapitalizedWords(legend))
        dataset = dataset.union(self.findCapitalizedWords(intro))

        for legend_item in legend:
            dataset.update(re.findall('(?<=Source:\s).*?(?=[,.])', legend_item))

        ans = [path, title, doi]
        ans.extend(dataset)

        return ans

    


