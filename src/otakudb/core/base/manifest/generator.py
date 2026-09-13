from abc import ABC, abstractmethod
from pathlib import Path

from . import Manifest

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

	def __init__(self, directory: Path, table_type: str):
		"""
		Генератор манифеста.

		:param directory: Полный путь к директории таблицы.
		:type directory: Path
		:param table_type: Тип таблицы.
		:type table_type: str
		"""

		self.__Directory = directory
		self.__Type = table_type

	def generate(self) -> Manifest:
		"""
		Генерирует пустой манифест.

		:return: Манифест.
		:rtype: Manifest
		"""
		
		ManifestObject = Manifest(self.__Directory)
		ManifestObject.set_type(self.__Type)
		ManifestObject = self._edit_manifest(ManifestObject)
		ManifestObject.save()

		return ManifestObject
