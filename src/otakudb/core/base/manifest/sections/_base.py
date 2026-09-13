from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
	from .. import Manifest

class BaseSection(ABC):
	"""Базовая секция манифеста."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _parse(self, data: dict[str, Any]):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict[str, Any]
		"""

		pass

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	@abstractmethod
	def _to_dict(self) -> dict[str, Any]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, Any]
		"""

		return {}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""
		Базовая секция манифеста.

		:param manifest: Манифест.
		:type manifest: Manifest
		"""

		self._manifest: "Manifest" = manifest

		self._post_init()

	def parse(self, data: dict[str, Any]):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict[str, Any]
		"""

		self._parse(data)

	def to_dict(self) -> dict[str, Any]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, Any]
		"""

		return self._to_dict()