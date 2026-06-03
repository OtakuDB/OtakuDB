from .Box import Box, RootBox

from Source.Core import Exceptions

from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
	from .Driver import Driver

class Navigator:
	"""Оператор навигации."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def current_box(self) -> Box | RootBox:
		"""Текущий контейнер."""

		return self.__CurrentBox
	
	@property
	def root_box(self) -> RootBox:
		"""Корневой контейнер."""

		return self.__Driver.root_box

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver"):
		"""
		Оператор навигации.

		:param driver: Драйвер.
		:type driver: Driver
		"""

		self.__Driver = driver

		self.__CurrentBox = self.__Driver.root_box

	def inbox(self, box_name: str) -> Box:
		"""
		Открывает вложенное хранилище.

		:param box_name: Название хранилища.
		:type box_name: str
		:raises StorageUnmounted: Хранилище отмонтировано.
		:return: Представление текущего навигации.
		:rtype: Box
		"""

		if not self.__Driver.storage_directory: raise Exceptions.Driver.StorageUnmounted()
		Item = self.__CurrentBox.get_item(box_name)
		if type(Item) != Box: raise Exceptions.Navigator.UnableInboxNonBoxObject(Item.path)
		self.__CurrentBox = Item
	
	def navigate(self, target_path: Path) -> Box:
		"""
		Выполняет переход по вирутальному пути.

		:param target_path: Вирутальный путь с поддержкой POSIX-стандарта.
		:type target_path: Path
		:return: Целевой контейнер.
		:rtype: Box
		:raises UnableInboxNonBoxObject: Невозможно перейти в каталог, не представляющий контейнер.
		"""

		if target_path.is_absolute():
			self.__CurrentBox = self.__Driver.get_box(target_path)
			
		else:
			CurrentVirtualPath = self.__CurrentBox.virtual_path

			for PathPart in target_path.parts:
				if PathPart == "..": CurrentVirtualPath = CurrentVirtualPath.parent
				else: CurrentVirtualPath = CurrentVirtualPath / PathPart

			if self.__Driver.is_box(CurrentVirtualPath): self.__CurrentBox = self.__Driver.get_box(CurrentVirtualPath)
			else: raise Exceptions.Navigator.UnableInboxNonBoxObject(CurrentVirtualPath)

		return self.__CurrentBox

	def to_root(self):
		"""Переходит в корневое представление древа навигации."""

		self.__CurrentBox = self.__Driver.root_box

	def unbox(self):
		"""
		Переходит в родительское представление.

		:raises RootUnboxingDenied: Переход в родительское представление из корня хранилища.
		:raises StorageUnmounted: Хранилище отмонтировано.
		"""

		if not self.__Driver.storage_directory: raise Exceptions.Driver.StorageUnmounted()

		Parent = self.__CurrentBox.parent
		if not Parent: raise Exceptions.Driver.RootUnboxingDenied()
		self.__CurrentBox = Parent