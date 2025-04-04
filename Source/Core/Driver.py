from Source.Core.Base import Manifest, Table
from Source.Core.Messages import Errors

import Source.Tables as TablesTypes

from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from Source.Core.Bus import ExecutionStatus

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
			Table.TYPE: Table,
			TablesTypes.Anime.TYPE: TablesTypes.Anime,

			TablesTypes.BattleTech.TYPE: TablesTypes.BattleTech,
			TablesTypes.BattleTech_Books.TYPE: TablesTypes.BattleTech_Books,
			TablesTypes.BattleTech_Sources.TYPE: TablesTypes.BattleTech_Sources
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
	"""Драйвер таблиц."""

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
		Драйвер таблиц.
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

	def create(self, name: str, type: str | None = None, table: Table = None) -> ExecutionStatus:
		"""
		Создаёт таблицу или модуль.
			name – название;\n
			type – тип;\n
			table – таблица, к которой привязывается модуль.
		"""

		Status = ExecutionStatus()

		try:
			NewTable = None

			if table:

				for Module in table.manifest.modules:

					if Module.name == name:
						Module.activate()
						NewTable: Table = self.__Tables[Module.type](self.__StorageDirectory, table, name)
						Status.merge(NewTable.create())
				
			else:
				NewTable: Table = self.__Tables[type](self.__StorageDirectory, name)
				Status.merge(NewTable.create())

			if Status and table: Status.push_message("Module initialized.")
			elif Status: Status.push_message("Table created.")

		except KeyError: Status.push_error(Errors.Driver.NO_TABLE_TYPE)
		except: Status.push_error(Errors.UNKNOWN)

		return Status
	
	def load_manifest(self, name: str, module: str | None = None) -> ExecutionStatus:
		"""
		Считывает манифест таблицы.
			name – название таблицы;\n
			module – название модуля.
		"""

		Status = ExecutionStatus()

		try:
			module = ("/" + module) if module else ""
			Path = f"{self.__StorageDirectory}/{name}{module}/manifest.json"
			Status.value = Manifest(Path, ReadJSON(Path))

		except FileExistsError: Status.push_message(Errors.Driver.BAD_MANIFEST)

		return Status	

	def mount(self, storage_dir: str | None = None) -> ExecutionStatus:
		"""
		Указывает каталог хранения таблиц.
			storage_dir – директория хранилища.
		"""

		Status = ExecutionStatus()
		storage_dir = self.__Session["storage-directory"] if not storage_dir else storage_dir
		
		try:
			
			if os.path.exists(storage_dir): 
				self.__StorageDirectory = storage_dir
				self.__Session["storage-directory"] = storage_dir
				self.__SaveSession()
				Status.print_messages(f"Mounted: \"{storage_dir}\".")

			else: Status.push_error(Errors.Driver.PATH_NOT_FOUND)

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def open(self, name: str, table: Table = None) -> ExecutionStatus:
		"""
		Открывает таблицу или модуль.
			name – название таблицы или модуля;\n
			table – таблица, к которой привязан модуль.
		"""

		Status = ExecutionStatus()
		
		try:
			ManifestLoadingStatus = ExecutionStatus()
			if table: ManifestLoadingStatus = self.load_manifest(table.name, name)
			else: ManifestLoadingStatus = self.load_manifest(name)
			
			if ManifestLoadingStatus:
				TableManifest: Manifest = ManifestLoadingStatus.value
				TableToOpen = None
				if table: TableToOpen = self.__Tables[TableManifest.type](self.__StorageDirectory, table, name)
				else: TableToOpen: TableToOpen = self.__Tables[TableManifest.type](self.__StorageDirectory, name)
				Status: ExecutionStatus = TableToOpen.open()

		except FileNotFoundError: Status.push_error(Errors.Driver.PATH_NOT_FOUND)
		except ZeroDivisionError: Status.push_error(Errors.Driver.NO_TABLE_TYPE)
		except ImportError: Status.push_error(Errors.UNKNOWN)

		return Status