import importlib
import pkgutil
import shutil
from pathlib import Path

from ... import tables
from .. import exceptions
from .box import Box, RootBox
from .table_descriptor import TableDescriptor

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Driver:
	"""Драйвер хранилища."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
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
		"""Последовательность названий доступных типов таблиц."""

		return tuple(info.name for info in pkgutil.iter_modules(tables.__path__))

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __free_box(self, virtual_path: Path):
		"""
		Выгружает контейнер.

		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		:raises BoxAlreadyInitializedError: Контейнер не инициализирован.
		"""

		box_virtual_path: str = virtual_path.as_posix()

		if not self.is_box_initialized(virtual_path):
			raise exceptions.session.box.BoxNotInitializedError(virtual_path)

		del self.__boxes[box_virtual_path]

	def __init_box(self, parent_box: Box | RootBox, name: str) -> Box:
		"""
		Инициализирует существующий контейнер.

		:param parent_box: Родительский контейнер.
		:type parent_box: Box | RootBox
		:param name: Имя контейнера.
		:type name: str
		:return: Контейнер.
		:rtype: Box
		:raises BoxAlreadyInitializedError: Контейнер уже инициализирован.
		"""

		virtual_path: Path = parent_box.virtual_path / name
		box_virtual_path: str = virtual_path.as_posix()

		if self.is_box_initialized(virtual_path):
			raise exceptions.session.box.BoxAlreadyInitializedError(virtual_path)

		box = Box(self, parent_box, name)
		self.__boxes[box_virtual_path] = box

		return box

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, storage_path: Path):
		"""
		Драйвер хранилища.
		
		:param storage_path: Путь к директории хранилища.
		:type storage_path: Path
		"""
		
		self.__storage_path: Path = storage_path

		self.__root_box: RootBox = RootBox(self)
		self.__boxes: dict[str, Box] = {}
		
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ РАБОТЫ С КОНТЕЙНЕРАМИ <<<<< #
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

		new_box = self.__init_box(parent_box, name)
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
		self.__free_box(target_box_virtual_path)

		if purge:
			shutil.rmtree(target_box.full_path)

		else: 
			if target_box.items:
				raise exceptions.session.box.BoxNotEmptyError(target_box_virtual_path)
			else:
				target_box.full_path.rmdir()

	def get_box(self, virtual_path: Path, auto_init: bool = False) -> Box:
		"""
		Возвращает инициализированный контейнер.

		:param virtual_path: Вирутальный путь к контейнеру.
		:type virtual_path: Path
		:param auto_init: Указывает, следует ли инициализировать контейнер, если он существует.
		:type auto_init: bool
		:return: Контейнер.
		:rtype: Box
		:raises BoxNotInitializedError: Контейнер не инициализирован.
		:raises ItemNotFoundError: Контейнер не найден.
		"""

		if not self.is_item_exists(virtual_path):
			raise exceptions.session.driver.ItemNotFoundError(virtual_path)

		if self.is_box_initialized(virtual_path):
			return self.__boxes[virtual_path.as_posix()] 

		if auto_init:
			parent_box = self.get_box(virtual_path.parent) if len(virtual_path.parts) > 1 else self.__root_box
			self.__init_box(parent_box, virtual_path.name)
			return self.__boxes[virtual_path.as_posix()] 

		raise exceptions.session.box.BoxNotInitializedError(virtual_path)

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
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ РАБОТЫ С ТАБЛИЦАМИ <<<<< #
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

		# To-Do: использовать новую модель манифеста.
		manifest_generator_module = importlib.import_module(f"otakudb.tables.{table_type}.manifest")
		manifest_generator = manifest_generator_module.Generator(table_full_path, table_type)
		manifest = manifest_generator.generate()

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
