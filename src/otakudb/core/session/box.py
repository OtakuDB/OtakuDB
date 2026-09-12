import os
from pathlib import Path
from typing import TYPE_CHECKING

from .. import exceptions
from .table_descriptor import TableDescriptor

if TYPE_CHECKING:
	from .driver import Driver

class RootBox:
	"""Корневой контейнер."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def full_path(self) -> Path:
		"""Полный путь к контейнеру."""

		return self._full_path

	@property
	def items(self) -> "tuple[Box | TableDescriptor, ...]":
		"""Последовательность содержащихся в контейнере элементов."""

		return tuple(self._items.values())
	
	@property
	def virtual_path(self) -> Path:
		"""Виртуальный путь к контейнеру."""

		return self._virtual_path
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _base_init(self, driver: "Driver", virtual_path: Path):
		"""
		Базовый метод инициализации контейнера.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		:raises FileNotFoundError: Директория контейнера не найдена.
		"""

		self._driver: "Driver" = driver
		self._virtual_path: Path = virtual_path
		self._full_path: Path = self._driver.storage_path / self._virtual_path
		
		self._items: dict[str, Box | TableDescriptor] = {}

		self.reload()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver"):
		"""
		Корневой контейнер.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:raises FileNotFoundError: Директория контейнера не найдена.
		"""

		self._base_init(driver, Path())

	def add_item(self, item: "Box | TableDescriptor"):
		"""
		Добавляет элемент в контейнер.

		:param item: Элемент.
		:type item: Box | TableDescriptor
		:raises BoxItemOverrideError: Перезапись элемента контейнера.
		"""

		if item.name in self._items:
			raise exceptions.session.box.BoxItemOverrideError(item.virtual_path)

		self._items[item.name] = item

	def create_box(self, name: str) -> "Box":
		"""
		Создаёт контейнер внутри текущего.

		:param name: Имя контейнера.
		:type name: str
		:return: Новый контейнер.
		:rtype: Box
		"""

		return self._driver.create_box(self, name)

	def create_table(self, name: str, table_type: str) -> "TableDescriptor":
		"""
		Создаёт таблицу внутри текущего контейнера.

		:param name: Имя таблицы.
		:type name: str
		:param table_type: Тип таблицы.
		:type table_type: str
		:return: Дескриптор таблицы.
		:rtype: TableDescriptor
		"""

		return self._driver.create_table(self, name, table_type)

	def delete_table(self, name: str):
		"""
		Удаляет таблицу.

		:param name: Имя таблицы.
		:type name: str
		:raises ItemNotFound: Элемент не найден.
		"""

		self._driver.delete_table(self, name)

	def get_item(self, name: str) -> "Box | TableDescriptor":
		"""
		Возвращает элемент по имени.

		:param name: Имя элемента.
		:type name: str
		:return: Элемент.
		:rtype: Box | TableDescriptor
		:raises ItemNotFoundError: Элемент не найден.
		"""

		if name not in self._items:
			virtual_path: Path = self._virtual_path / name
			raise exceptions.session.driver.ItemNotFoundError(virtual_path)

		return self._items[name]

	def pop_item(self, name: str) -> "Box | TableDescriptor":
		"""
		Извлекает элемент из контейнера.

		:param name: Имя элемента.
		:type name: str
		:return: Элемент.
		:rtype: Box | TableDescriptor
		:raises ItemNotFoundError: Элемент не найден.
		"""

		if name not in self._items:
			virtual_path: Path = self._virtual_path / name
			raise exceptions.session.driver.ItemNotFoundError(virtual_path)

		return self._items.pop(name)

	def reload(self):
		"""Сканирует директорию контейнера и заново получает вложенные элементы."""

		elements_names: tuple[str, ...] = tuple(Value.name for Value in os.scandir(self.full_path) if Value.is_dir())
		items: dict[str, "Box | TableDescriptor"] = {}

		for name in elements_names:
			element_virtual_path = self._virtual_path / name

			if self._driver.is_box(element_virtual_path):
				items[name] = self._driver.get_box(element_virtual_path, auto_init = True)
			else:
				items[name] = TableDescriptor(self._driver, self, name)

		self._items = items

class Box(RootBox):
	"""Контейнер."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def name(self) -> str:
		"""Имя контейнера."""

		return self.__name

	@property
	def parent(self) -> "Box | RootBox":
		"""Родительский контейнер."""

		return self.__parent_box

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", parent_box: "Box | RootBox", name: str):
		"""
		Контейнер.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param parent_box: Родительский контейнер.
		:type parent_box: Box | RootBox
		:param name: Имя контейнера.
		:type name: str
		"""

		self._base_init(driver, parent_box.virtual_path / name)

		self.__parent_box: "Box | RootBox" = parent_box
		self.__name: str = name

	def delete(self, purge: bool = False):
		"""
		Удаляет контейнер и всё его содержимое.
		
		:param purge: Указывает, нужно ли удалить содержимое контейнера, если он не пуст.
		:type purge: bool
		"""

		self._driver.delete_box(self.__parent_box, self.__name, purge)
