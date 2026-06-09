from ._Base import BaseContainer

from typing import Any

class Custom(BaseContainer):
	"""Дополнительные опции."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Data = dict()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

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
		self.save()

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = data

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return self.__Data.copy()
