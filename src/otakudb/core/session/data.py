from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, TypeAdapter

from dublib.functions.filesystem import json

from ...interfaces.enums import Interfaces

#==========================================================================================#
# >>>>> DATA MODEL <<<<< #
#==========================================================================================#

class SessionDataModel(BaseModel):
	"""Session data model."""

	last_mounted_storage: Path | None = None
	interfaces_options: dict[Interfaces, dict[str, Any]] = Field(
		default_factory = lambda: {interface: {} for interface in Interfaces},
	)

#==========================================================================================#
# >>>>> MAIN CLASS <<<<< #
#==========================================================================================#

class SessionData:
	"""Session data."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def last_mounted_storage(self) -> Path | None:
		"""Путь к последнему монтированному хранилищу."""

		return self.__data.last_mounted_storage

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Session data."""

		self.__file: Path = Path(".session.json")
		self.__adapter: TypeAdapter[SessionDataModel] = TypeAdapter(SessionDataModel)
		self.__data: SessionDataModel = SessionDataModel()

	def get_global_interface_options(self, interface: Interfaces) -> dict[str, Any]:
		"""
		Return global interface options dictionary.

		:param interface: Interface type.
		:type interface: Interfaces
		:return: Global interface options dictionary.
		:rtype: dict[str, Any]
		"""
		return self.__data.interfaces_options[interface]

	def load(self):
		"""Load session data from file."""

		if self.__file.exists():
			data: dict = json.read(self.__file)
			self.__data = self.__adapter.validate_python(data)

	def save(self):
		"""Сохраняет данные в файл данных сессии."""

		data: dict = self.__adapter.dump_python(self.__data, mode = "json")
		json.write(self.__file, data)

	def set_global_interface_options(self, interface: Interfaces, options: dict[str, Any]):
		"""
		Set global interface options dictionary.

		:param interface: Interface type.
		:type interface: Interfaces
		:param options: Options dictionary.
		:type options: dict[str, Any]
		"""

		self.__data.interfaces_options[interface] = options

	def set_last_mounted_storage(self, storage_path: Path | None):
		"""
		Задаёт путь к последнему монтированному хранилищу.

		:param storage_path: Путь к хранилищу.
		:type storage_path: Path | None
		"""

		self.__data.last_mounted_storage = storage_path
