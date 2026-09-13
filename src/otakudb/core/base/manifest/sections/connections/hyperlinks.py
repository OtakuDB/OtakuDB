from .._base import BaseSection

class HyperlinksParameters(BaseSection):
	"""Параметры гиперссылок."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__hyperlinks = data

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__hyperlinks: dict = {}

	def _to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return self.__hyperlinks.copy()
