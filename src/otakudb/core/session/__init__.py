from os import PathLike
from pathlib import Path

from .data import SessionData
from .driver import Driver
from .navigator import Navigator

class Session:
	"""Сессия взаимодействия."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def data(self) -> SessionData:
		"""Данные сессии."""

		return self.__data
	
	@property
	def driver(self) -> Driver | None:
		"""Драйвер хранилища."""

		return self.__driver
	
	@property
	def navigator(self) -> Navigator | None:
		"""Оператор навигации."""

		return self.__navigator

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Сессия взаимодействия."""

		self.__driver: Driver | None = None
		self.__data: SessionData = SessionData()

		self.__navigator: Navigator | None = None

		self.__data.load()

	def mount(self, storage_path: str | PathLike[str]) -> Driver:
		"""
		Монтирует директорию как хранилище.

		:param storage: Путь к хранилищу.
		:type storage: str | PathLike[str]
		:return: Драйвер хранилища.
		:rtype: Driver
		:raises FileNotFoundError: Директория не существует.
		"""

		storage_path = Path(storage_path)

		self.__driver = Driver(storage_path)
		self.__navigator = Navigator(self.__driver)
		self.__data.set_last_mounted_storage(storage_path)
		
		return self.__driver