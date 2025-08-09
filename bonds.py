import logging
import requests
from xml.etree import ElementTree
import os
from collections import OrderedDict
import csv
import math
import yaml


URL_BONDS = 'https://iss.moex.com/iss/history' \
            '/engines/stock/markets/bonds/securities.xml' \
            '?limit=100&date={date}&start={start}'

# Список облигаций, которые доступны только квалифицированным инвесторам
SKILLED_BONDS = []
# Список облигаций, которые доступны неквалифицированным инвесторам
UNSKILLED_BONDS = []
# Название колонки в CSV файле, для атрибута
# "только для квалифицированных инвесторов"
SKILLED_ONLY_ATTR = 'SKILLED_ONLY'


def download_bonds_xml(date, start=0):
    url = URL_BONDS.format(date=date, start=start)
    logging.debug('Request: {}'.format(url))
    r = requests.get(url)
    os.makedirs('./downloads', exist_ok=True)
    with open('./downloads/stock_bonds_{}_{}.xml'.format(date, start),
              'w', encoding='utf-8') as f:
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
    return filepath


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
    # Добавляем атрибут "только для квалифицированных инвесторов"
    attrs[SKILLED_ONLY_ATTR] = str
    return attrs


def get_bonds(xml, bond_attrs):
    bonds = []
    for row in xml.findall("data[@id='history']/rows/row"):
        bond = OrderedDict()
        for attr_name, attr_type in bond_attrs.items():
            value = row.get(attr_name)
            bond[attr_name] = attr_type(value) if value else ''
        # Добавляем значение атрибута "только для квалифицированных инвесторов"
        if bond['SECID'] in SKILLED_BONDS:
            bond[SKILLED_ONLY_ATTR] = 'True'
        elif bond['SECID'] in UNSKILLED_BONDS:
            bond[SKILLED_ONLY_ATTR] = 'False'
        else:
            bond[SKILLED_ONLY_ATTR] = ''
        bonds.append(bond)
    return bonds


def load_skilled_bonds():
    with open('config.yaml') as stream:
        global SKILLED_BONDS
        global UNSKILLED_BONDS

        config = yaml.safe_load(stream)
        logging.debug(config)
        try:
            SKILLED_BONDS = config['bonds']['skilled']
            logging.debug("config['bonds']['skilled']")
            logging.debug(SKILLED_BONDS)

            UNSKILLED_BONDS = config['bonds']['unskilled']
            logging.debug("config['bonds']['unskilled']")
            logging.debug(UNSKILLED_BONDS)
        except Exception as err:
            logging.error(err)
            logging.error(
                'Ошибка чтения списка облигаций, '
                'которые доступны только квалифицированным инвесторам.'
            )


def download_bonds(load_date):
    # Загружаем список облигаций, которые доступны только квалифицированным
    # инвесторам.
    load_skilled_bonds()

    xml_text = download_bonds_xml(load_date)
    xml_data = ElementTree.fromstring(xml_text)

    attrs = get_bond_attributes(xml_data)
    logging.debug(attrs)

    bonds = get_bonds(xml_data, attrs)
    csv_file_name = save_bonds_to_csv(
        bonds, load_date, append=False, header=attrs)

    cursor = get_cursor(xml_data)
    logging.debug(cursor)

    for i in range(1, math.ceil(cursor['total']/cursor['pagesize'])):
        xml_text = download_bonds_xml(load_date, int(i*cursor['pagesize']))
        xml_data = ElementTree.fromstring(xml_text)
        bonds = get_bonds(xml_data, attrs)
        save_bonds_to_csv(bonds, load_date)

    return csv_file_name


if __name__ == "__main__":
    load_skilled_bonds()
