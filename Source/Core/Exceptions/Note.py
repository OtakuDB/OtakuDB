class LocalBindsDenied(Exception):
	"""Исключение: прикрепление записей той же таблицы к текущей записи запрещено."""

	def __init__(self):
		"""Исключение: прикрепление записей той же таблицы к текущей записи запрещено"""

		super().__init__("Binding same table notes blocked by manifest.")

class MetainfoBlocked(Exception):
	"""Исключение: невозможно задать метаданные."""

	def __init__(self):
		"""Исключение: невозможно задать метаданные."""

		super().__init__("Metainfo filtered by manifest or denied.")

class AttachmentsDenied(Exception):
	"""Исключение: прикрепление вложений к записи запрещено."""

	def __init__(self, allow_slots: bool):
		"""
		Исключение: прикрепление вложений к записи запрещено.

		:param allow_slots: Состояние: запрещены ли вложения в слоты.
		:type allow_slots: bool
		"""

		Message = "Attachments denied by table manifest."
		if allow_slots: Message = "Allowed only slots attachments."
		super().__init__(Message)

class AttachmentSlotAlreadyFilled(Exception):
	"""Исключение: слот уже содержит файл."""

	def __init__(self, slot: str):
		"""
		Исключение: слот уже содержит файл.

		:param slot: Имя слота.
		:type slot: str
		"""

		super().__init__(f"Slot \"{slot}\" already contains file.")