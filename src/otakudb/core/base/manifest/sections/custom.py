from typing import Any

from ._base import BaseSection

class CustomSection(BaseSection):
	"""Дополнительные опции."""

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

		self.__data: dict = {}

	def _to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return self.__data.copy()

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

		return self.__data[key]
	
	def __setitem__(self, key: str, value: Any):
		"""
		Задаёт значение опции.

		:param key: Ключ опции.
		:type key: str
		:param value: Значение опции.
		:type value: str
		"""

		self.__data[key] = value
