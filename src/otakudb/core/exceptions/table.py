class ManifestError(Exception):
	"""Исключение: ошибка манифеста."""

	def __init__(self, message: str):
		"""
		Исключение: ошибка манифеста.

		:param message: Сообщение об ошибке.
		:type message: str
		"""
		
		super().__init__(message)

class NoteNotFoundError(Exception):
	"""Исключение: запись не найдена."""

	def __init__(self, note_id: int):
		"""
		Исключение: запись не найдена.

		:param note_id: ID записи.
		:type note_id: int
		"""
		
		super().__init__(note_id)

class OperationError(Exception):
	"""Исключение: ошибка во время выполнения операции с таблицей."""

	def __init__(self, message: str):
		"""
		Исключение: ошибка во время выполнения операции с таблицей.

		:param message: Сообщение об ошибке.
		:type message: str
		"""
		
		super().__init__(message)