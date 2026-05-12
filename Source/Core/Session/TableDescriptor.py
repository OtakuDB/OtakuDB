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
	def manifest(self) -> Manifest:
		"""Манифест таблицы."""

		return self.__Manifest
	
	@property
	def name(self) -> str:
		"""Имя таблицы."""

		return self.__VirtualPath.name

	@property
	def path(self) -> Path:
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

	def __init__(self, driver: "Driver", box: "Box", virtual_path: Path, manifest: Manifest | None = None):
		"""
		Дескриптор таблицы.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param box: Контейнер, которому принадлежит таблица.
		:type box: Box
		:param virtual_path: Виртуальный путь к таблице.
		:type virtual_path: Path
		:param manifest: Манифест таблицы. При отсутствии загружается автоматически.
		:type manifest: Manifest | None
		:raises FileNotFoundError: Выбрасывается при отсутствии директории таблицы.
		"""

		self.__Driver = driver
		self.__Box = box
		self.__VirtualPath = virtual_path

		self.__TotalPath = self.__Driver.storage_directory / self.__VirtualPath
		if not self.__TotalPath.exists(): raise FileNotFoundError(self.__TotalPath)

		self.__Manifest = manifest or Manifest(self.__TotalPath).load()

		self.__TableObject: "BaseTable | None" = None
		self.__InintializeTable()

	def __repr__(self) -> str:
		"""Возвращает техническое представление объекта."""

		return f"<Table::{self.name}>"
	
	def rename(self, name: str):
		"""
		Изменяет пути под новое название таблицы.

		:param name: Новое название таблицы.
		:type name: str
		"""

		self.__VirtualPath = self.__VirtualPath.parent / name
		self.__TotalPath = self.__Driver.storage_directory / self.__VirtualPath
		self.__Box.reload()