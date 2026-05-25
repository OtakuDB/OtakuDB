from .TableDescriptor import TableDescriptor
from .Box import Box

from Source.Core import Exceptions

from dublib.Methods.Filesystem import ListDir

from typing import TYPE_CHECKING
from pathlib import Path
from os import PathLike
import importlib
import os

if TYPE_CHECKING:
	from Source.Core.Base.Manifest.Generator import ManifestGenerator

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Driver:
	"""Драйвер хранилища."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def storage_directory(self) -> Path | None:
		"""Директория хранилища."""

		return self.__StorageDirectory

	@property
	def tables_types(self) -> tuple[str]:
		"""Последовательность названий доступных типов таблиц."""

		Types = ListDir("Source/Tables")
		if "__pycache__" in Types: Types.remove("__pycache__")

		return tuple(Types)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Драйвер хранилища."""
		
		self.__StorageDirectory = None

	def is_box(self, virtual_path: Path) -> bool:
		"""
		Проверяет, представляет ли директория по вирутальному пути контейнер.

		:param virtual_path: Виртуальный путь к директории.
		:type virtual_path: Path
		:return: Возвращает `True`, если директория является контейнером.
		:rtype: bool
		"""

		TotalPath = self.__StorageDirectory / virtual_path / "manifest.json"

		return not TotalPath.exists()

	def mount(self, directory: PathLike):
		"""
		Монтирует указанную директорию как хранилище.

		:param directory: Директория хранилища.
		:type directory: PathLike
		:raises FileNotFoundError: Выбрасывается при отсутствии монтируемой директории.
		"""

		if not os.path.exists(directory): raise FileNotFoundError(directory)
		self.__StorageDirectory = Path(directory)

	def create_box(self, parent_box: Box | None, name: str) -> Box:
		"""
		Создаёт новый контейнер.

		:param parent_box: Путь к родительскому контейнеру.
		:type parent_box: Box | None
		:param name: Название контейнера.
		:type name: str
		:return: Новый контейнер.
		:rtype: Box
		:raises StorageUnmounted: Хранилище отмонтировано.
		"""

		if not self.__StorageDirectory: raise Exceptions.Driver.StorageUnmounted()

		TotalPath = self.__StorageDirectory / parent_box.path / name
		os.makedirs(TotalPath, exist_ok = True)

		return Box(self, parent_box.path, name)

	def create_table(self, type: str, name: str, parent_box: Box) -> TableDescriptor:
		"""
		Создаёт новую таблицу.

		:param type: Тип таблицы.
		:type type: str
		:param name: Название таблицы.
		:type name: str
		:param parent_box: Родительский контейнер.
		:type parent_box: Box
		:return: Дескриптор таблицы.
		:rtype: TableDescriptor
		:raises StorageUnmounted: Хранилище отмонтировано.
		:raises TableAlreadyExists: Таблица уже существует.
		"""

		if not self.__StorageDirectory: raise Exceptions.Driver.StorageUnmounted()

		TableVirtualPath = parent_box.path / name
		TableTotalPath = self.__StorageDirectory / TableVirtualPath

		if TableTotalPath.exists(): raise Exceptions.Driver.TableAlreadyExists(TableVirtualPath)

		os.makedirs(TableTotalPath, exist_ok = True)

		ManifestGeneratorModule = importlib.import_module(f"Source.Tables.{type}.manifest")
		ManifestGenerator: "ManifestGenerator" = ManifestGeneratorModule.Generator(TableTotalPath, type)
		Manifest = ManifestGenerator.generate()

		parent_box.reload()

		return TableDescriptor(self, parent_box, TableVirtualPath, Manifest)
	
	def get_box(self, virtual_path: Path | None = None) -> Box:
		"""
		Вовзаращает контейнер по вирутальному пути.

		:param virtual_path: Виртуальный путь к контейнеру. При отсутствии будет возвращён корневой контейнер.
		:type virtual_path: Path | None
		:return: Контейнер.
		:rtype: Box
		:raises FileNotFoundError: Вирутальный путь не найден.
		"""

		virtual_path = virtual_path or Path()

		TotalPath = self.__StorageDirectory / virtual_path
		if not TotalPath.exists(): raise FileNotFoundError(TotalPath)

		if virtual_path and str(virtual_path) != ".": return Box(self, virtual_path.parent, virtual_path.name)
		else: return Box(self)