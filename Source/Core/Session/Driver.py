from .TableDescriptor import TableDescriptor
from .Box import Box, RootBox

from Source.Core import Exceptions

from dublib.Methods.Filesystem import ListDir

from typing import TYPE_CHECKING
from pathlib import Path
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
	def root_box(self) -> RootBox | None:
		"""Корневой контейнер."""

		return self.__Boxes.get(".")

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
		
		self.__StorageDirectory: Path | None = None
		self.__Boxes: dict[str, Box] = dict()

	def mount(self, directory: Path):
		"""
		Монтирует директорию как хранилище.

		:param directory: Директория хранилища или `None` для отключения.
		:type directory: Path | None
		:raises FileNotFoundError: Директория хранилища не найдена.
		"""
		
		if directory.exists():
			self.__StorageDirectory = directory
			self.__Boxes["."] = RootBox(self)
		else: raise FileNotFoundError(directory)

	def unmount(self):
		"""Отмонтирует хранилище."""

		self.__StorageDirectory = None
		self.__RootBox = None

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ РАБОТЫ С КОНТЕЙНЕРАМИ <<<<< #
	#==========================================================================================#

	def create_box(self, parent_box: Box, name: str) -> Box:
		"""
		Создаёт новый контейнер.

		:param parent_box: Путь к родительскому контейнеру.
		:type parent_box: Box
		:param name: Название контейнера.
		:type name: str
		:return: Новый контейнер.
		:rtype: Box
		:raises StorageUnmounted: Хранилище отмонтировано.
		"""

		if not self.__StorageDirectory: raise Exceptions.Driver.StorageUnmounted()

		NewBoxFullPath = parent_box.full_path / name
		os.makedirs(NewBoxFullPath, exist_ok = True)
		NewBox = self.init_box(parent_box, name)
		parent_box.add_item(NewBox)

		return NewBox

	def get_box(self, virtual_path: Path) -> Box:
		"""
		Возвращает инициализированный контейнер.

		:param virtual_path: Вирутальный путь к контейнеру.
		:type virtual_path: Path
		:param auto_init: Переключает автоматическую инициализацию контейнера.
		:type auto_init: bool
		:return: Контейнер.
		:rtype: Box
		:raises BoxNotFound: Контейнер не найден.
		"""

		try: return self.__Boxes[virtual_path.as_posix()]
		except KeyError: raise Exceptions.Driver.BoxNotFound(virtual_path)

	def init_box(self, parent_box: Box | RootBox, name: str) -> Box:
		"""
		Инициализирует существующий контейнер.

		:param parent_box: Родительский контейнер.
		:type parent_box: Box | RootBox
		:param name: Имя контейнера.
		:type name: str
		:return: Контейнер.
		:rtype: Box
		"""

		VirtualPath = parent_box.virtual_path / name
		self.__Boxes[VirtualPath.as_posix()] = Box(self, parent_box, name)

		return self.get_box(VirtualPath)

	def is_box(self, virtual_path: Path) -> bool:
		"""
		Проверяет, представляет ли директория по вирутальному пути контейнер.

		:param virtual_path: Виртуальный путь к директории.
		:type virtual_path: Path
		:return: Возвращает `True`, если директория является контейнером.
		:rtype: bool
		"""

		FullManifestPath = self.__StorageDirectory / virtual_path / "manifest.json"

		return not FullManifestPath.exists()
	
	def is_box_initialized(self, virtual_path: Path) -> bool:
		"""
		Проверяет, инициализирован ли контейнер.

		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		:return: Возвращает `True`, если контейнер инициализирован.
		:rtype: bool
		"""

		return virtual_path.as_posix() in self.__Boxes









	

	

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

		TableVirtualPath = parent_box.virtual_path / name
		TableFullPath = self.__StorageDirectory / TableVirtualPath

		if TableFullPath.exists(): raise Exceptions.Driver.TableAlreadyExists(TableVirtualPath)

		os.makedirs(TableFullPath, exist_ok = True)

		ManifestGeneratorModule = importlib.import_module(f"Source.Tables.{type}.manifest")
		ManifestGenerator: "ManifestGenerator" = ManifestGeneratorModule.Generator(TableFullPath, type)
		Manifest = ManifestGenerator.generate()

		parent_box.reload()

		return TableDescriptor(self, parent_box, name, Manifest)