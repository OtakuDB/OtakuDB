from .TableDescriptor import TableDescriptor
from .Box import Box, RootBox

from Source.Core import Exceptions

from dublib.Methods.Filesystem import ListDir

from typing import TYPE_CHECKING
from pathlib import Path
import functools
import importlib
import shutil
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
	# >>>>> ДЕКОРАТОРЫ <<<<< #
	#==========================================================================================#

	def require_storage(function):
		"""
		Декоратор. Проверяет, примонтировано ли хранилище, перед выполнением метода.

		:param function: Метод объекта.
		:type function: Callable
		:return: Обёрнутая функция.
		:rtype: Callable
		:raises Exceptions.Driver.StorageUnmounted: Хранилище отмонтировано.
		"""

		@functools.wraps(function)
		def Wrapper(self: "Driver", *args, **kwargs):
			if not self.__StorageDirectory: raise Exceptions.Driver.StorageUnmounted()
			return function(self, *args, **kwargs)
		
		return Wrapper

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

	@require_storage
	def create_box(self, parent_box: Box, name: str) -> Box:
		"""
		Создаёт новый контейнер.

		:param parent_box: Родительский контейнер.
		:type parent_box: Box
		:param name: Имя контейнера.
		:type name: str
		:return: Новый контейнер.
		:rtype: Box
		:raises ItemAlreadyExists: Элемент с таким именем уже существует.
		"""

		NewBoxFullPath = parent_box.full_path / name
		if NewBoxFullPath.exists(): raise Exceptions.Driver.ItemAlreadyExists(NewBoxFullPath)
		else: os.makedirs(NewBoxFullPath)

		NewBox = self.init_box(parent_box, name)
		parent_box.add_item(NewBox)

		return NewBox

	@require_storage
	def delete_box(self, parent_box: Box, name: str, purge: bool = False):
		"""
		Удаляет контейнер.

		:param parent_box: Родительский контейнер.
		:type parent_box: Box
		:param name: Имя контейнера.
		:type name: str
		:param purge: Указывает, нужно ли удалить содержимое контейнера, если он не пуст.
		:type purge: bool
		:raises BoxNotEmpty: Контейнер не пуст.
		:raises ItemNotFound: Элемент не найден.
		"""

		TargetBoxVirtualPath = parent_box.virtual_path / name
		TargetBox = self.get_box(TargetBoxVirtualPath)
		parent_box.pop_item(name)

		if purge: shutil.rmtree(TargetBox.full_path)
		else: 
			if TargetBox.items: raise Exceptions.Driver.BoxNotEmpty(TargetBox.virtual_path)
			else: TargetBox.full_path.rmdir()

	@require_storage
	def get_box(self, virtual_path: Path) -> Box:
		"""
		Возвращает инициализированный контейнер.

		:param virtual_path: Вирутальный путь к контейнеру.
		:type virtual_path: Path
		:return: Контейнер.
		:rtype: Box
		:raises ItemNotFound: Элемент не найден.
		"""

		try: return self.__Boxes[virtual_path.as_posix()]
		except KeyError: raise Exceptions.Driver.ItemNotFound(virtual_path)

	@require_storage
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

	@require_storage
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
	
	@require_storage
	def is_box_initialized(self, virtual_path: Path) -> bool:
		"""
		Проверяет, инициализирован ли контейнер.

		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		:return: Возвращает `True`, если контейнер инициализирован.
		:rtype: bool
		"""

		return virtual_path.as_posix() in self.__Boxes

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ РАБОТЫ С ТАБЛИЦАМИ <<<<< #
	#==========================================================================================#

	@require_storage
	def create_table(self, box: Box, name: str, type: str) -> TableDescriptor:
		"""
		Создаёт новую таблицу.

		:param box: Контейнер.
		:type box: Box
		:param name: Название таблицы.
		:type name: str
		:param type: Тип таблицы.
		:type type: str
		:return: Дескриптор таблицы.
		:rtype: TableDescriptor
		:raises ItemAlreadyExists: Элемент с таким именем уже существует.
		:raises IncorrectTableType: Несуществующий тип таблицы.
		"""

		if type not in self.tables_types: raise Exceptions.Driver.IncorrectTableType(type)

		TableVirtualPath = box.virtual_path / name
		TableFullPath = self.__StorageDirectory / TableVirtualPath

		if TableFullPath.exists(): raise Exceptions.Driver.ItemAlreadyExists(TableVirtualPath)
		else: os.makedirs(TableFullPath)

		ManifestGeneratorModule = importlib.import_module(f"Source.Tables.{type}.manifest")
		ManifestGenerator: "ManifestGenerator" = ManifestGeneratorModule.Generator(TableFullPath, type)
		Manifest = ManifestGenerator.generate()

		Descriptor = TableDescriptor(self, box, name, Manifest)
		box.add_item(Descriptor) 

		return Descriptor
	
	@require_storage
	def delete_table(self, box: Box, name: str):
		"""
		Удаляет таблицу.

		:param box: Контейнер.
		:type box: Box
		:param name: Название таблицы.
		:type name: str
		:raises ItemNotFound: Элемент не найден.
		"""

		Descriptor = box.pop_item(name)
		shutil.rmtree(Descriptor.full_path)