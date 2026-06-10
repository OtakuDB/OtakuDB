from . import Manifest

from abc import ABC, abstractmethod
from pathlib import Path

class ManifestGenerator(ABC):
	"""Генератор манифеста."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _EditManifest(self, manifest: Manifest) -> Manifest:
		"""
		Переопределите данный метод для редактирования стандартного манифеста.

		После завершения редактирования будет выполнено обязательное сохранение манифеста, поэтому для методов редактирования рекомендуется отключать сохранение.

		:param manifest: Редактируемый манифест.
		:type manifest: Manifest
		:return: Отредактированный манифест.
		:rtype: Manifest
		"""

		return manifest

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, directory: Path, type: str):
		"""
		Генератор манифеста.

		:param directory: Полный путь к директории таблицы.
		:type directory: Path
		:param type: Тип таблицы.
		:type type: str
		"""

		self.__Directory = directory
		self.__Type = type

	def generate(self) -> Manifest:
		"""
		Генерирует пустой манифест.

		:return: Манифест.
		:rtype: Manifest
		"""
		
		ManifestObject = Manifest(self.__Directory)
		ManifestObject.set_type(self.__Type)
		ManifestObject = self._EditManifest(ManifestObject)
		ManifestObject.save()

		return ManifestObject
