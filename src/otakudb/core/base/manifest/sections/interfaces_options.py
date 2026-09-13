from typing import Any

from dublib.functions.data import deep_copy

from Source.interfaces.enums import Interfaces

from ._base import BaseSection

class InterfacesOptions(BaseSection):
	"""Опции интерфейсов."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Data = {Element.value: {} for Element in Interfaces}

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

		Value = self.__Data.get(interface.value)
		if Value: Value = deep_copy(Value)
		else: Value = {}
		
		return Value

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = data

	def set_options(self, interface: Interfaces, options: dict[str, Any]):
		"""
		Задаёт словарь параметров интерфейса.

		:param interface: Интерфейс.
		:type interface: Interfaces
		:param options: Словарь параметров.
		:type options: dict[str, Any]
		"""

		self.__Data[interface.value] = options

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return deep_copy(self.__Data)