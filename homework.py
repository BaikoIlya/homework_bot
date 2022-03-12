import os
import sys
import time
import logging
from http import HTTPStatus
from requests import RequestException
import requests
import telegram
from telegram.ext import Updater
from dotenv import load_dotenv
from exceptions import WrongType, WrongKey

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Бот отправляет сообщение."""
    try:
        logging.info(f'Попытка отправить сообщение: {message}')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info('Сообщение отправлено в Телеграмм')
    except Exception as error:
        logging.error(f'Не получилось отправить из-за ошибки {error}')


def get_api_answer(current_timestamp):
    """Делаем запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logging.info(
            f'Попытка сделать запрос с параметрами: '
            f'{ENDPOINT}, {HEADERS}, {params}'
        )
        homework_status = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if homework_status.status_code != HTTPStatus.OK:
            message = 'Не доступен эндпоинт'
            logging.error(message)
            raise Exception(message)
        return homework_status.json()
    except RequestException:
        message = 'Ошибка при запросе к основному API'
        logging.error(message)


def check_response(response):
    """Проверяем в каком формате пришли данные."""
    if not isinstance(response, dict):
        logging.error(WrongType(type(response), dict))
        raise WrongType(type(response), dict)
    if 'homeworks' not in response:
        logging.error(WrongKey('homeworks', response))
        raise WrongKey('homeworks', response)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        logging.error(WrongType(type(homeworks), list))
        raise WrongType(type(homeworks), list)
    return homeworks


def parse_status(homework):
    """Проверяем наличие изменений в статусе домашней работы."""
    if 'homework_name' not in homework:
        logging.error(WrongKey('homework_name', homework))
        raise WrongKey('homework_name', homework)
    homework_name = homework.get('homework_name')
    if 'status' not in homework:
        logging.error(WrongKey('status', homework))
        raise WrongKey('status', homework)
    homework_status = homework.get('status')

    if homework_status in HOMEWORK_STATUSES:
        current_status = HOMEWORK_STATUSES[homework_status]
    else:
        message = f'Нет такого статуса: {homework_status}'
        logging.error(message)
        raise KeyError(message)

    verdict = current_status

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем есть ли все нужные ключи для работы бота."""
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logging.critical('Нет переменной PRACTICUM_TOKEN')
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        """Если нет обязательного эллеманта бот принудительно выключается"""
        raise SystemExit

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    updater = Updater(token=TELEGRAM_TOKEN)
    updater.start_polling()
    last_error = Exception
    last_status = []

    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_status = check_response(response)
            if last_status != current_status:
                for homework in current_status:
                    message = parse_status(homework)
                    send_message(bot, message)
                last_status = current_status
            else:
                logging.info('Отсутствуют новые статусы')
            current_timestamp = int(time.time())

        except Exception as error:
            """Ошибка отправляется в телеграмм только в первый раз"""
            if last_error.args == error.args:
                last_error = error
            else:
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                last_error = error
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout,
    )
    main()
