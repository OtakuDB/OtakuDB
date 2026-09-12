import importlib
from pathlib import Path
from typing import TYPE_CHECKING

from ...core.base.manifest import Manifest

if TYPE_CHECKING:
	from ..base.table import BaseTable
	from .box import Box, RootBox
	from .driver import Driver

class TableDescriptor:
	"""Дескриптор таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def full_path(self) -> Path:
		"""Полный путь к таблице."""

		return self.__full_path

	@property
	def manifest(self) -> Manifest:
		"""Манифест таблицы."""

		return self.__manifest
	
	@property
	def name(self) -> str:
		"""Имя таблицы."""

		return self.__name

	@property
	def virtual_path(self) -> Path:
		"""Вирутальный путь к таблице."""

		return self.__virtual_path

	@property
	def table(self) -> "BaseTable":
		"""Таблица."""

		return self.__table
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ititialize_table(self):
		"""Иницилазирует таблицу.."""

		module_path: str = f"otakudb.tables.{self.__manifest.type}.table"
		table_module = importlib.import_module(module_path)
		self.__table = table_module.Table(self.__driver, self)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", box: "Box | RootBox", name: str, manifest: Manifest | None = None):
		"""
		Дескриптор таблицы.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param box: Контейнер, которому принадлежит таблица.
		:type box: Box | RootBox
		:param name: Имя таблицы.
		:type name: str
		:param manifest: Манифест таблицы. При отсутствии загружается автоматически.
		:type manifest: Manifest | None
		:raises FileNotFoundError: Директория таблицы не найдена.
		"""

		self.__driver: "Driver" = driver
		self.__box: "Box | RootBox" = box
		self.__name: str = name
		
		self.__virtual_path: Path = self.__box.virtual_path / self.__name
		self.__full_path = self.__driver.storage_path / self.__virtual_path

		if not self.__full_path.exists():
			raise FileNotFoundError(self.__full_path)

		self.__manifest = manifest or Manifest(self.__full_path).load()

		self.__ititialize_table()
	
	def rename(self, name: str):
		"""
		Изменяет пути под новое название таблицы.

		:param name: Новое название таблицы.
		:type name: str
		"""

		self.__box.pop_item(self.__name)
		self.__virtual_path = self.__virtual_path.parent / name
		self.__full_path = self.__driver.storage_path / self.__virtual_path
		self.__box.add_item(self)
		self.__manifest.set_directory(self.full_path)
