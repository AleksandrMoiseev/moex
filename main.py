import logging
import requests
from xml.etree import ElementTree
import math
import os
from collections import OrderedDict
import csv
import argparse
# from datetime import datetime


URL_BONDS = 'https://iss.moex.com/iss/history' \
            '/engines/stock/markets/bonds/securities.xml' \
            '?limit=100&date={date}&start={start}'


def download_bonds_xml(date, start=0):
    url = URL_BONDS.format(date=date, start=start)

    logging.debug('Request: {}'.format(url))

    r = requests.get(url)

    os.makedirs('./downloads', exist_ok=True)
    with open('./downloads/stock_bonds_{}_{}.xml'.format(date, start),
              'w') as f:
        f.write(r.text)

    return r.text


def save_bonds_to_csv(bonds, date, append=True, header=None):
    os.makedirs('./csv', exist_ok=True)
    filepath = './csv/stock_bonds_{}.csv'.format(date)
    csvfile = open(filepath, 'a' if append else 'w',
                   newline='', encoding='utf-8')
    writer = csv.writer(csvfile)
    if header:
        writer.writerow(header.keys())
    for bond in bonds:
        writer.writerow(bond.values())
    csvfile.close()


def get_cursor(xml):
    for row in xml.findall("data[@id='history.cursor']/rows/row[@TOTAL]"):
        return {
            'total': int(row.get('TOTAL', 0)),
            'index': int(row.get('INDEX', 0)),
            'pagesize': int(row.get('PAGESIZE', 0))
        }


def get_bond_attributes(xml):
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


def get_bonds(xml, bond_attrs):
    bonds = []
    for row in xml.findall("data[@id='history']/rows/row"):
        bond = OrderedDict()
        for attr_name, attr_type in bond_attrs.items():
            value = row.get(attr_name)
            bond[attr_name] = attr_type(value) if value else ''
        bonds.append(bond)
    return bonds


def configure_logging():
    logging.basicConfig(
        format='%(levelname)-7s:%(asctime)s: %(message)s',
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler('moex.log'),
            logging.StreamHandler()])
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description='Загрузка данных об облигациях с сайта Московской биржи')
    arg_parser.add_argument(
        '--date',
        required=True,
        help='Дата торгов в формате YYYY-MM-DD',
    )
    return arg_parser.parse_args()


def main(load_date):
    xml_text = download_bonds_xml(load_date)
    xml_data = ElementTree.fromstring(xml_text)

    attrs = get_bond_attributes(xml_data)
    logging.debug(attrs)

    bonds = get_bonds(xml_data, attrs)
    save_bonds_to_csv(bonds, load_date, append=False, header=attrs)

    cursor = get_cursor(xml_data)
    logging.debug(cursor)

    for i in range(1, math.ceil(cursor['total']/cursor['pagesize'])):
        xml_text = download_bonds_xml(load_date, int(i*cursor['pagesize']))
        xml_data = ElementTree.fromstring(xml_text)
        bonds = get_bonds(xml_data, attrs)
        save_bonds_to_csv(bonds, load_date)


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    main(args.date)
    # main('2024-08-22')