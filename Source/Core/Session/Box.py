from .TableDescriptor import TableDescriptor

from dublib.Methods.Filesystem import ListDir

from typing import TYPE_CHECKING
from pathlib import Path
import os

if TYPE_CHECKING:
	from .Driver import Driver

class Box:
	"""Контейнер."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def name(self) -> str:
		"""Имя представления."""

		return self.__VirtualPath.name
	
	@property
	def items(self) -> "tuple[Box | TableDescriptor]":
		"""Копия словаря элементов текущего представления."""

		return tuple(self.__Items.values())

	@property
	def parent(self) -> "Box | None":
		"""Родительский контейнер."""

		if not self.__ParentPath: return

		try: return self.__Driver.get_box(self.__ParentPath)
		except FileNotFoundError: pass

	@property
	def path(self) -> Path:
		"""Виртуальный путь к представлению."""

		return self.__VirtualPath

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", parent_path: Path | None = None, name: str | None = None):
		"""
		Контейнер.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param parent_path: Виртуальный путь к родительскому контейнеру.
		:type parent_path: Path | None
		:param name: Имя контейнера. Обязательно при наличии родительского контейнера.
		:type name: str | None
		:raises FileNotFoundError: Директория контейнера не найдена.
		:raises ValueError: Не назначено имя для вложенного контейнера.
		"""

		if parent_path and not name: raise ValueError("Box must have name.")
		
		self.__Driver = driver
		self.__ParentPath = parent_path
		self.__Name = name

		self.__VirtualPath = Path()
		if self.__ParentPath: self.__VirtualPath = self.__ParentPath / self.__Name
		self.__TotalPath = self.__Driver.storage_directory / self.__VirtualPath

		if not self.__TotalPath.exists(): raise FileNotFoundError(self.__TotalPath)

		self.__Items: "dict[str, Box | TableDescriptor]" = dict()
		self.reload()

	def __repr__(self) -> str:
		"""Возвращает техническое представление объекта."""

		# To-Do: рефакторинг алгоритма?
		Lines = list()
		IsRoot = str(self.__VirtualPath) == "."

		if IsRoot: Lines.append("<RootBox>")
		else: Lines.append(f"<Box::{self.name}>")
		
		for Item in tuple(sorted(self.items, key = lambda Item: str(Item))):
			Indentation = len(self.__VirtualPath.parts)
			Lines.append("    " * Indentation + str(Item))

		if IsRoot:
			Lines = ["    " + Line for Line in Lines]
			Lines[0] = Lines[0].lstrip()

		return "\n".join(Lines)
	
	def create_box(self, name: str) -> "Box":
		"""
		Создаёт контейнер внутри текущего контейнера.

		:param name: Имя нового контейнера.
		:type name: str
		:return: Представление созданного контейнера.
		:rtype: Box
		"""

		return self.__Driver.create_box(name, self.__TotalPath / name)
	
	def create_table(self, type: str, name: str) -> "TableDescriptor":
		"""
		Создаёт таблицу внутри текущего контейнера.

		:param type: Тип таблицы.
		:type type: str
		:param name: Имя таблицы.
		:type name: str
		:return: Представление созданного контейнера.
		:rtype: Box
		"""

		return self.__Driver.create_table(type, name, self.__VirtualPath)

	def delete(self):
		"""Удаляет текущее представление."""

		os.rmdir(self.__TotalPath)

	def get_item(self, name: str) -> "Box | TableDescriptor":
		"""
		Возвращает элемент по имени.

		:param name: Имя элемента.
		:type name: str
		:return: Элемент.
		:rtype: Box | TableDescriptor
		:raises KeyError: Выбрасывается при отсутствии элемента с указанным именем.
		"""

		return self.__Items[name]
	
	def reload(self) -> "dict[str, Box | TableDescriptor]":
		"""
		Сканирует директорию контейнера.
		
		:return: Список элементов текущего представления.
		:rtype: tuple[Box | TableDescriptor]
		"""

		Elements = tuple(Value.name for Value in os.scandir(self.__TotalPath) if Value.is_dir())
		Items = dict()

		for Element in Elements:
			ElementPath = self.__VirtualPath / Element
			ManifestPath = self.__Driver.storage_directory / ElementPath / "manifest.json"
			
			if ManifestPath.exists(): Items[Element] = TableDescriptor(self.__Driver, self, ElementPath)
			else: Items[Element] = Box(self.__Driver, self.__VirtualPath, Element)

		self.__Items = Items

		return self.__Items