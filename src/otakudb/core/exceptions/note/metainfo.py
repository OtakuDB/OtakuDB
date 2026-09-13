class MetainfoBlockedError(Exception):
	"""Исключение: поле метаданных не описано и свободный режим отключён."""

	def __init__(self, message: str | None = None):
		"""
		Исключение: поле метаданных не описано и свободный режим отключён.

		:param message: Описание ошибки.
		:type message: str | None
		"""

		super().__init__(message or "Metainfo field not described and free metainfo denied.")

class MetainfoFieldNotDescribedError(Exception):
	"""Исключение: поле метаданных не описано."""

	def __init__(self, field: str):
		"""
		Исключение: поле метаданных не описано.

		:param field: Имя поля метаданных.
		:type field: str
		"""

		super().__init__(field)

class MetainfoFieldIncorrectTypingError(Exception):
	"""Исключение: неверный тип значения поля метаданных."""

	def __init__(self, field: str, value_type: type, allowed_types: tuple[type, ...]):
		"""
		Исключение: неверный тип значения поля метаданных.

		:param field: Имя поля метаданных.
		:type field: str
		:param value_type: Тип значения.
		:type value_type: type
		:param allowed_types: Разрешённые типы.
		:type allowed_types: tuple[type, ...]
		"""

		allowed: str = ", ".join(str(element) for element in allowed_types)
		super().__init__(f"Value of {field} is {value_type}, allowed: {allowed}.")

class MetainfoFieldEnlistingDeniedError(Exception):
	"""Исключение: использование списков в поле метаданных запрещено."""

	def __init__(self, field: str):
		"""
		Исключение: использование списков в поле метаданных запрещено.

		:param field: Имя поля метаданных.
		:type field: str
		"""

		super().__init__(field)
