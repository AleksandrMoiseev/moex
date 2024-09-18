import logging
import requests
from xml.etree import ElementTree
import os
from collections import OrderedDict
import csv
import math


URL_SHARES = 'https://iss.moex.com/iss/history' \
            '/engines/stock/markets/shares/securities.xml' \
            '?limit=100&date={date}&start={start}'


def download_shares_xml(date, start=0):
    url = URL_SHARES.format(date=date, start=start)
    logging.debug('Request: {}'.format(url))
    r = requests.get(url)
    os.makedirs('./downloads', exist_ok=True)
    with open('./downloads/stock_shares_{}_{}.xml'.format(date, start),
              'w') as f:
        f.write(r.text)
    return r.text


def save_shares_to_csv(shares, date, append=True, header=None):
    os.makedirs('./csv', exist_ok=True)
    filepath = './csv/stock_shares_{}.csv'.format(date)
    csvfile = open(filepath, 'a' if append else 'w',
                   newline='', encoding='utf-8')
    writer = csv.writer(csvfile)
    if header:
        writer.writerow(header.keys())
    for share in shares:
        writer.writerow(share.values())
    csvfile.close()
    return filepath


def get_cursor(xml):
    for row in xml.findall("data[@id='history.cursor']/rows/row[@TOTAL]"):
        return {
            'total': int(row.get('TOTAL', 0)),
            'index': int(row.get('INDEX', 0)),
            'pagesize': int(row.get('PAGESIZE', 0))
        }


def get_share_attributes(xml):
    TYPES_MAP = {
        'string': str,
        'date': str,
        'time': str,
        'double': float,
        'int32': int,
        'int64': int,
    }
    attrs = OrderedDict()
    for row in xml.findall("data[@id='history']/metadata/columns/column"):
        attrs[row.get('name')] = TYPES_MAP.get(row.get('type'), str)
    return attrs


def get_shares(xml, share_attrs):
    shares = []
    for row in xml.findall("data[@id='history']/rows/row"):
        share = OrderedDict()
        for attr_name, attr_type in share_attrs.items():
            value = row.get(attr_name)
            share[attr_name] = attr_type(value) if value else ''
        shares.append(share)
    return shares


def download_shares(load_date):
    xml_text = download_shares_xml(load_date)
    xml_data = ElementTree.fromstring(xml_text)

    attrs = get_share_attributes(xml_data)
    logging.debug(attrs)

    shares = get_shares(xml_data, attrs)
    csv_file_name = save_shares_to_csv(
        shares, load_date, append=False, header=attrs)

    cursor = get_cursor(xml_data)
    logging.debug(cursor)

    for i in range(1, math.ceil(cursor['total']/cursor['pagesize'])):
        xml_text = download_shares_xml(load_date, int(i*cursor['pagesize']))
        xml_data = ElementTree.fromstring(xml_text)
        bonds = get_shares(xml_data, attrs)
        save_shares_to_csv(bonds, load_date)

    return csv_file_name


if __name__ == "__main__":
    download_shares('2024-09-17')
