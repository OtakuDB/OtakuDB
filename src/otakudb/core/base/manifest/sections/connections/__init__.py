from .._base import BaseSection
from .bonds import BondsParameters
from .hyperlinks import HyperlinksParameters

class ConnectionsSection(BaseSection):
	"""Параметры соединений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def bonds(self) -> BondsParameters:
		"""Параметры соединений."""

		return self.__bonds
	
	@property
	def hyperlinks(self) -> HyperlinksParameters:
		"""Параметры гиперссылок."""

		return self.__hyperlinks

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _parse(self, data: dict[str, dict]):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict[str, dict]
		"""

		self.__bonds.parse(data.get("bonds", {}))
		self.__hyperlinks.parse(data.get("hyperlinks", {}))

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__bonds = BondsParameters(self._manifest)
		self.__hyperlinks = HyperlinksParameters(self._manifest)

	def _to_dict(self) -> dict[str, dict]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, dict]
		"""

		return {
			"bonds": self.__bonds.to_dict(),
			"hyperlinks": self.__hyperlinks.to_dict()
		}
