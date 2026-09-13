from typing import Any

from dublib.functions.data import deep_copy

from ....interfaces.enums import Interfaces
from ._base import BaseSection

class InterfacesOptions(BaseSection):
	"""Опции интерфейсов."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__data = data

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__data: dict[str, dict] = {interface.value: {} for interface in Interfaces}

	def _to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return deep_copy(self.__data)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def get_options(self, interface: Interfaces) -> dict[str, Any]:
		"""
		Возвращает копию словаря параметров интерфейса.

		:param interface: Интерфейс.
		:type interface: Interfaces
		:return: Копия словаря параметров интерфейса.
		:rtype: dict[str, Any]
		"""

		value: dict[str, Any] | None = self.__data.get(interface.value)
		
		return deep_copy(value) if value else {}

	def set_options(self, interface: Interfaces, options: dict[str, Any]):
		"""
		Задаёт словарь параметров интерфейса.

		:param interface: Интерфейс.
		:type interface: Interfaces
		:param options: Словарь параметров.
		:type options: dict[str, Any]
		"""

		self.__data[interface.value] = options
