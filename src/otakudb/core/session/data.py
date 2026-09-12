from json import JSONDecodeError
from pathlib import Path

from dublib.functions.filesystem import json

class SessionData:
	"""Данные сессии."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def last_mounted_storage(self) -> Path | None:
		"""Путь к последнему монтированному хранилищу."""

		Value = self.__Data.get("last_mounted_storage")
		if Value: Value = Path(Value)

		return Value

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __LoadData(self):
		"""Загружает данные из файла JSON."""

		try: self.__Data = json.read(".session.json")
		except (FileNotFoundError, JSONDecodeError): pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Данные сессии."""

		self.__Data = {}

		self.__LoadData()

	def save(self):
		"""Сохраняет данные в файл JSON."""

		json.write(".session.json", self.__Data)
		
	def set_last_mounted_storage(self, path: Path | None):
		"""
		Задаёт путь к последнему монтированному хранилищу.

		:param path: Путь к хранилищу.
		:type path: Path | None
		"""
		
		self.__Data["last_mounted_storage"] = path.as_posix() if path else None
		self.save()