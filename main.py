import logging
import argparse

from bonds import download_bonds
from shares import download_shares


def configure_logging():
    logging.basicConfig(
        format='%(levelname)-7s:%(asctime)s: %(message)s',
        level=logging.INFO,  # DEBUG
        handlers=[
            logging.FileHandler('moex.log', 'w', 'utf-8'),
            logging.StreamHandler()])
    # logging.getLogger('urllib3').setLevel(logging.WARNING)


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description='Загрузка данных об облигациях и акциях '
                    'с сайта Московской биржи')
    arg_parser.add_argument(
        '--date',
        required=True,
        help='Дата торгов в формате YYYY-MM-DD',
    )
    return arg_parser.parse_args()


def main(load_date):
    logging.info('Начинается загрузка данных о торгах облигациями'
                 ' на {}'.format(load_date))
    csv_file_name = download_bonds(load_date)
    logging.info('Файл "{}" сформирован.'.format(csv_file_name))
    
    logging.info('Начинается загрузка данных о торгах акциями'
                 ' на {}'.format(load_date))
    csv_file_name = download_shares(load_date)
    logging.info('Файл "{}" сформирован.'.format(csv_file_name))


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    main(args.date)

