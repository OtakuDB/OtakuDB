from pathlib import Path
from typing import TYPE_CHECKING

from .. import exceptions
from .box import Box, RootBox

if TYPE_CHECKING:
	from .driver import Driver

class Navigator:
	"""Оператор навигации."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def current_box(self) -> Box | RootBox:
		"""Текущий контейнер."""

		return self.__current_box
	
	@property
	def root_box(self) -> RootBox:
		"""Корневой контейнер."""

		return self.__driver.root_box

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver"):
		"""
		Оператор навигации.

		:param driver: Драйвер.
		:type driver: Driver
		"""

		self.__driver = driver
		self.__current_box: Box | RootBox = self.__driver.root_box

	def inbox(self, box_name: str) -> Box:
		"""
		Открывает вложенное хранилище.

		:param box_name: Название хранилища.
		:type box_name: str
		:return: Представление текущего навигации.
		:rtype: Box
		:raises UnableInboxNonBoxItemError: Невозможно открыть объект, не являющийся контейнером.
		"""
		
		item = self.__current_box.get_item(box_name)

		if not isinstance(item, Box):
			raise exceptions.session.navigator.UnableInboxNonBoxItemError(item.virtual_path)
		
		self.__current_box = item

		return item

	def navigate(self, virtual_path: Path) -> Box:
		"""
		Выполняет переход по вирутальному пути.

		:param virtual_path: Вирутальный путь с поддержкой POSIX-стандарта.
		:type virtual_path: Path
		:return: Целевой контейнер.
		:rtype: Box
		:raises UnableInboxNonBoxItemError: Невозможно перейти в каталог, не представляющий контейнер.
		"""

		if virtual_path.is_absolute():
			self.__current_box = self.__driver.get_box(virtual_path)
			
		else:
			current_box_virtual_path: Path = self.__current_box.virtual_path

			for part in virtual_path.parts:
				if part == "..": current_box_virtual_path = current_box_virtual_path.parent
				else: current_box_virtual_path = current_box_virtual_path / part

			if not self.__driver.is_box(current_box_virtual_path):
				raise exceptions.session.navigator.UnableInboxNonBoxItemError(current_box_virtual_path)

			self.__current_box = self.__driver.get_box(current_box_virtual_path)

		return self.__current_box

	def to_root(self):
		"""Переходит в корневое представление древа навигации."""

		self.__current_box = self.root_box

	def unbox(self):
		"""
		Переходит в родительский контейнер.

		:raises RootUnboxingError: Невозможно подняться из корневого каталога.
		"""

		if type(self.__current_box) is Box:
			self.__current_box = self.__current_box.parent

		raise exceptions.session.navigator.RootUnboxingError()
