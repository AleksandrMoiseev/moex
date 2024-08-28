import logging
import argparse

from bonds import download_bonds


def configure_logging():
    logging.basicConfig(
        format='%(levelname)-7s:%(asctime)s: %(message)s',
        level=logging.INFO,  # DEBUG
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
    arg_parser.add_argument(
        '-u', '--unskilled',
        help='Убрать облигации, '
             'которые доступны только квалифицированным инвесторам',
        action='store_true'  # on/off flag
    )
    return arg_parser.parse_args()


def main(load_date):
    logging.info('Начинается загрузка данных о торгах облигациями'
                 ' на {}'.format(load_date))
    csv_vile_name = download_bonds(load_date)
    logging.info('Файл "{}" сформирован.'.format(csv_vile_name))


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    main(args.date)
    # main('2024-08-27')
