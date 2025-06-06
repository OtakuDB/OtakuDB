from Source.Core.Base import Table, Module, Note
from Source.Core.Bus import ExecutionStatus
from Source.Core.Messages import Errors
from Source.Core.Driver import Driver

from dataclasses import dataclass

import enum

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class StorageLevels(enum.Enum):
	"""Уровни объектов хранилища."""

	DRIVER = None
	TABLE = "table"
	MODULE = "module"
	NOTE = "note"

@dataclass
class PathObjects:
	"""Контейнер объектов в пути."""

	table: str = None
	module: str = None
	note: int = None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Session:
	"""Сессия работы с хранилищем таблиц."""

	#==========================================================================================#
	# >>>>> ОБЪЕКТЫ ХРАНИЛИЩА <<<<< #
	#==========================================================================================#

	@property
	def table(self) -> Table | None:
		"""Объект открытой таблицы."""

		return self.__Table
	
	@property
	def module(self) -> Module | None:
		"""Объект открытого модуля."""

		return self.__Module
	
	@property
	def note(self) -> Note | None:
		"""Объект открытой записи."""

		return self.__Note
	
	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def driver(self) -> Driver:
		"""Драйвер хранилища."""

		return self.__Driver

	@property
	def path(self) -> str:
		"""Текущий путь внутри хранилища."""

		PathParts = list()
		
		if self.__Table: PathParts.append(self.__Table.name)
		if self.__Module: PathParts.append(self.__Module.name)
		if self.__Note: PathParts.append(str(self.__Note.id))

		return "/".join(PathParts)
	
	@property
	def storage_level(self) -> StorageLevels:
		"""Уровень текущего открытого объекта хранилища."""

		return self.__Level

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParsePath(self, path: str) -> PathObjects:
		"""
		Парсит путь на элементы.
			path – путь к объекту.
		"""

		if not path.startswith("/"): path = f"{self.path}/{path}"

		TableName = None
		ModuleName = None
		NoteID = None 

		PathParts = path.strip("/").split("/")

		if PathParts[-1].isdigit() or len(PathParts) == 3: NoteID = PathParts.pop()
		TableName = PathParts[0]
		if len(PathParts) == 2: ModuleName = PathParts[1]
		
		return PathObjects(TableName, ModuleName, NoteID)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self):
		"""Сессия работы с хранилищем таблиц."""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Driver = Driver(mount = True)
		self.__Level = StorageLevels.DRIVER

		self.__Table: Table = None
		self.__Module: Table = None
		self.__Note: Note = None

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ НАВИГАЦИИ <<<<< #
	#==========================================================================================#

	def close(self):
		"""Закрывает объект текущего уровня."""

		if self.__Note:
			self.__Note = None
			self.__Level = StorageLevels.MODULE if self.__Module else StorageLevels.TABLE

		elif self.__Module:
			self.__Module = None
			self.__Level = StorageLevels.TABLE

		elif self.__Table:
			self.__Table = None
			self.__Level = StorageLevels.DRIVER

	def open_objects(self, path: str) -> ExecutionStatus:
		"""
		Открывает объекты по указанному пути и устанавливает их в качестве активных.
			path – путь к объектам.
		"""

		Status = ExecutionStatus()
		Targets = self.__ParsePath(path)

		if Targets.table: 
			OpenStatus = self.__Driver.load_table(Targets.table)
			Status.merge(OpenStatus, overwrite = False)

			if OpenStatus.value:
				self.__Table = OpenStatus.value
				self.__Level = StorageLevels.TABLE

		else: self.__Table = None

		if Targets.module: 
			OpenStatus = self.__Driver.load_module(self.__Table, Targets.module)
			Status.merge(OpenStatus, overwrite = False)

			if OpenStatus.value:
				self.__Module = OpenStatus.value
				self.__Level = StorageLevels.MODULE

		else: self.__Module = None

		if Targets.note: 
			OpenStatus = ExecutionStatus()
			if self.__Module: OpenStatus = self.__Module.get_note(Targets.note)
			else: OpenStatus = self.__Table.get_note(Targets.note)
			Status.merge(OpenStatus, overwrite = False)

			if OpenStatus.value:
				self.__Note = OpenStatus.value
				self.__Level = StorageLevels.NOTE

		else: self.__Note = None

		return Status
	
	def rename_current_object(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает объект текущего уровня (таблицу или модуль).
			name – новое имя.
		"""

		Status = ExecutionStatus()

		if name.isdigit():
			Status.push_error("Driver.INCORRECT_OBJECT_NAME")
			return Status

		if self.storage_level is StorageLevels.TABLE:
			Status += self.__Driver.rename_loaded_table(self.__Table.name, name)
			Status.push_message("Table renamed.")

		elif self.storage_level is StorageLevels.MODULE:
			Status += self.__Driver.rename_loaded_module(self.__Table.name, self.__Module.name, name)
			Status.push_message("Module renamed.")

		elif self.storage_level is StorageLevels.NOTE:
			self.__Note.rename(name)
			Status.push_message("Note renamed.")

		else: Status.push_error(Errors.UNKNOWN)

		return Status