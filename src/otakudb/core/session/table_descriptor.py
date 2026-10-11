import importlib
from pathlib import Path
from typing import TYPE_CHECKING, cast

from ...core.base.manifest import BaseManifest

if TYPE_CHECKING:
	from ..base.note import BaseNote
	from ..base.table import BaseTable
	from .box import Box, RootBox
	from .driver import Driver

class TableDescriptor[N: "BaseNote", M: "BaseManifest"]:
	"""Дескриптор таблицы."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def full_path(self) -> Path:
		"""Полный путь к таблице."""

		return self.__full_path

	@property
	def manifest(self) -> M:
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
	def table(self) -> "BaseTable[N, M]":
		"""Таблица."""

		return self.__table

	#==========================================================================================#
	# >>>>> PRIBATE METHODS <<<<< #
	#==========================================================================================#

	def __ititialize_table(self):
		"""Иницилазирует таблицу.."""

		module_path: str = f"otakudb.tables.{self.__manifest.table_type}.table"
		table_module = importlib.import_module(module_path)
		self.__table = table_module.Table(self.__driver, self)

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", box: "Box | RootBox", name: str, manifest: M | None = None):
		"""
		Дескриптор таблицы.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param box: Контейнер, которому принадлежит таблица.
		:type box: Box | RootBox
		:param name: Имя таблицы.
		:type name: str
		:param manifest: Манифест таблицы. При отсутствии загружается автоматически.
		:type manifest: BaseManifest | None
		:raises FileNotFoundError: Директория таблицы не найдена.
		"""

		self.__driver: "Driver" = driver
		self.__box: "Box | RootBox" = box
		self.__name: str = name

		self.__virtual_path: Path = self.__box.virtual_path / self.__name
		self.__full_path = self.__driver.storage_path / self.__virtual_path

		if not self.__full_path.exists():
			raise FileNotFoundError(self.__full_path)

		self.__manifest: M = manifest or cast(M, self.__driver.load_manifest(self.__full_path))

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
		self.__manifest.change_directory(self.full_path)
