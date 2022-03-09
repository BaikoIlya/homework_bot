import logging
import os
import telegram
import time
import sys
import requests
from http import HTTPStatus
from dotenv import load_dotenv
from requests import RequestException
from telegram.ext import Updater


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

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

"""Функция на случай если нужна отдельная,
   потому что в задании не совсем понятно как должны отправляться сообщения"""
# last_error_send = None
# bot_send = telegram.Bot(token=TELEGRAM_TOKEN)
#
#
# def send_error(error, message):
#     global last_error_send
#     if last_error_send != error:
#         bot_send.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
#     last_error_send = error


def send_message(bot, message):
    """Бот отправляет сообщение"""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info('Сообщение отправлено в Телеграмм')
    except Exception as error:
        logger.error(f'Не получилось отправить из-за ошибки {error}')


def get_api_answer(current_timestamp):
    """Делаем запрос к API"""

    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_status = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if homework_status.status_code != HTTPStatus.OK:
            message = 'Не доступен эндпоинт'
            # send_error(TypeError, message=message)
            logger.error(message)
            raise Exception(message)
        return homework_status.json()
    except RequestException:
        message = 'Ошибка при запросе к основному API'
        # send_error(TypeError, message=message)
        logger.error(message)


def check_response(response):
    """Проверяем в каком формате пришли данные"""
    if type(response) != dict:
        message = 'Ответ не в формате Python'
        # send_error(TypeError, message=message)
        logger.error(message)
        raise TypeError(message)
    else:
        if response.get('homeworks') is None:
            message = 'Отсутствует ключ homeworks'
            # send_error(KeyError, message=message)
            logger.error(message)
            raise KeyError(message)
        else:
            homeworks = response.get('homeworks')
        if type(homeworks) != list:
            message = 'homeworks не список'
            # send_error(TypeError, message=message)
            logger.error(message)
            raise TypeError(message)
        else:
            return homeworks


def parse_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status in HOMEWORK_STATUSES:
        current_status = HOMEWORK_STATUSES[homework_status]
    else:
        message = f'Нет такого статуса: {homework_status}'
        # send_error(KeyError, message=message)
        logger.error(message)
        raise KeyError(message)

    verdict = current_status

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем есть ли все нужные ключи для работы бота"""
    if PRACTICUM_TOKEN is None:
        logger.critical('Нет переменной PRACTICUM_TOKEN')
        return False
    if PRACTICUM_TOKEN == '':
        logger.critical('Не заполенена переменная PRACTICUM_TOKEN')
        return False
    elif TELEGRAM_TOKEN is None:
        logger.critical('Нет переменной TELEGRAM_TOKEN')
        return False
    elif TELEGRAM_TOKEN == '':
        logger.critical('Не заполнена перемення TELEGRAM_TOKEN')
        return False
    elif TELEGRAM_CHAT_ID is None:
        logger.critical('Нет переменной TELEGRAM_CHAT_ID')
        return False
    elif TELEGRAM_CHAT_ID == '':
        logger.critical('Не заполена переменная TELEGRAM_CHAT_ID')
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
    updater.idle()
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
                logger.debug('Отсутствуют новые статусы')
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            """Ошибка отправляется в телеграмм только в первый раз"""
            if last_error.args == error.args:
                last_error = error
            else:
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                last_error = error
            time.sleep(RETRY_TIME)
        # else:
            # ...


if __name__ == '__main__':
    main()
