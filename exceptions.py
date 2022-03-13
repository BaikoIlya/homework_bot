class WrongType(TypeError):
    """Исключение возникает при не верном классе."""

    def __init__(self, cur_type, need_type):
        self.cur_type = cur_type
        self.need_type = need_type
        message = (
            f'Полученный класс {self.cur_type} '
            f'не соответствует ожидаемому {self.need_type}'
        )
        super().__init__(message)


class WrongKey(KeyError):
    """Исключение возникает при не верном ключе."""

    def __init__(self, cur_key, cur_dict):
        self.cur_key = cur_key
        self.cur_dict = cur_dict
        message = (
            f'Полученного ключа {self.cur_key} '
            f'нет в словаре {self.cur_dict}'
        )
        super().__init__(message)


class WrongStatusCode(Exception):
    """Исключение возникает при статус коде не 200"""

    def __init__(self, status_code):
        self.status_code = status_code
        message = (
            f'При попытке подключения к API произошёл сбой, '
            f'статус запроса {self.status_code}'
        )
        super().__init__(message)


class ApiException(Exception):
    """Проброс ошибки RequestExeption"""

    def __init__(self):
        message = (
            'Ошибка при запросе к основному API'
        )
        super().__init__(message)
