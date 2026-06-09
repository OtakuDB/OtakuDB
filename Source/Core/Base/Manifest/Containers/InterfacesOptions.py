from ._Base import BaseContainer

from Source.Interfaces.Enums import Interfaces

from dublib.Methods.Data import Copy

from typing import Any

class InterfacesOptions(BaseContainer):
	"""Опции интерфейсов."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Data = {Element.value: dict() for Element in Interfaces}

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
		if Value: Value = Copy(Value)
		else: Value = dict()
		
		return Value

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = data

	def set_options(self, interface: Interfaces, options: dict[str, Any], save: bool = True):
		"""
		Задаёт словарь параметров интерфейса.

		:param interface: Интерфейс.
		:type interface: Interfaces
		:param options: Словарь параметров.
		:type options: dict[str, Any]
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		"""

		self.__Data[interface.value] = options
		if save: self.save()

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return Copy(self.__Data)