from Source.Core.Enums import Interfaces

from typing import Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
	from . import Manifest

class Attachments:
	"""Параметры вложений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def rule(self) -> bool:
		"""Правило использования вложений. 0 – запрещены все, 1 – разрешены только слоты, 2 – разрешены все."""

		return self.__Data["rule"]

	@property
	def slots(self) -> dict[str, str | None]:
		"""Определения слотов, предназначенных для особого взаимодействия."""

		return self.__Data["slots"].copy()

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""Параметры вложений."""

		self.__Manifest = manifest

		self.__Data: dict[str, bool | dict] = {
			"rule": 1,
			"slots": {}
		}

	def add_slot(self, slot: str, description: str | None):
		"""
		Резервирует слот вложений для особого взаимодействия.

		:param slot: Название слота.
		:type slot: str
		:param description: Описание слота.
		:type description: str | None
		"""

		self.__Data["slots"][slot] = description
		self.__Manifest.save()

	def get_slot_description(self, slot: str) -> str | None:
		"""
		Возвращает описание слота.

		:param slot: Имя слота.
		:type slot: str
		:return: Описание.
		:rtype: str | None
		:raises KeyError: Слот не определён.
		"""

		return self.__Data["slots"][slot]

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data

	def remove_slot(self, slot: str):
		"""
		Удаляет слот вложений.

		:param slot: Название слота.
		:type slot: str
		:raises KeyError: Слот отсутствует.
		"""

		del self.__Data["slots"][slot]
		self.__Manifest.save()

	def set_attachments_rule(self, rule: Literal[0, 1, 2]):
		"""
		Задаёт правило использования вложений. 0 – запрещены все, 1 – разрешены только слоты, 2 – разрешены все.

		:param rule: _description_
		:type rule: Literal[0, 1, 2]
		"""

		self.__Data["rule"] = rule
		self.__Manifest.save()

	def to_dict(self) -> dict[str, bool | dict]:
		"""
		Возвращает словарное представление общих опций.

		:return: Словарное представление общих опций.
		:rtype: dict[str, bool | dict]
		"""

		return self.__Data.copy()

class Common:
	"""Общие опции таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def binds(self) -> bool:
		"""Указывает, разрешено ли прикреплять к записи другие записи той же таблицы."""

		return self.__Data["binds"]

	@property
	def recycle_id(self) -> bool:
		"""Указывает, необходимо ли занимать освободившиеся ID."""

		return self.__Data["recycle_id"]

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""Общие опции таблицы."""

		self.__Manifest = manifest

		self.__Data = {
			"recycle_id": True,
			"binds": False
		}

	def switch_binds(self, status: bool):
		"""
		Переключает состояние использования локальных связей.

		:param status: Состояние использования локальных связей.
		:type status: bool
		"""

		self.__Data["binds"] = status
		self.__Manifest.save()

	def switch_recycle_id(self, status: bool):
		"""
		Переключает состояние утилизации свободных ID.

		:param status: Состояние утилизации свободных ID.
		:type status: bool
		"""

		self.__Data["recycle_id"] = status
		self.__Manifest.save()

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data

	def to_dict(self) -> dict[str, bool | dict]:
		"""
		Возвращает словарное представление общих опций.

		:return: Словарное представление общих опций.
		:rtype: dict[str, bool | dict]
		"""

		return self.__Data.copy()

class Custom:
	"""Дополнительные опции."""

	def __init__(self, manifest: "Manifest"):
		"""Общие опции таблицы."""

		self.__Manifest = manifest

		self.__Data = dict()

	def __getitem__(self, key: str) -> Any:
		"""
		Возвращает значение опции.

		:param key: Ключ опции.
		:type key: str
		:return: Значение.
		:rtype: Any
		:raises KeyError: Опция не найдена.
		"""

		return self.__Data[key]
	
	def __setitem__(self, key: str, value: Any):
		"""
		Задаёт значение опции.

		:param key: Ключ опции.
		:type key: str
		:param value: Значение опции.
		:type value: str
		"""

		self.__Data[key] = value
		self.__Manifest.save()

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = data

	def to_dict(self) -> dict[str, bool | dict]:
		"""
		Возвращает словарное представление дополнительных опций.

		:return: Словарное представление дополнительных опций.
		:rtype: dict[str, bool | dict]
		"""

		return self.__Data.copy()

class InterfacesOptions:
	"""Опции интерфейсов."""

	def __init__(self, manifest: "Manifest"):
		"""
		Опции интерфейсов.

		:param manifest: Манифест таблицы.
		:type manifest: Manifest
		"""

		self.__Manifest = manifest

		self.__Data = {Element.value: dict() for Element in Interfaces}

	def get_options(self, interface: Interfaces) -> dict[str, Any]:
		"""
		Возвращает копию словаря параметров интерфейса.

		:param interface: Интерфейс.
		:type interface: Interfaces
		:return: Копия словаря параметров интерфейса.
		:rtype: dict[str, Any]
		"""

		Value = self.__Data.get(interface.value)
		if Value: Value = Value.copy()
		else: Value = dict()
		
		return Value

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data

	def save(self):
		"""Сохраняет манифест."""

		self.__Manifest.save()

	def set_options(self, interface: Interfaces, options: dict[str, Any]):
		"""
		Задаёт словарь параметров интерфейса.

		:param interface: Интерфейс.
		:type interface: Interfaces
		:param options: Словарь параметров.
		:type options: dict[str, Any]
		"""

		self.__Data[interface.value] = options
		self.save()

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление опций.

		:return: Словарное представление опций.
		:rtype: dict
		"""

		return self.__Data.copy()
