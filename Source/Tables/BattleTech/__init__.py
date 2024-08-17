from Source.Core.Exceptions import *
from Source.Core.Errors import *

from dublib.CLI.Terminalyzer import Command, ParsedCommandData
from dublib.Engine.Bus import ExecutionError, ExecutionStatus
from dublib.Methods.Filesystem import NormalizePath
from dublib.Methods.JSON import ReadJSON, WriteJSON

import os

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class BattleTech_NoteCLI:
	"""Обработчик взаимодействий с записью через CLI."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		return self.__Commands

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GenerateCommands(self) -> list[Command]:
		"""Генерирует список команд."""

		return list()
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BattleTech_Table", note: "BattleTech_Note"):
		"""
		Обработчик взаимодействий с таблицей через CLI.
			table – объектное представление таблицы;\n
			note – объектное представление записи.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Table = table
		self.__Note = note
		self.__Commands = self.__GenerateCommands()

	def execute(self, command_data: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

		return ExecutionStatus(0)

class BattleTech_TableCLI:
	"""Обработчик взаимодействий с таблицей через CLI."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		return self.__Commands

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GenerateCommands(self) -> list[Command]:
		"""Генерирует список команд."""

		return list()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BattleTech_Table"):
		"""
		Обработчик взаимодействий с таблицей через CLI.
			table – объектное представление таблицы.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Table = table
		self.__Commands = self.__GenerateCommands()

	def execute(self, command_data: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

		return ExecutionStatus(0)
	
#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class BattleTech_Note:
	"""Базовая запись BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	BASE_NOTE = {
		"name": None,
		"another_names": [],
		"estimation": None,
		"status": None,
		"group": None,
		"tags": [],
		"metainfo": {},
		"parts": []
	}

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> BattleTech_NoteCLI:
		"""Класс-обработчик CLI записи."""

		return self.__NoteCLI
	
	@property
	def id(self) -> int:
		"""Идентификатор."""

		return self.__ID
	
	@property
	def name(self) -> str | None:
		"""Название."""

		return self.__Data["name"]

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self.__Data["another_names"]
	
	@property
	def emoji_status(self) -> str:
		"""Статус просмотра в видзе эмодзи."""

		Statuses = {
			"announced": "ℹ️",
			"watching": "▶️",
			"completed": "✅",
			"dropped": "⛔",
			"planned": "🗓️",
			None: ""
		}

		return Statuses[self.__Data["status"]]

	@property
	def estimation(self) -> int | None:
		"""Оценка."""

		return self.__Data["estimation"]

	@property
	def group_id(self) -> int | None:
		"""Идентификатор группы."""

		return self.__Data["group"]

	@property
	def metainfo(self) -> dict:
		"""Метаданные."""

		return self.__Data["metainfo"]

	@property
	def parts(self) -> list[dict]:
		"""Список частей."""

		return list(self.__Data["parts"])

	@property
	def progress(self) -> float:
		"""Прогресс просмотра."""

		Progress = 0
		MaxProgress = 0
		CurrentProgress = 0
		Parts = self.parts

		if Parts:

			for Part in self.parts:

				if "announced" not in Part.keys() and "skipped" not in Part.keys():

					if "series" in Part.keys() and Part["series"] != None:
						MaxProgress += Part["series"]

					else:
						MaxProgress += 1

			for Part in self.parts:

				if "announced" not in Part.keys() and "skipped" not in Part.keys():

					if "watched" in Part.keys() and "series" in Part.keys() and Part["series"] != None:
						CurrentProgress += Part["series"] if "mark" not in Part.keys() else Part["mark"]

					elif "watched" in Part.keys():
						CurrentProgress += 1

			Progress = round(float(CurrentProgress / MaxProgress * 100), 1)
			if str(Progress).endswith(".0"): Progress = int(Progress)

		return Progress

	@property
	def status(self) -> str | None:
		"""Статус просмотра."""

		return self.__Data["status"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return list(self.__Data["tags"])

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BattleTech_Table", note_id: int):
		"""
		Запись о просмотре аниме.
			table – объектное представление таблицы;\n
			note_id – идентификатор записи.
		"""
		
		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__ID = note_id
		self.__Table = table
		self.__Path = f"{table.path}/{self.__ID}.json"
		self.__Data = ReadJSON(self.__Path)
		self.__NoteCLI = Anime_NoteCLI(table, self)

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает запись.
			name – название записи.
		"""

		Status = ExecutionStatus(0)

		try:
			self.__Data["name"] = name
			self.save()
			Status.message = "Name updated."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def save(self) -> ExecutionStatus:
		"""Сохраняет запись в локальный файл."""

		Status = ExecutionStatus(0)

		try:
			WriteJSON(self.__Path, self.__Data)

		except: Status = ERROR_UNKNOWN

		return Status

class BattleTech_Table:
	"""Базовая таблица BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "battletech"
	MANIFEST: dict = {
		"version": 1,
		"type": "battletech",
		"modules": [
			{
				"name": "books",
				"type": "battletech:books",
				"active": False
			}
		]
	}

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> BattleTech_TableCLI:
		"""Класс-обработчик CLI таблицы."""

		return self.__TableCLI

	@property
	def manifest(self) -> dict:
		"""Манифест таблицы."""

		return self.__Manifest.copy()	

	@property
	def modules(self) -> dict:
		"""Словарь модулей."""

		return self.__Manifest["modules"].copy()

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self.__Name

	@property
	def notes(self) -> list[BattleTech_Note]:
		"""Список записей."""

		return self.__Notes.values()
	
	@property
	def notes_id(self) -> list[int]:
		"""Список ID записей."""

		return self.__Notes.keys()

	@property
	def storage(self) -> str:
		"""Путь к хранилищу таблиц."""

		return self.__StorageDirectory

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Create(self):
		"""Создаёт таблицу."""

		if not os.path.exists(f"{self.__Path}"): os.makedirs(f"{self.__Path}")
		WriteJSON(f"{self.__Path}/manifest.json", self.MANIFEST)

	def __GenerateNewID(self, id_list: list[int]) -> int:
		"""
		Генерирует новый ID.
			id_list – список существующих ID.
		"""

		NewID = None
		if type(id_list) != list: id_list = list(id_list)

		if self.__Manifest["recycle_id"]:

			for ID in range(1, len(id_list) + 1):

				if ID not in id_list:
					NewID = ID
					break

		if not NewID: NewID = int(max(id_list)) + 1 if len(id_list) > 0 else 1

		return NewID

	def __GetNotesListID(self) -> list[int]:
		"""Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON."""

		ListID = list()
		Files = os.listdir(f"{self.__Path}")
		Files = list(filter(lambda File: File.endswith(".json"), Files))

		for File in Files: 
			if not File.replace(".json", "").isdigit(): Files.remove(File)

		for File in Files: ListID.append(int(File.replace(".json", "")))
		
		return ListID

	def __ReadNote(self, note_id: int):
		"""
		Считывает содержимое записи.
			note_id – идентификатор записи.
		"""

		self.__Notes[note_id] = Anime_Note(self, note_id)

	def __ReadNotes(self):
		"""Считывает содержимое всех записей."""

		ListID = self.__GetNotesListID()

		for ID in ListID:
			self.__ReadNote(ID)

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, storage: str, name: str, autocreation: bool = True):
		"""
		Базовая таблица BattleTech.
			storage_path – директория хранения таблиц;\n
			name – название таблицы;\n
			autocreation – указывает, нужно ли создавать таблицу при отсутствии таковой. 
		"""

		
		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__StorageDirectory = NormalizePath(storage)
		self.__Name = name
		self.__Path = f"{self.__StorageDirectory}/{name}"
		self.__Notes = dict()
		self.__TableCLI = BattleTech_TableCLI(self)
		self.__Manifest = None

		#---> Проверка существования или создание таблицы.
		#==========================================================================================#
		if not os.path.exists(f"{self.__Path}/manifest.json") and autocreation: self.__Create()
		elif not os.path.exists(f"{self.__Path}/manifest.json"): raise FileNotFoundError(f"{self.__Path}/manifest.json")

		#---> Загрузка данных.
		#==========================================================================================#
		self.__Manifest = ReadJSON(f"{self.__Path}/manifest.json")
		if self.__Manifest["type"] != self.TYPE: raise TypeError(f"Only \"{self.TYPE}\" type tables supported.")
		self.__ReadNotes()

	def create_note(self) -> ExecutionStatus:
		"""Создаёт запись."""

		Status = ExecutionStatus(0)

		try:
			ID = self.__GenerateNewID(self.__Notes.keys())
			WriteJSON(f"{self.__Path}/{ID}.json", Anime_Note.BASE_NOTE)
			self.__ReadNote(ID)
			Status["note_id"] = ID
			Status.message = f"Note #{ID} created."

		except: Status = ERROR_UNKNOWN

		return Status
	
	def delete_note(self, note_id: int) -> ExecutionStatus:
		"""
		Удаляет запись из таблицы. 
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus(0)

		try:
			note_id = int(note_id)
			del self.__Notes[note_id]
			os.remove(f"{self.__StorageDirectory}/{self.__Path}/{note_id}.json")
			Status.message = "Note deleted."

		except: Status = ERROR_UNKNOWN

		return Status

	def get_module_info(self, module: str) -> ExecutionStatus:
		"""
		Возвращает данные модуля.
			module – название модуля.
		"""

		Status = ExecutionStatus(0)

		try:

			for Module in self.__Manifest["modules"]:

				if Module["name"] == module: 
					Status.value = Module
					break

		except: Status = ERROR_UNKNOWN

		return Status

	def get_note(self, note_id: int) -> ExecutionStatus:
		"""
		Возвращает запись.
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus(0)

		try:
			note_id = int(note_id)
			if note_id in self.__Notes.keys(): Status.value = self.__Notes[note_id]
			else: Status = TABLE_ERROR_MISSING_NOTE

		except: Status = ERROR_UNKNOWN

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		Status = ExecutionStatus(0)

		try:
			OldPath = self.__Path
			NewPath = self.__Path.split("/")
			NewPath[-1] = name
			self.__Path = "/".join(NewPath)
			os.rename(f"{OldPath}", f"{self.__Path}")
			self.__Name = name
			Status.message = "Table renamed."

		except: Status = ERROR_UNKNOWN

		return Status

	def save_manifest(self) -> ExecutionStatus:
		"""Обновляет файл манифеста."""

		Status = ExecutionStatus(0)

		try:
			WriteJSON(f"{self.__Path}/manifest.json", self.__Manifest)

		except: Status = ERROR_UNKNOWN

		return Status
	
	def set_module_status(self, module: str, status: bool) -> ExecutionStatus:
		"""
		Задаёт модулю статус активации.
			module – название модуля;\n
			status – статус активации.
		"""

		Status = ExecutionStatus(0)

		try:
			
			for Index in range(len(self.__Manifest["modules"])):

				if self.__Manifest["modules"][Index]["name"] == module: 
					self.__Manifest["modules"][Index]["active"] = status
					break

			self.save_manifest()

		except: Status = ERROR_UNKNOWN

		return Status