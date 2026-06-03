from .Navigator import Navigator
from .Data import SessionData
from .Driver import Driver

from pathlib import Path
from os import PathLike

class Session:
	"""Сессия взаимодействия."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def data(self) -> SessionData:
		"""Данные сессии."""

		return self.__Data

	@property
	def driver(self) -> Driver:
		"""Драйвер хранилища."""

		return self.__Driver
	
	@property
	def navigator(self) -> Navigator | None:
		"""Оператор навигации."""

		return self.__Navigator

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Сессия взаимодействия."""

		self.__Driver = Driver()
		self.__Navigator: Navigator | None = None
		self.__Data = SessionData()

	def mount(self, storage: PathLike):
		"""
		Монтирует директорию как хранилище.

		:param storage: Путь к хранилищу.
		:type storage: PathLike
		:raises FileNotFoundError: Директория не существует.
		"""

		storage = Path(storage)
		self.__Driver.set_storage(storage)
		self.__Navigator = Navigator(self.__Driver)
		self.__Data.set_last_mounted_storage(storage)