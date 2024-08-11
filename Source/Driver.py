from Source.Tables.BattleTech.Books import BattleTech_Books_Table
from Source.Tables.Anime import Anime_Table
from Source.CLI.Templates import Pick
from Source.Core.Errors import *

from dublib.Methods.JSON import ReadJSON, WriteJSON
from dublib.Engine.Bus import ExecutionStatus

import shutil
import os

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Tables:
	"""Дескрипторы типов таблиц."""

	def __init__(self):
		"""Дескрипторы типов таблиц."""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__TablesTypes = {
			Anime_Table.TYPE: Anime_Table,
			BattleTech_Books_Table.type: BattleTech_Books_Table
		}

	def __getitem__(self, table_type: str) -> any:
		"""
		Возвращает класс, описывающий тип таблицы.
			table_type – тип таблицы.
		"""

		return self.__TablesTypes[table_type]

class Modules:
	"""Парсер модулей таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def names(self) -> list[str]:
		"""Список названий модулей."""

		return list(self.__Modules.keys())
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ToDict(self, modules: list[dict]) -> dict:
		"""
		Преобразует список модулей в словарь.
			modules – список модулей.
		"""

		ModulesDict = dict()
		for Module in modules: ModulesDict[Module["name"]] = Module

		return ModulesDict
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, modules: list[dict]):
		"""
		Парсер модулей таблицы.
			modules – список модулей.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Modules = self.__ToDict(modules)

	def __getitem__(self, module_name: str) -> dict:
		"""
		Возвращает данные модуля.
			module_name – название модуля.
		"""

		return self.__Modules[module_name]

	def get_module_path(self, module_name: str) -> str:
		"""
		Возвращает путь к модулю.
			module_name – название модуля.
		"""

		return self.__Modules[module_name]["path"]

	def get_module_type(self, module_name: str) -> str:
		"""
		Возвращает тип модуля.
			module_name – название модуля.
		"""

		return self.__Modules[module_name]["type"]

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Driver:
	"""Менеджер таблиц."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_mounted(self) -> bool:
		"""Состояние: монтировано ли хранилище."""

		return True if self.__StorageDirectory else False

	@property
	def tables(self) -> list[str]:
		"""Список названий существующих таблиц."""

		StorageList = os.listdir(self.__StorageDirectory)
		Tables = list()

		for Object in StorageList:
			Path = f"{self.__StorageDirectory}/{Object}"

			if os.path.isdir(Path): 
				if os.path.exists(f"{Path}/manifest.json") or os.path.exists(f"{Path}/modules.json"): Tables.append(Object)

		return Tables

	@property
	def storage_directory(self) -> str | None:
		"""Директория хранилища."""

		return self.__StorageDirectory

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ReadSession(self):
		"""Читает сессионный файл."""

		if os.path.exists("session.json"):
			self.__Session = ReadJSON("session.json")

		else:
			self.__SaveSession()

	def __SaveSession(self):
		"""Сохраняет сессионный файл."""

		WriteJSON("session.json", self.__Session)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, mount: bool = False):
		"""
		Менеджер таблиц.
			mount – указывает, следует ли монтировать директорию хранилища.
		"""
		
		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__StorageDirectory = None
		self.__Session = {
			"storage-directory": "Data"
		}
		self.__Tables = Tables()

		self.__ReadSession()
		if mount: self.mount()

	def create_table(self, name: str, table_type: str) -> ExecutionStatus:
		"""
		Создаёт таблицу.
			name – название таблицы;
			table_type – тип таблицы.
		"""

		Status = ExecutionStatus(0)

		try:
			self.__Tables[table_type](self.__StorageDirectory, name, autocreation = True)
			Status.message = "Created."

		except KeyError:
			Status = DRIVER_ERROR_NO_TABLE_TYPE
			Status["print"] = table_type

		except FileExistsError: Status = ERROR_UNKNOWN

		return Status

	def get_manifest(self, name: str, module: str | None = None) -> ExecutionStatus:
		"""
		Считывает манифест таблицы.
			name – название таблицы;\n
			module – название модуля.
		"""

		Status = ExecutionStatus(0)

		try:
			module = ("/" + module) if module else ""
			Status.value = ReadJSON(f"{self.__StorageDirectory}/{name}{module}/manifest.json")

		except FileExistsError:
			Status = DRIVER_ERROR_BAD_MANIFEST

		return Status	

	def mount(self, storage_dir: str | None = None) -> ExecutionStatus:
		"""
		Указывает каталог хранения таблиц.
			storage_dir – директория хранилища.
		"""

		Status = ExecutionStatus(0)
		storage_dir = self.__Session["storage-directory"] if not storage_dir else storage_dir
		
		try:
			
			if os.path.exists(storage_dir): 
				self.__StorageDirectory = storage_dir
				self.__Session["storage-directory"] = storage_dir
				self.__SaveSession()
				Status.message = f"Mounted: \"{storage_dir}\"."

			else:
				Status = DRIVER_ERROR_BAD_PATH

		except:
			Status = ERROR_UNKNOWN

		return Status

	def open_table(self, name: str) -> ExecutionStatus:
		"""
		Открывает таблицу. Возвращает объектное представление таблицы.
			name – название таблицы.
		"""

		Status = ExecutionStatus(0)
		
		try:
			Manifest = self.get_manifest(name)

			if Manifest.code == 0:
				Manifest = Manifest.value
				Type = Manifest["type"]

				if "modules" in Manifest.keys():
					ParsedModules = Modules(Manifest["modules"])
					ModuleName = Pick("Choose table submodule:", ParsedModules.names)
					Type = ParsedModules.get_module_type(ModuleName)

				Table = self.__Tables[Type](self.__StorageDirectory, name, autocreation = False)
				Status.value = Table

			else: Status = Manifest

		except FileExistsError: Status = DRIVER_ERROR_BAD_PATH

		except IndexError: Status = DRIVER_ERROR_NO_MODULES

		except KeyError: Status = DRIVER_ERROR_NO_TABLE_TYPE

		except ImportError: Status = ERROR_UNKNOWN

		return Status

	def delete_table(self, name: str) -> ExecutionStatus:
		"""
		Удаляет таблицу.
			name – название таблицы.
		"""

		Status = ExecutionStatus(0)

		try:
			shutil.rmtree(f"{self.__StorageDirectory}/{name}")

		except FileNotFoundError: Status = DRIVER_ERROR_BAD_PATH

		return Status