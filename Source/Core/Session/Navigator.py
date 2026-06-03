from .Box import Box

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
	def current_box(self) -> Box | None:
		"""Текущий контейнер."""

		return self.__CurrentBox
	
	@property
	def root_box(self) -> Box:
		"""Корневой контейнер."""

		return self.__RootBox

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

		self.__RootBox = self.__Driver.get_box()
		self.__CurrentBox = self.__RootBox

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
			CurrentPath = self.__CurrentBox.path

			for PathPart in target_path.parts:
				if PathPart == "..": CurrentPath = CurrentPath.parent
				else: CurrentPath = CurrentPath / PathPart

			if self.__Driver.is_box(CurrentPath): self.__CurrentBox = self.__Driver.get_box(CurrentPath)
			else: raise Exceptions.Navigator.UnableInboxNonBoxObject(CurrentPath)

		return self.__CurrentBox

	def to_root(self):
		"""Переходит в корневое представление древа навигации."""

		self.__CurrentBox = self.__RootBox

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