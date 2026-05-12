from . import Manifest

from pathlib import Path

class ManifestGenerator:
	"""Генератор манифеста."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _EditManifest(self, manifest: Manifest) -> Manifest:
		"""
		Переопределите данный метод для редактирования стандартного манифеста.

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

		return self._EditManifest(ManifestObject)
