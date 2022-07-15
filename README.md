### Описание:

Данный Telegram-bot создан для оповещения об изменении статуса домашней работы.

Бот в автономном режиме делает запросы к API и в случае изменения данных отправляет соответствующее сообщщение в Telegram.

Бот загружен и Heroku и работает в автономном режиме.

### Установка:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/BaikoIlya/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
Открыть файл с кодом:

```
homework.py
```

Внести собственные значения ключей:

```
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
```

Запустить этот файл.
