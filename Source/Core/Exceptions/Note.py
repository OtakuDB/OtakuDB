#==========================================================================================#
# >>>>> МЕТАДАННЫЕ <<<<< #
#==========================================================================================#

class MetainfoBlocked(Exception):
	"""Исключение: поле метаданных не описано и свободный режим отключён."""

	def __init__(self, message: str | None = None):
		"""
		Исключение: поле метаданных не описано и свободный режим отключён.

		:param message: Описание ошибки.
		:type message: str | None
		"""

		super().__init__(message or "Metainfo field not described and free metainfo denied.")

class MetainfoFieldNotDescribed(Exception):
	"""Исключение: поле метаданных не описано."""

	def __init__(self, field: str):
		"""
		Исключение: поле метаданных не описано.

		:param field: Имя поля метаданных.
		:type field: str
		"""

		super().__init__(field)

class MetainfoFieldIncorrectTyping(Exception):
	"""Исключение: неверный тип значения поля метаданных."""

	def __init__(self, field: str, value_type: type, allowed_types: tuple[type, ...]):
		"""
		_summary_

		:param field: _description_
		:type field: str
		:param value_type: _description_
		:type value_type: type
		:param allowed_types: _description_
		:type allowed_types: tuple[type, ...]
		"""

		super().__init__(field)

class MetainfoFieldEnlistingDenied(Exception):
	"""Исключение: использование списков в поле метаданных запрещено."""

	def __init__(self, field: str):
		"""
		Исключение: использование списков в поле метаданных запрещено.

		:param field: Имя поля метаданных.
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

class BondAlreadyDescribed(Exception):
	"""Исключение: связь уже описана."""

	def __init__(self, bond_name: str):
		"""
		Исключение: связь уже описана.

		:param bond_name: Имя связи.
		:type bond_name: str
		"""

		super().__init__(bond_name)

class MaxBindedNotesCountReached(Exception):
	"""Исключение: достигнуто максимальное количество прикрепляемых записей."""

	def __init__(self, bond_name: str, count: int):
		"""
		Исключение: достигнуто максимальное количество прикрепляемых записей.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param count: Максимальное количество записей.
		:type count: int
		"""

		super().__init__(f"For \"{bond_name}\" bond allowed only {count} notes.")

class BondNotDescribed(Exception):
	"""Исключение: связь не описана."""

	def __init__(self, bond_name: str):
		"""
		Исключение: связь не описана.

		:param bond_name: Имя связи.
		:type bond_name: str
		"""

		super().__init__(bond_name)