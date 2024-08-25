import logging
import requests
from xml.etree import ElementTree
import math


URL_BONDS='https://iss.moex.com/iss/history/engines/stock/markets/bonds/securities.xml' \
          '?limit=100&date={date}&start={start}'


def download_bonds_xml(date, start=0):
    url = URL_BONDS.format(date=date, start=start)

    logging.debug('Request: {}'.format(url))

    r = requests.get(url)

    with open('./data/stock_bonds_{}_{}.xml'.format(date, start), 'w') as f:
        f.write(r.text)

    return r.text


def get_cursor(xml):
    for row in xml.findall("data[@id='history.cursor']/rows/row[@TOTAL]"):
        return {
            'total': int(row.get('TOTAL', 0)),
            'index': int(row.get('INDEX', 0)),
            'pagesize': int(row.get('PAGESIZE', 0))
        }


def main():
    xml_text = download_bonds_xml('2024-08-23')

    xml_data = ElementTree.fromstring(xml_text)

    cursor = get_cursor(xml_data)
    logging.debug(cursor)
    
    for i in range(1, math.ceil(cursor['total']/cursor['pagesize'])):
        xml_text = download_bonds_xml('2024-08-23', int(i*cursor['pagesize']))


if __name__ == "__main__":
    main()