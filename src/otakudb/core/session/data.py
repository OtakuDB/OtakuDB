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

		value: str | None = self.__data.get("last_mounted_storage")

		return Path(value) if value else None

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Данные сессии."""

		self.__data_file: Path = Path(".session.json")
		self.__data: dict = {}
		
	def load(self):
		"""Загружает данные из файла данных сессии."""

		if not self.__data_file.exists():
			return

		self.__data = json.read(self.__data_file)

	def save(self):
		"""Сохраняет данные в файл данных сессии."""

		json.write(self.__data_file, self.__data)

	def set_last_mounted_storage(self, storage_path: Path | None):
		"""
		Задаёт путь к последнему монтированному хранилищу.

		:param storage_path: Путь к хранилищу.
		:type storage_path: Path | None
		"""
		
		self.__data["last_mounted_storage"] = storage_path.as_posix() if storage_path else None
		self.save()