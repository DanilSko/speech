# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from sentimental import Sentimental

sent = Sentimental()


def read_xml(text):
    return BeautifulSoup(text, "lxml")


def add_attributes(xml):
    saids = xml.findAll('said')
    for said in saids:
        said['aloud'] = 'True'
        said['type'] = 'direct'
        said['characteristic'] = define_characteristic(said)


def define_characteristic(said):
    result = sent.analyze(said.text)
    result = {'negative': result['negative'], 'positive': result["positive"]}
    if result['negative'] == result['positive']:
        sentiment = 'neutral'
    else:
        sentiment = sorted(result.items(),
                           key=lambda x: x[1], reverse=True)[0][0]
    return sentiment
