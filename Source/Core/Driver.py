from Source.Core.Base import Manifest, Module, Table
from Source.Core.Bus import ExecutionStatus
from Source.Core.Messages import Errors

import Source.Tables as TablesTypes

from dublib.Methods.Filesystem import ReadJSON, WriteJSON

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

			TablesTypes.Otaku.TYPE: TablesTypes.Otaku,
			TablesTypes.Otaku_Anime.TYPE: TablesTypes.Otaku_Anime,

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
		self.__Objects: dict[str, Table | Module] = dict()

		self.__ReadSession()
		if mount: self.mount()

	def create_table(self, name: str, type: str | None = None) -> ExecutionStatus:
		"""
		Создаёт таблицу.
			name – название;\n
			type – тип.
		"""

		Status = ExecutionStatus()

		if not self.__StorageDirectory or not os.path.exists(self.__StorageDirectory):
			Status.push_error(Errors.Driver.STORAGE_NOT_MOUNTED)
			return Status

		try:
			NewTable: Table = self.__Tables[type](self, self.__StorageDirectory, name)
			Status += NewTable.create()
			if Status: Status.push_message("Table created.")

		except KeyError: Status.push_error(Errors.Driver.NO_TABLE_TYPE)
		except: Status.push_error(Errors.UNKNOWN)

		return Status
	
	def get_loaded_object(self, table_name: str, module_name: str | None = None) -> ExecutionStatus:
		"""
		Возвращает загруженный в оперативную память объект.

		:param table_name: Имя таблицы.
		:type table_name: str
		:param module_name: Имя модуля, если требуется модуль.
		:type module_name: str | None
		:return: Статус выполнения.
		:rtype: ExecutionStatus
		"""

		Status = ExecutionStatus()
		Name = f"{table_name}:{module_name}" if module_name else table_name

		try: Status.value = self.__Objects[Name]
		except KeyError: Status.push_error(Errors.Driver.MISSING_OBJECT)
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def initialize_module(self, type: str, table: Table) -> ExecutionStatus:
		"""
		Инициализирует модуль таблицы.

		:param type: Тип модуля в формате `{TABLE}:{MODULE}`.
		:type type: str
		:param table: Таблица, к которой привязывается модуль.
		:type table: Table
		:return: Статус выполнения.
		:rtype: ExecutionStatus
		"""

		Status = ExecutionStatus()

		try:

			if type in tuple(Element.type for Element in table.manifest.modules):
				NewModule: Module = self.__Tables[type](self, self.__StorageDirectory, table, type.split(":")[-1])
				Status += NewModule.create()
				Status.push_message("Module initialized.")

			else: Status.push_error(Errors.Driver.NO_MODULE_TYPE)

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
			Path = f"{self.__StorageDirectory}/{name}{module}"
			Status.value = Manifest(Path).load()

		except FileExistsError: Status.push_message(Errors.Driver.BAD_MANIFEST)

		return Status	

	def load_module(self, table: Table, module_name: str) -> ExecutionStatus:
		"""
		Загружает модуль.
			table – таблица, к которой привязан модуль;\n
			module_name – название модуля.
		"""

		Status = ExecutionStatus()
		
		try:
			ManifestLoadingStatus = ExecutionStatus()
			ObjectPath = f"{table.name}:{module_name}"

			LoadStatus = self.get_loaded_object(table.name, module_name)
			if not LoadStatus.has_errors and LoadStatus: return LoadStatus

			ManifestLoadingStatus = self.load_manifest(table.name, module_name)
			
			if ManifestLoadingStatus:
				TableManifest: Manifest = ManifestLoadingStatus.value
				TableToOpen = None
				TableToOpen = self.__Tables[TableManifest.type](self, self.__StorageDirectory, table, module_name)
				Status: ExecutionStatus = TableToOpen.open()
				if not Status.has_errors: self.__Objects[ObjectPath] = Status.value

		except FileNotFoundError: Status.push_error(Errors.PATH_NOT_FOUND)
		except ImportError: Status.push_error(Errors.UNKNOWN)

		return Status

	def load_table(self, table_name: str) -> ExecutionStatus:
		"""
		Загружает таблицу или модуль.
			table_name – название таблицы.
		"""

		Status = ExecutionStatus()
		
		try:
			ManifestLoadingStatus = ExecutionStatus()

			LoadingStatus = self.get_loaded_object(table_name)
			if not LoadingStatus.has_errors: return LoadingStatus
			else: ManifestLoadingStatus = self.load_manifest(table_name)

			if ManifestLoadingStatus:
				TableManifest: Manifest = ManifestLoadingStatus.value
				TableToOpen: Table = self.__Tables[TableManifest.type](self, self.__StorageDirectory, table_name)
				Status += TableToOpen.open()
				if not Status.has_errors: self.__Objects[table_name] = Status.value
				
		except FileNotFoundError: Status.push_error(Errors.PATH_NOT_FOUND)
		except: Status.push_error(Errors.UNKNOWN)
		
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

			else: Status.push_error(Errors.PATH_NOT_FOUND)

		except: Status.push_error(Errors.UNKNOWN)

		return Status
	
	def rename_loaded_table(self, old_table_name: str, table_name: str) -> ExecutionStatus:
		"""
		Изменяет название таблица.
			old_table_name – прежнее название таблицы;\n
			table_name – новое название таблицы.
		"""

		Status = ExecutionStatus()

		try:
			if table_name in self.__Objects.keys():
				Status.push_error(Errors.Driver.OBJECT_OVERWRITING_DENIED)
				return Status
			
			self.__Objects[old_table_name].rename(table_name)
			self.__Objects[table_name] = self.__Objects[old_table_name]
			del self.__Objects[old_table_name]

		except KeyError: Status.push_error(Errors.Driver.MISSING_OBJECT)
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def rename_loaded_module(self, table_name: str, old_module_name: str, module_name: str) -> ExecutionStatus:
		"""
		Изменяет название объекта.
			table_name – название таблицы;\n
			old_module_name – прежнее название модуля;\n
			module_name – новое название модуля.
		"""

		Status = ExecutionStatus()
		OldName = f"{table_name}:{old_module_name}"
		Name = f"{table_name}:{module_name}"

		try:
			if Name in self.__Objects.keys():
				Status.push_error(Errors.Driver.OBJECT_OVERWRITING_DENIED)
				return Status
			
			self.__Objects[OldName].rename(module_name)
			self.__Objects[Name] = self.__Objects[OldName]
			del self.__Objects[OldName]

		except KeyError: Status.push_error(Errors.Driver.MISSING_OBJECT)
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def unload_object(self, table: Table, module: Module | None = None) -> ExecutionStatus:
		"""
		Выгружает объект из оперативной памяти.

		:param table: Таблица.
		:type table: Table
		:param module: Модуль. Если указан, таблица не будет выгружена.
		:type module: Module | None
		:return: Статус выполнения.
		:rtype: ExecutionStatus
		"""

		Status = ExecutionStatus()
		Name = f"{table.name}:{module.name}" if module else table.name

		try: del self.__Objects[Name]
		except KeyError: Status.push_error(Errors.Driver.MISSING_OBJECT)
		except: Status.push_error(Errors.UNKNOWN)

		return Status