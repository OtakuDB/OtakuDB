import importlib
import pkgutil
import shutil
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

from dublib.functions.filesystem import json

from ... import tables
from .. import exceptions
from .box import Box, RootBox
from .table_descriptor import TableDescriptor

if TYPE_CHECKING:
	from ..base.manifest import BaseManifest

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Driver:
	"""Драйвер хранилища."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def root_box(self) -> RootBox:
		"""Корневой контейнер."""

		return self.__root_box

	@property
	def storage_path(self) -> Path:
		"""Путь к директории хранилища."""

		return self.__storage_path

	@property
	def available_tables_types(self) -> tuple[str, ...]:
		"""Available tables types."""

		return tuple(info.name for info in pkgutil.iter_modules(tables.__path__))

	#==========================================================================================#
	# >>>>> PRIVATE METHODS <<<<< #
	#==========================================================================================#

	def __initialize_manifest(self, directory: Path, table_type: str) -> "BaseManifest":
		"""
		Initialize manifest.

		:param directory: Full path to table directory.
		:type directory: Path
		:param table_type: Table type.
		:type table_type: str
		:return: Manifest.
		:rtype: BaseManifest
		"""

		module_path: str = f"otakudb.tables.{table_type}.manifest"

		module: ModuleType = importlib.import_module(module_path)
		Manifest: type[BaseManifest] = module.Manifest

		return Manifest(directory)

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, storage_path: Path):
		"""
		Драйвер хранилища.

		:param storage_path: Путь к директории хранилища.
		:type storage_path: Path
		"""

		self.__storage_path: Path = storage_path

		self.__boxes: dict[str, Box] = {}
		self.__root_box: RootBox = RootBox(self)

	#==========================================================================================#
	# >>>>> PUBLIC BOX INTERACTION METHODS <<<<< #
	#==========================================================================================#

	def create_box(self, parent_box: Box | RootBox, name: str) -> Box:
		"""
		Создаёт контейнер.

		:param parent_box: Родительский контейнер.
		:type parent_box: Box | RootBox
		:param name: Имя контейнера.
		:type name: str
		:return: Новый контейнер.
		:rtype: Box
		:raises ItemAlreadyExistsError: Элемент с таким именем уже существует.
		"""

		new_box_full_path: Path = parent_box.full_path / name

		if new_box_full_path.exists():
			raise exceptions.session.driver.ItemAlreadyExistsError(new_box_full_path)
		else:
			new_box_full_path.mkdir()

		new_box = self.init_box(parent_box, name)
		parent_box.add_item(new_box)

		return new_box

	def delete_box(self, parent_box: Box | RootBox, name: str, purge: bool = False):
		"""
		Удаляет контейнер.

		:param parent_box: Родительский контейнер.
		:type parent_box: Box | RootBox
		:param name: Имя контейнера.
		:type name: str
		:param purge: Указывает, нужно ли удалить содержимое контейнера, если он не пуст.
		:type purge: bool
		:raises BoxNotEmptyError: Контейнер не пуст.
		:raises ItemNotFoundError: Элемент не найден.
		"""

		target_box_virtual_path = parent_box.virtual_path / name
		target_box = self.get_box(target_box_virtual_path)
		parent_box.pop_item(name)
		self.free_box(target_box_virtual_path)

		if purge:
			shutil.rmtree(target_box.full_path)

		else:
			if target_box.items:
				raise exceptions.session.box.BoxNotEmptyError(target_box_virtual_path)
			else:
				target_box.full_path.rmdir()

	def free_box(self, virtual_path: Path):
		"""
		Unload box from memory.

		:param virtual_path: Virtual path to box.
		:type virtual_path: Path
		:raises BoxAlreadyInitializedError: Box not initialized.
		"""

		box_virtual_path: str = virtual_path.as_posix()

		if not self.is_box_initialized(virtual_path):
			raise exceptions.session.box.BoxNotInitializedError(virtual_path)

		del self.__boxes[box_virtual_path]

	def get_box(self, virtual_path: Path) -> Box:
		"""
		Return initialized box.

		:param virtual_path: Virtual path to box.
		:type virtual_path: Path
		:return: Box.
		:rtype: Box
		:raises BoxNotInitializedError: Box not initialized.
		:raises ItemNotFoundError: Box not found.
		"""

		if not self.is_item_exists(virtual_path):
			raise exceptions.session.driver.ItemNotFoundError(virtual_path)

		if self.is_box_initialized(virtual_path):
			return self.__boxes[virtual_path.as_posix()]

		raise exceptions.session.box.BoxNotInitializedError(virtual_path)

	def init_box(self, parent_box: Box | RootBox, name: str) -> Box:
		"""
		Initialize exists box.

		:param parent_box: Parent box.
		:type parent_box: Box | RootBox
		:param name: Box name.
		:type name: str
		:return: Initialized box.
		:rtype: Box
		:raises BoxAlreadyInitializedError: Box already initialized.
		"""

		virtual_path: Path = parent_box.virtual_path / name
		box_virtual_path: str = virtual_path.as_posix()

		if self.is_box_initialized(virtual_path):
			raise exceptions.session.box.BoxAlreadyInitializedError(virtual_path)

		box = Box(self, parent_box, name)
		self.__boxes[box_virtual_path] = box

		return box

	def is_box(self, virtual_path: Path) -> bool:
		"""
		Проверяет, ведёт ли вирутальный путь к контейнеру.

		:param virtual_path: Виртуальный путь.
		:type virtual_path: Path
		:return: Возвращает `True`, если директория является контейнером.
		:rtype: bool
		"""

		full_manifest_path: Path = self.__storage_path / virtual_path / "manifest.json"

		return not full_manifest_path.exists()

	def is_box_initialized(self, virtual_path: Path) -> bool:
		"""
		Проверяет, инициализирован ли контейнер.

		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		:return: Возвращает `True`, если контейнер инициализирован.
		:rtype: bool
		"""

		return virtual_path.as_posix() in self.__boxes

	def is_item_exists(self, virtual_path: Path) -> bool:
		"""
		Проверяет, существует ли элемент по указанному вирутальному пути.

		:param virtual_path: Виртуальный путь.
		:type virtual_path: Path
		:return: Возвращает `True`, если элемент существует.
		:rtype: bool
		"""

		full_path: Path = self.__storage_path / virtual_path

		return full_path.exists()

	#==========================================================================================#
	# >>>>> PUBLIC TABLES INTERACTIONS METHODS <<<<< #
	#==========================================================================================#

	def create_table(self, box: Box | RootBox, name: str, table_type: str) -> TableDescriptor:
		"""
		Создаёт таблицу.

		:param box: Контейнер.
		:type box: Box | RootBox
		:param name: Название таблицы.
		:type name: str
		:param table_type: Тип таблицы.
		:type table_type: str
		:return: Дескриптор таблицы.
		:rtype: TableDescriptor
		:raises ItemAlreadyExistsError: Элемент с таким именем уже существует.
		:raises TableTypeNotFoundError: Тип таблицы не найден.
		"""

		if table_type not in self.available_tables_types:
			raise exceptions.session.driver.TableTypeNotFoundError(table_type)

		table_virtual_path: Path = box.virtual_path / name
		table_full_path: Path = self.__storage_path / table_virtual_path

		if table_full_path.exists():
			raise exceptions.session.driver.ItemAlreadyExistsError(table_virtual_path)

		table_full_path.mkdir()

		manifest = self.__initialize_manifest(table_full_path, table_type)
		manifest.save()
		descriptor = TableDescriptor(self, box, name, manifest)
		box.add_item(descriptor)

		return descriptor

	def delete_table(self, box: Box | RootBox, name: str):
		"""
		Удаляет таблицу.

		:param box: Контейнер.
		:type box: Box | RootBox
		:param name: Название таблицы.
		:type name: str
		:raises ItemNotFoundError: Элемент не найден.
		"""

		descriptor = box.pop_item(name)
		shutil.rmtree(descriptor.full_path)

	def load_manifest(self, directory: Path) -> "BaseManifest":
		"""
		Load manifest.

		:param directory: Full path to table directory.
		:type directory: Path
		:param table_type: Table type.
		:type table_type: str
		:return: Manifest.
		:rtype: BaseManifest
		"""

		manifest_path: Path = directory / "manifest.json"
		manifest_data: dict = json.read(manifest_path)
		table_type: str = manifest_data["type"]

		manifest = self.__initialize_manifest(directory, table_type)
		manifest.parse(manifest_data)

		return manifest
