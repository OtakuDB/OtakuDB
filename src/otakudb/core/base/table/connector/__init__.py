from typing import TYPE_CHECKING, NoReturn

from .bonds import BondsOperator

if TYPE_CHECKING:
	from .. import BaseTable

class Connector:
	"""Оператор соединений."""

	@property
	def bonds(self) -> BondsOperator:
		"""Оператор связей."""

		return self.__bonds_operator
	
	@property
	def hyperlinks(self) -> NoReturn:
		"""Оператор гиперссылок."""

		# To-Do: реализовать межтабличные гиперссылки.

		raise NotImplementedError("Hyperlinks")

	def __init__(self, table: "BaseTable"):
		"""
		Оператор связей и гиперссылок.

		:param table: Таблица.
		:type table: BaseTable
		"""

		self.__table: "BaseTable" = table
		self.__bonds_operator: BondsOperator = BondsOperator(self.__table)