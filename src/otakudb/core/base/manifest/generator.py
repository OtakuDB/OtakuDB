from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from . import Manifest

if TYPE_CHECKING:
	from pathlib import Path

class ManifestGenerator(ABC):
	"""Генератор манифеста."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _edit_manifest(self, manifest: Manifest) -> Manifest:
		"""
		Переопределите данный метод для редактирования стандартного манифеста.

		После завершения редактирования сохранение происходит автоматически.

		:param manifest: Редактируемый манифест.
		:type manifest: Manifest
		:return: Отредактированный манифест.
		:rtype: Manifest
		"""

		return manifest

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, directory: "Path", table_type: str):
		"""
		Генератор манифеста.

		:param directory: Полный путь к директории таблицы.
		:type directory: Path
		:param table_type: Тип таблицы.
		:type table_type: str
		"""

		self.__directory: "Path" = directory
		self.__table_type: str = table_type

	def generate(self) -> Manifest:
		"""
		Генерирует пустой манифест.

		:return: Манифест.
		:rtype: Manifest
		"""
		
		manifest = Manifest(self.__directory, self.__table_type)
		manifest = self._edit_manifest(manifest)
		manifest.save()

		return manifest
