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
