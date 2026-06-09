class NoteNotFound(Exception):
	"""Исключение: запись не найдена."""

	def __init__(self, id: int):
		"""
		Исключение: запись не найдена.

		:param id: ID записи.
		:type id: int
		"""
		
		super().__init__(f"Note #{id} not found.")

class OperationError(Exception):
	"""Исключение: ошибка во время выполнения операции с таблицей."""

	def __init__(self, message: str):
		"""
		Исключение: ошибка во время выполнения операции с таблицей.

		:param message: Сообщение об ошибке.
		:type message: str
		"""
		
		super().__init__(message)