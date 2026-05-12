from .Navigator import Navigator
from .Driver import Driver

from os import PathLike

class Session:
	"""Сессия взаимодействия."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def driver(self) -> Driver:
		"""Драйвер хранилища."""

		return self.__Driver
	
	@property
	def navigator(self) -> Navigator:
		"""Оператор навигации."""

		return self.__Navigator

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, storage: PathLike):
		"""
		Сессия взаимодействия.

		:param storage: Путь к директории хранилища.
		:type storage: PathLike
		"""

		self.__Driver = Driver()
		self.__Driver.mount(storage)
		self.__Navigator = Navigator(self.__Driver)