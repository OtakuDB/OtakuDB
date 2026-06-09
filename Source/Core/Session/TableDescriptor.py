from Source.Core.Base.Manifest import Manifest

from typing import TYPE_CHECKING
from pathlib import Path
import importlib

if TYPE_CHECKING:
	from Source.Core.Base.Table import BaseTable
	from Source.Core.Session.Box import Box 
	from .Driver import Driver

class TableDescriptor:
	"""Дескриптор таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def full_path(self) -> Path:
		"""Полный путь к таблице."""

		return self.__FullPath

	@property
	def manifest(self) -> Manifest:
		"""Манифест таблицы."""

		return self.__Manifest
	
	@property
	def name(self) -> str:
		"""Имя таблицы."""

		return self.__Name

	@property
	def virtual_path(self) -> Path:
		"""Вирутальный путь к таблице."""

		return self.__VirtualPath

	@property
	def table(self) -> "BaseTable":
		"""Таблица."""

		return self.__TableObject
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __InintializeTable(self):
		"""Иницилазирует таблицу.."""

		ImportPath = f"Source.Tables.{self.__Manifest.type}.table"
		TableModule = importlib.import_module(ImportPath)
		self.__TableObject = TableModule.Table(self.__Driver, self)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", box: "Box", name: str, manifest: Manifest | None = None):
		"""
		Дескриптор таблицы.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param box: Контейнер, которому принадлежит таблица.
		:type box: Box
		:param name: Имя таблицы.
		:type name: str
		:param manifest: Манифест таблицы. При отсутствии загружается автоматически.
		:type manifest: Manifest | None
		:raises FileNotFoundError: Директория таблицы не найдена.
		"""

		self.__Driver = driver
		self.__Box = box
		self.__Name = name

		self.__VirtualPath = box.virtual_path / self.__Name
		self.__FullPath = self.__Driver.storage_directory / self.__VirtualPath

		if not self.__FullPath.exists(): raise FileNotFoundError(self.__FullPath)

		self.__Manifest = manifest or Manifest(self.__FullPath).load()

		self.__InintializeTable()
	
	def rename(self, name: str):
		"""
		Изменяет пути под новое название таблицы.

		:param name: Новое название таблицы.
		:type name: str
		"""

		self.__Box.pop_item(self.__Name)
		self.__VirtualPath = self.__VirtualPath.parent / name
		self.__FullPath = self.__Driver.storage_directory / self.__VirtualPath
		self.__Box.add_item(self, name)