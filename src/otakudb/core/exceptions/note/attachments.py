class AttachmentsDeniedError(Exception):
	"""Исключение: прикрепление вложений к записи запрещено."""

	def __init__(self, is_slots_allowed: bool):
		"""
		Исключение: прикрепление вложений к записи запрещено.

		:param allow_slots: Состояние: разрешены ли вложения в слоты.
		:type allow_slots: bool
		"""

		super().__init__("Allowed only slots attachments." if is_slots_allowed else "Attachments denied by table manifest.")

class AttachmentSlotAlreadyDescribedError(Exception):
	"""Исключение: слот уже описан."""

	def __init__(self, slot: str):
		"""
		Исключение: слот уже описан.

		:param slot: Имя слота.
		:type slot: str
		"""

		super().__init__(slot)

class AttachmentSlotAlreadyFilledError(Exception):
	"""Исключение: слот уже содержит файл."""

	def __init__(self, slot: str):
		"""
		Исключение: слот уже содержит файл.

		:param slot: Имя слота.
		:type slot: str
		"""

		super().__init__(slot)

class AttachmentSlotNotDescribedError(Exception):
	"""Исключение: слот не описан."""

	def __init__(self, slot: str):
		"""
		Исключение: слот не описан.

		:param slot: Имя слота.
		:type slot: str
		"""

		super().__init__(slot)
