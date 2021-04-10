#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib import request
import json
from bs4 import BeautifulSoup


# get the english words
def get_frequency_list_words():
    url = "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2005/08/1-10000"
    s = request.urlopen(url)
    bs = BeautifulSoup(s)
    elems2 = bs.select('p a')
    li2 = []
    for el in elems2:
        # print(el.text)
        li2.append(el.text)

    with open('englishFrequencyList.json', 'w+', encoding='utf8') as f:
        f.write(json.dumps(li2, ensure_ascii=False))

# that is outdated (I shouldn't use the github thingy for now but instead the enchantedlearning page)
'''
import urllib
from bs4 import BeautifulSoup
url = "https://raw.githubusercontent.com/freedict/fd-dictionaries/master/eng-spa/eng-spa.tei"
s = urllib.request.urlopen(url)
bs = BeautifulSoup(s)
elems = bs.select('entry')
li = {}
for el in elems:
    li[el.find("orth").text] = [found.text for found in el.findAll("quote")]
'''

# get swedish words
def get_picture_words():
    li = {}
    for num in range(97, 123):
        letter = chr(num)
        # example: url = "https://www.enchantedlearning.com/languages/swedish/Tisfor.shtml"
        url = "https://www.enchantedlearning.com/languages/swedish/" + letter.upper() +"isfor.shtml"
        s = request.urlopen(url)
        bs = BeautifulSoup(s)
        elems = [el for el in bs.select('td') if el.find("img")]
        for el in elems:
            # this is still not the best solution for every word pair
            findings = el.findAll('b')
            if findings:
                if len(findings) == 2:
                    k, v = findings[0].text, findings[1].text
                    found = k.rfind(v)
                    if found not in [-1, 0]:
                        k = k[:found]
                    li[k] = v

    removeKeys = []
    for k, v in li.items():
        if k == '' or v == '':
            removeKeys.append(k)
    for k in removeKeys:
        del li[k]

    # put dict li in a json file, encode it as utf-8
    # https://stackoverflow.com/questions/18337407/saving-utf-8-texts-in-json-dumps-as-utf8-not-as-u-escape-sequence
    with open('swedishTranslations.json', 'w+', encoding='utf8') as f:
        f.write(json.dumps(li, ensure_ascii=False))


# get_frequency_list_words()
get_picture_words()
