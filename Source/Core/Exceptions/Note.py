class LocalBindsDenied(Exception):
	"""Исключение: прикрепление записей той же таблицы к текущей записи запрещено."""

	def __init__(self):
		"""Исключение: прикрепление записей той же таблицы к текущей записи запрещено"""

		super().__init__("Binding same table notes blocked by manifest.")

#==========================================================================================#
# >>>>> МЕТАДАННЫЕ <<<<< #
#==========================================================================================#

class MetainfoBlocked(Exception):
	"""Исключение: невозможно задать метаданные."""

	def __init__(self, message: str | None = None):
		"""
		Исключение: невозможно задать метаданные.

		:param message: Описание ошибки.
		:type message: str | None
		"""

		super().__init__(message or "Metainfo filtered by manifest or denied.")

class MetainfoFieldNotDescribed(Exception):
	"""Исключение: поле метаданных не описано."""

	def __init__(self, field: str):
		"""
		Исключение: поле метаданных не описано.

		:param field: Название поля метаданных.
		:type field: str
		"""

		super().__init__(field)

#==========================================================================================#
# >>>>> ВЛОЖЕНИЯ <<<<< #
#==========================================================================================#

class AttachmentsDenied(Exception):
	"""Исключение: прикрепление вложений к записи запрещено."""

	def __init__(self, is_slots_allowed: bool):
		"""
		Исключение: прикрепление вложений к записи запрещено.

		:param allow_slots: Состояние: разрешены ли вложения в слоты.
		:type allow_slots: bool
		"""

		Message = "Attachments denied by table manifest."
		if is_slots_allowed: Message = "Allowed only slots attachments."
		super().__init__(Message)

class AttachmentSlotAlreadyDescribed(Exception):
	"""Исключение: слот уже описан."""

	def __init__(self, slot: str):
		"""
		Исключение: слот уже описан.

		:param slot: Имя слота.
		:type slot: str
		"""

		super().__init__(slot)

class AttachmentSlotAlreadyFilled(Exception):
	"""Исключение: слот уже содержит файл."""

	def __init__(self, slot: str):
		"""
		Исключение: слот уже содержит файл.

		:param slot: Имя слота.
		:type slot: str
		"""

		super().__init__(slot)

class AttachmentSlotNotDescribed(Exception):
	"""Исключение: слот не описан."""

	def __init__(self, slot: str):
		"""
		Исключение: слот не описан.

		:param slot: Имя слота.
		:type slot: str
		"""

		super().__init__(slot)

#==========================================================================================#
# >>>>> СВЯЗИ <<<<< #
#==========================================================================================#

class LocalBindAlreadyDescribed(Exception):
	"""Исключение: локальное соединение уже описано."""

	def __init__(self, connection: str):
		"""
		Исключение: локальное соединение уже описано.

		:param connection: Имя соединения.
		:type connection: str
		"""

		super().__init__(connection)

class LocalBindNotDescribed(Exception):
	"""Исключение: локальное соединение не описано."""

	def __init__(self, connection: str):
		"""
		Исключение: локальное соединение не описано.

		:param connection: Имя соединения.
		:type connection: str
		"""

		super().__init__(connection)