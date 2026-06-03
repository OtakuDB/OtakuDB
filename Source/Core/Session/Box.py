from .TableDescriptor import TableDescriptor

from Source.Core import Exceptions

from typing import TYPE_CHECKING
from pathlib import Path
import os

if TYPE_CHECKING:
	from .Driver import Driver

class RootBox:
	"""Корневой контейнер."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def full_path(self) -> Path:
		"""Полный путь к контейнеру."""

		return self._Driver.storage_directory / self.virtual_path

	@property
	def items(self) -> "tuple[Box | TableDescriptor]":
		"""Последовательность содержащихся в контейнере элементов."""

		return tuple(self._Items.values())
	
	@property
	def virtual_path(self) -> Path:
		"""Виртуальный путь к контейнеру."""

		return self._VirtualPath
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _BaseInit(self, driver: "Driver", virtual_path: Path):
		"""
		Базовый метод инициализации контейнера.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		"""

		self._Driver = driver
		self._VirtualPath = virtual_path
		self._FullPath = self._Driver.storage_directory / self._VirtualPath

		self._Items: dict[str, Box | TableDescriptor] = dict()

		self.reload()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver"):
		"""
		Корневой контейнер.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		"""

		self._BaseInit(driver, Path())

	def add_item(self, item: "Box | TableDescriptor"):
		"""
		Добавляет новый элемент в контейнер.

		:param item: Новый элемент.
		:type item: Box | TableDescriptor
		"""

		if item.name in self._Items: raise Exceptions.Driver.BoxItemOverride(item.virtual_path)
		self._Items[item.name] = item

	def create_box(self, name: str) -> "Box":
		"""
		Создаёт контейнер внутри текущего.

		:param name: Имя контейнера.
		:type name: str
		:return: Новый контейнер.
		:rtype: Box
		:raises ItemAlreadyExists: Элемент с таким именем уже существует.
		"""

		return self._Driver.create_box(self, name)

	def create_table(self, name: str, type: str) -> "TableDescriptor":
		"""
		Создаёт таблицу внутри текущего контейнера.

		:param name: Имя таблицы.
		:type name: str
		:param type: Тип таблицы.
		:type type: str
		:return: Дескриптор таблицы.
		:rtype: TableDescriptor
		:raises ItemAlreadyExists: Элемент с таким именем уже существует.
		:raises IncorrectTableType: Несуществующий тип таблицы.
		"""

		return self._Driver.create_table(self, name, type)

	def delete_table(self, name: str):
		"""
		Удаляет таблицу.

		:param name: Имя таблицы.
		:type name: str
		:raises ItemNotFound: Элемент не найден.
		"""

		self._Driver.delete_table(self, name)

	def get_item(self, name: str) -> "Box | TableDescriptor":
		"""
		Возвращает элемент по имени.

		:param name: Имя элемента.
		:type name: str
		:return: Элемент.
		:rtype: Box | TableDescriptor
		:raises KeyError: Элемент не найден.
		"""

		return self._Items[name]

	def pop_item(self, name: str) -> "Box | TableDescriptor":
		"""
		Извлекает элемент из контейнера.

		:param name: Имя элемента.
		:type name: str
		:return: Элемент.
		:rtype: Box | TableDescriptor
		:raises ItemNotFound: Элемент не найден.
		"""

		if name not in self._Items: raise Exceptions.Driver.ItemNotFound(self._VirtualPath / name)
		Item = self.get_item(name)
		del self._Items[name]

		return Item

	def reload(self):
		"""Сканирует и обновляет элементы контейнера."""

		Elements = tuple(Value.name for Value in os.scandir(self.full_path) if Value.is_dir())
		Items = dict()

		for Element in Elements:
			ElementVirtualPath = self.virtual_path / Element

			if self._Driver.is_box(ElementVirtualPath):
				if not self._Driver.is_box_initialized(ElementVirtualPath): self._Driver.init_box(self, Element)
				Items[Element] = self._Driver.get_box(ElementVirtualPath)

			else: Items[Element] = TableDescriptor(self._Driver, self, Element)

		self._Items = Items

class Box(RootBox):
	"""Контейнер."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def name(self) -> str:
		"""Имя контейнера."""

		return self.__Name

	@property
	def parent(self) -> "Box | RootBox":
		"""Родительский контейнер."""

		return self.__ParentBox

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

		self._BaseInit(driver, parent_box.virtual_path / name)

		self.__ParentBox = parent_box
		self.__Name = name

	def delete(self, purge: bool = False):
		"""
		Удаляет контейнер и всё его содержимое.
		
		:param purge: Указывает, нужно ли удалить содержимое контейнера, если он не пуст.
		:type purge: bool
		:raises BoxNotEmpty: Контейнер не пуст.
		:raises ItemNotFound: Элемент не найден.
		"""

		self._Driver.delete_box(self.__ParentBox, self.__Name, purge)
