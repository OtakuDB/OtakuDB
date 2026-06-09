from typing import Any, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
	from .. import Manifest

class BaseContainer(ABC):
	"""Базовый контейнер секции манифеста."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""
		Базовый контейнер секции манифеста.

		:param manifest: Манифест.
		:type manifest: Manifest
		"""

		self._Manifest = manifest

		self._PostInitMethod()

	@abstractmethod
	def parse(self, data: dict[str, Any]):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict[str, Any]
		"""

		pass

	def save(self):
		"""Сохраняет манифест в локальный файл JSON."""

		self._Manifest.save()

	@abstractmethod
	def to_dict(self) -> dict[str, Any]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, Any]
		"""

		pass