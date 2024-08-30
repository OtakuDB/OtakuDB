from Source.CLI.Templates import Columns
from Source.Core.Exceptions import *
from Source.Core.Warnings import *
from Source.Core.Errors import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.StyledPrinter import StyledPrinter, Styles, TextStyler 
from dublib.Methods.Filesystem import NormalizePath
from dublib.Methods.JSON import ReadJSON, WriteJSON
from dublib.CLI.Templates import Confirmation
from dublib.Engine.Bus import ExecutionStatus
from dublib.Methods.System import Clear

import shutil
import os

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class ModuleData:
	"""Данные модуля."""

	@property
	def is_active(self) -> str:
		"""Состояние: активирован ли модуль."""

		return self.__Data["is_active"]

	@property
	def name(self) -> str:
		"""Название модуля."""

		return self.__Data["name"]
	
	@property
	def type(self) -> str:
		"""Тип модуля."""

		return self.__Data["type"]

	def __init__(self, data: dict, manifest: "TableManifest"):
		"""
		Данные модуля.
			data – словарь описания;\n
			manifest – манифест.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Data = data
		self.__Manifest = manifest

	def activate(self):
		"""Активирует модуль."""

		self.__Data["is_activate"] = True
		self.__Manifest.save()

	def deactivate(self):
		"""Деактивирует модуль."""

		self.__Data["is_activate"] = False
		self.__Manifest.save()

#==========================================================================================#
# >>>>> МАНИФЕСТ <<<<< #
#==========================================================================================#

class CommonOptions:
	"""Общие опции таблицы."""

	@property
	def recycle_id(self) -> bool:
		"""Указывает, необходимо ли занимать освободившиеся ID."""

		self.__Data["recycle_id"]

	def __init__(self, data: dict):
		"""
		Общие опции таблицы.
			data – словарь опций.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Data = data

class CustomOptions:
	"""Дополнительные опции."""

	def __init__(self, data: dict):
		"""
		Дополнительные опции.
			data – словарь опций.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Data = data

	def __getitem__(self, key: str) -> any:
		"""
		Возвращает опцию.
			key – ключ опции.
		"""

		return self.__Data[key]

class MetainfoRules:
	"""Правила метаданных."""

	@property
	def fields(self) -> list[str]:
		"""Список названий полей с правилами."""

		return self.__Data.keys()

	def __init__(self, data: dict):
		"""
		Общие опции таблицы.
			data – словарь опций.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Data = data

	def __getitem__(self, key: str) -> any:
		"""
		Возвращает правило.
			key – ключ правила.
		"""

		return self.__Data[key]

class ViewerOptions:
	"""Опции просмоторщика записей."""

	def __init__(self, data: dict):
		"""
		Опции просмоторщика записей.
			data – словарь опций.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Data = data

	def __getitem__(self, key: str) -> any:
		"""
		Возвращает опцию.
			key – ключ опции.
		"""

		return self.__Data[key]

class Manifest:
	"""Манифест таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def common(self) -> CommonOptions:
		"""Общие опции таблиц."""

		return self.__Common

	@property
	def custom(self) -> CustomOptions | None:
		"""Дополнительные опции."""

		return self.__Custom

	@property
	def metainfo_rules(self) -> MetainfoRules | None:
		"""Опции метаданных."""

		return self.__MetainfoRules

	@property
	def modules(self) -> list[ModuleData]:
		"""Список модулей таблицы."""

		return self.__Modules
	
	@property
	def type(self) -> str:
		"""Тип таблицы."""

		return self.__Data["type"]
	
	@property
	def viewer(self) -> ViewerOptions | None:
		"""Опции просмоторщика записей."""

		return self.__ViewerOptions

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseModules(self) -> list[ModuleData]:
		"""Парсит данные модулей."""

		Modules = list()

		if "modules" in self.__Data.keys():
			for Module in self.__Data["modules"]: Modules.append(ModuleData(Module, self.__Data))

		return Modules

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, path: str, data: dict):
		"""
		Манифест таблицы.
			path – путь к директории таблицы;\n
			data – словарь манифеста.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Path = path
		self.__Data = data

		self.__Modules = self.__ParseModules()
		self.__Common = CommonOptions(data["common"])
		self.__MetainfoRules = MetainfoRules(data["metainfo_rules"]) if "metainfo_rules" in data.keys() else None
		self.__ViewerOptions = ViewerOptions(data["viewer"]) if "viewer" in data.keys() else None
		self.__Custom = CustomOptions(data["custom"]) if "custom" in data.keys() else None

	def save(self) -> ExecutionStatus:
		"""Сохраняет манифест."""

		Status = ExecutionStatus(0)

		try:
			ModulesBuffer = list()
			for Module in self.modules: ModulesBuffer.append({"name": Module.name, "type": Module.type, "is_active": Module.is_active})
			self.__Data["modules"] = ModulesBuffer
			WriteJSON(f"{self.__Path}/manifest.json", self.__Data)

		except: Status = ERROR_UNKNOWN

		return Status

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class NoteCLI:
	"""CLI записи."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = list()

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("close", "Close note.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete note.")
		Com.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
		CommandsList.append(Com)

		Com = Command("meta", "Manage note metainfo fields.")
		Com.add_argument(ParametersTypes.All, description = "Field name.", important = True)
		Com.add_argument(ParametersTypes.All, description = "Field value.")
		ComPos = Com.create_position("OPERATION", "Type of operation with metainfo.", important = True)
		ComPos.add_flag("set", description = "Create new or update exists field.")
		ComPos.add_flag("del", description = "Remove field.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename note.")
		Com.add_argument(description = "New name.", important = True)
		CommandsList.append(Com)

		Com = Command("view", "View note in console.")
		CommandsList.append(Com)

		return CommandsList + self._GenereateCustomCommands()

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		# Инициализация команд...

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		return Status

	def _View(self) -> ExecutionStatus:
		"""Выводит форматированное представление записи."""

		Status = ExecutionStatus(0)

		try:
			#---> Вывод описания записи.
			#==========================================================================================#
			if self._Note.name: StyledPrinter(self._Note.name, decorations = [Styles.Decorations.Bold], end = False)

			#---> Вывод классификаторов записи.
			#==========================================================================================#

			if self._Note.metainfo:
				StyledPrinter(f"METAINFO:", decorations = [Styles.Decorations.Bold])
				MetaInfo = self._Note.metainfo
				
				for Key in MetaInfo.keys():
					CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
					print(f"    {CustomMetainfoMarker}{Key}: " + str(MetaInfo[Key]))

		except: Status = ERROR_UNKNOWN

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: "Table", note: "Note"):
		"""
		CLI записи.
			driver – драйвер таблиц;\n
			table – объектное представление таблицы;\n
			note – объектное представление записи.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._Driver = driver
		self._Table = table
		self._Note = note

	def execute(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		if parsed_command.name == "clear":
			Clear()

		elif parsed_command.name == "close":
			Status["interpreter"] = "table"

		elif parsed_command.name == "exit":
			exit(0)

		elif parsed_command.name == "delete":
			Response = parsed_command.check_flag("y")
			if not Response: Response = Confirmation(f"Are you sure to delete #{self._Note.id} note?")
			
			if Response:
				Status = self._Table.delete_note(self._Note.id)
				if Status.code == 0: Status["interpreter"] = "table"

		elif parsed_command.name == "meta":
			if parsed_command.check_flag("set"): Status = self._Note.set_metainfo(parsed_command.arguments[0], parsed_command.arguments[1])
			if parsed_command.check_flag("del"): Status = self._Note.remove_metainfo(parsed_command.arguments[0])

		elif parsed_command.name == "rename":
			Status = self._Note.rename(parsed_command.arguments[0])

		elif parsed_command.name == "view":
			self._View()

		else:
			Status = self._ExecuteCustomCommands(parsed_command)

		return Status

class TableCLI:
	"""CLI таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = list()

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("close", "Close table.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete table.")
		Com.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
		CommandsList.append(Com)

		Com = Command("init", "Initialize module.")
		Com.add_argument(description = "Module name.", important = True)
		CommandsList.append(Com)

		Com = Command("list", "Show list of notes.")
		Com.add_flag("r", "Reverse list.")
		Com.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		Com = Command("modules", "List of modules.")
		CommandsList.append(Com)

		Com = Command("new", "Create new note.")
		Com.add_flag("o", "Open new note.")
		CommandsList.append(Com)

		Com = Command("open", "Open note or module.")
		ComPos = Com.create_position("TARGET", "Target for opening.", important = True)
		ComPos.add_argument(description = "Note ID or module name.")
		ComPos.add_flag("m", description = "Open note with max ID.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename table.")
		Com.add_argument(description = "Table name.", important = True)
		CommandsList.append(Com)

		Com = Command("search", "Search notes by part of name.")
		Com.add_argument(description = "Search query.", important = True)
		Com.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		return CommandsList + self._GenereateCustomCommands()

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		# Инициализация команд...

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		return Status

	def _List(self, parsed_command: ParsedCommandData, search: str | None = None) -> ExecutionStatus:
			"""
			Выводит список записей.
				parsed_command – описательная структура команды;\n
				search – поисковый запрос.
			"""

			Status = ExecutionStatus(0)

			try:
				Content = {
					"ID": [],
					"Name": []
				}
				SortBy = None
				IsReverse = parsed_command.check_flag("r")
				Notes = self._Module.notes if self._Module else self._Table.notes

				if parsed_command.check_key("sort"):
					SortBuffer = parsed_command.get_key_value("sort").lower()
					if SortBuffer == "id": SortBy = "ID"
					if SortBuffer == "name": SortBy = "Name"

					if not SortBy:
						Status = ExecutionError(-1, "no_column_to_sort")
						return Status

				if Notes:

					if search:
						print("Search:", TextStyler(search, text_color = Styles.Colors.Yellow))
						NotesCopy = list(Notes)
						SearchBuffer = list()

						for Note in NotesCopy:
							Names = list()
							if Note.name: Names.append(Note.name)

							for Name in Names:
								if search.lower() in Name.lower(): SearchBuffer.append(Note)

						Notes = SearchBuffer
					
					for Note in Notes:
						Name = Note.name if Note.name else ""
						Content["ID"].append(Note.id)
						Content["Name"].append(Name if len(Name) < 60 else Name[:60] + "…")

					if len(Notes): Columns(Content, sort_by = SortBy, reverse = IsReverse)
					else: Status.message = "Notes not found."

				else:
					Status.message = "Table is empty."

			except: Status = ERROR_UNKNOWN

			return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: "Table"):
		"""
		CLI таблицы.
			driver – драйвер таблиц;\n
			table – таблица.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._Driver = driver
		self._Table = table
		self._Module = None

	def execute(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		if parsed_command.name == "clear":
			Clear()

		elif parsed_command.name == "close":
			Status["interpreter"] = "driver"

		elif parsed_command.name == "exit":
			exit(0)

		elif parsed_command.name == "init":
			Status["initialize_module"] = parsed_command.arguments[0]

		elif parsed_command.name == "list":
			Status = self._List(parsed_command)

		elif parsed_command.name == "modules":
			Modules = self._Table.manifest.modules

			if Modules:
				TableData = {
					"Module": [],
					"Status": []
				}

				for Module in Modules:
					ModuleStatus = TextStyler("active", text_color = Styles.Colors.Green) if Module.is_active else TextStyler("inactive", text_color = Styles.Colors.Red)
					TableData["Module"].append(Module.name)
					TableData["Status"].append(ModuleStatus)
				
				Columns(TableData, sort_by = "Module")

			else: Status.message = "No modules in table."

		elif parsed_command.name == "new":
			Status = self._Table.create_note()
			if parsed_command.check_flag("o") and Status.code == 0: Status["open_note"] = Status["note_id"]

		elif parsed_command.name == "open":

			if parsed_command.check_flag("m"):
				NoteID = max(self._Table.notes_id)
				Status["open_note"] = NoteID

			elif parsed_command.arguments[0].isdigit():
				Status["open_note"] = int(parsed_command.arguments[0])

			else:
				Status["open_module"] = parsed_command.arguments[0]
				Status["interpreter"] = "module"

		elif parsed_command.name == "delete":
			Response = parsed_command.check_flag("y")
			if not Response: Response = Confirmation("Are you sure to delete \"" + self._Table.name + "\" table?")
			
			if Response:
				Status = self._Table.delete()

				if Status.code == 0:
					Status.message = "Table deleted."
					Status["interpreter"] = "driver"

		elif parsed_command.name == "rename":
			Status = self._Table.rename(parsed_command.arguments[0])

		elif parsed_command.name == "search":
			Status = self._List(parsed_command, parsed_command.arguments[0])

		else:
			Status = self._ExecuteCustomCommands(parsed_command)

		return Status
	
class ModuleCLI(TableCLI):
	"""CLI модуля."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = list()

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("close", "Close table.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete table.")
		Com.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
		CommandsList.append(Com)

		Com = Command("init", "Initialize module.")
		Com.add_argument(description = "Module name.", important = True)
		CommandsList.append(Com)

		Com = Command("list", "Show list of notes.")
		Com.add_flag("r", "Reverse list.")
		Com.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		Com = Command("open", "Open note or module.")
		ComPos = Com.create_position("TARGET", "Target for opening.", important = True)
		ComPos.add_argument(description = "Note ID or module name.")
		ComPos.add_flag("m", description = "Open note with max ID.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename table.")
		Com.add_argument(description = "Table name.", important = True)
		CommandsList.append(Com)

		return CommandsList + self._GenereateCustomCommands()

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		# Инициализация команд...

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: "Table", module: "Module"):
		"""
		CLI таблицы.
			driver – драйвер таблиц;\n
			table – таблица, к которой привязан модуль;\n
			module – модуль.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._Driver = driver
		self._Table = table
		self._Module = module

	def execute(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		if parsed_command.name == "clear":
			Clear()

		elif parsed_command.name == "close":
			Status["interpreter"] = "table"

		elif parsed_command.name == "exit":
			exit(0)

		elif parsed_command.name == "list":
			Status = self._List(parsed_command)

		elif parsed_command.name == "open":

			if parsed_command.check_flag("m"):
				NoteID = max(self._Module.notes_id)
				Status["open_note"] = NoteID

			else:
				Status["open_note"] = int(parsed_command.arguments[0])

		elif parsed_command.name == "delete":
			Response = parsed_command.check_flag("y")
			if not Response: Response = Confirmation("Are you sure to delete \"" + self._Table.name + "\" table?")
			
			if Response:
				Status = self._Table.delete()
				if Status.code == 0: Status["interpreter"] = "driver"

		else:
			Status = self._ExecuteCustomCommands(parsed_command)

		return Status

#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class Note:
	"""Базовая запись."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	BASE_NOTE = {
		"name": None,
		"metainfo": {}
	}

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> NoteCLI:
		"""Класс-обработчик CLI записи."""

		return self._CLI
	
	@property
	def id(self) -> int:
		"""ID записи."""

		return self._ID
	
	@property
	def metainfo(self) -> dict:
		"""Метаданные."""

		return self._Data["metainfo"]

	@property
	def name(self) -> str | None:
		"""Название записи."""

		return self._Data["name"]

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GeneratePath(self) -> str:
		"""Генерирует путь к файлу записи."""

		Path = None
		if self._Table.is_module: Path = f"{self._Table.storage}/{self._Table.table.name}/{self._Table.name}/{self._ID}.json"
		else: Path = f"{self._Table.storage}/{self._Table.name}/{self._ID}.json"

		return Path

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._CLI = NoteCLI

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "Table", note_id: int):
		"""
		Базовая запись.
			table – таблица;\n
			note_id – ID записи.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._Table = table
		self._ID = note_id
		self._Path = self.__GeneratePath()
		self._Data = ReadJSON(self._Path)
		self._CLI = None

		#---> Пост-процессинг.
		#==========================================================================================#
		self._PostInitMethod()

	def remove_metainfo(self, key: str) -> ExecutionStatus:
		"""
		Удаляет поле метаданных.
			key – ключ поля.
		"""

		Status = ExecutionStatus(0)

		try:
			del self._Data["metainfo"][key]
			self.save()
			Status.message = "Metainfo field removed."

		except: Status = ERROR_UNKNOWN

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает запись.
			name – название записи.
		"""

		Status = ExecutionStatus(0)

		try:
			self._Data["name"] = name
			self.save()
			Status.message = "Note renamed."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def save(self) -> ExecutionStatus:
		"""Сохраняет запись."""

		Status = ExecutionStatus(0)

		try:
			WriteJSON(self._Path, self._Data)

		except: Status = ERROR_UNKNOWN

		return Status

	def set_metainfo(self, key: str, data: str) -> ExecutionStatus:
		"""
		Задаёт значение поля метаданных.
			key – ключ поля;\n
			data – значение.
		"""

		Status = ExecutionStatus(0)

		try:
			Rules = self._Table.manifest.metainfo_rules
			if key in Rules.fields and Rules[key] and data not in Rules[key]: raise MetainfoBlocked()
			self._Data["metainfo"][key] = data
			self._Data["metainfo"] = dict(sorted(self._Data["metainfo"].items()))
			self.save()
			Status.message = "Metainfo field updated."

		except MetainfoBlocked: Status = NOTE_ERROR_METAINFO_BLOCKED
		except: Status = ERROR_UNKNOWN

		return Status

class Table:
	"""Базовая таблица."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "table"
	MANIFEST: dict = {
		"object": "table",
		"type": TYPE,
		"modules": [],
		"common": {
			"recycle_id": True
		},
		"metainfo_rules": {},
		"viewer": {},
		"custom": {}
	}

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> TableCLI:
		"""Класс-обработчик CLI таблицы."""

		return self._CLI

	@property
	def is_module(self) -> bool:
		"Указывает, является ли таблица модулем."

		return self._IsModule

	@property
	def manifest(self) -> Manifest:
		"""Манифест таблицы."""

		return self._Manifest

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self._Name

	@property
	def notes(self) -> list[Note]:
		"""Список записей."""

		return self._Notes.values()
	
	@property
	def notes_id(self) -> list[int]:
		"""Список ID записей."""

		return self._Notes.keys()

	@property
	def storage(self) -> str:
		"""Путь к хранилищу таблиц."""

		return self._StorageDirectory

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GenerateNewID(self, id_list: list[int]) -> int:
		"""
		Генерирует новый ID.
			id_list – список существующих ID.
		"""

		NewID = None
		if type(id_list) != list: id_list = list(id_list)

		if self.manifest.common.recycle_id:

			for ID in range(1, len(id_list) + 1):

				if ID not in id_list:
					NewID = ID
					break

		if not NewID: NewID = int(max(id_list)) + 1 if len(id_list) > 0 else 1

		return NewID

	def _GetNotesID(self) -> list[int]:
		"""Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON."""

		ListID = list()
		Files = os.listdir(self._Path)
		Files = list(filter(lambda File: File.endswith(".json"), Files))

		for File in Files: 
			if not File.replace(".json", "").isdigit(): Files.remove(File)

		for File in Files: ListID.append(int(File.replace(".json", "")))
		
		return ListID

	def _ReadNote(self, note_id: int):
		"""
		Считывает содержимое записи.
			note_id – идентификатор записи.
		"""

		self._Notes[note_id] = self._Note(self, note_id)

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostCreateMethod(self):
		"""Метод, выполняющийся после создания таблицы."""

		pass

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = Note
		self._CLI = TableCLI

	def _PostOpenMethod(self):
		"""Метод, выполняющийся после чтения данных таблицы."""

		pass

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, storage: str, name: str):
		"""
		Базовая таблица.
			storage_path – директория хранения таблиц;\n
			name – название таблицы.
		"""
		
		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._StorageDirectory = NormalizePath(storage)
		self._Name = name
		self._Path = f"{self._StorageDirectory}/{name}"
		self._Notes = dict()
		self._Manifest = None
		self._IsModule = False
		self._Note = None
		self._CLI = None

		#---> Пост-процессинг.
		#==========================================================================================#
		self._PostInitMethod()

	def create(self) -> ExecutionStatus:
		"""Создаёт таблицу."""

		Status = ExecutionStatus(0)

		try:
			if not os.path.exists(self._Path): os.makedirs(self._Path)
			WriteJSON(f"{self._Path}/manifest.json", self.MANIFEST)
			self._PostCreateMethod()

		except: Status = ERROR_UNKNOWN

		return Status

	def create_note(self) -> ExecutionStatus:
		"""Создаёт запись."""

		Status = ExecutionStatus(0)

		try:
			ID = self._GenerateNewID(self._Notes.keys())
			WriteJSON(f"{self._Path}/{ID}.json", self._Note.BASE_NOTE)
			self._ReadNote(ID)
			Status["note_id"] = ID
			Status.message = f"Note #{ID} created."

		except ZeroDivisionError: Status = ERROR_UNKNOWN

		return Status

	def delete(self) -> ExecutionStatus:
		"""Удаляет таблицу."""

		Status = ExecutionStatus(0)

		try:
			shutil.rmtree(self._Path)

		except FileNotFoundError: Status = DRIVER_ERROR_NO_TABLE

		return Status

	def delete_note(self, note_id: int) -> ExecutionStatus:
		"""
		Удаляет запись из таблицы. 
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus(0)

		try:
			note_id = int(note_id)
			del self._Notes[note_id]
			os.remove(f"{self._Path}/{note_id}.json")
			Status.message = f"Note #{note_id} deleted."

		except KeyError: Status = TABLE_ERROR_MISSING_NOTE
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
			if note_id in self._Notes.keys(): Status.value = self._Notes[note_id]
			else: Status = TABLE_ERROR_MISSING_NOTE

		except: Status = ERROR_UNKNOWN

		return Status

	def open(self) -> ExecutionStatus:
		"""Загружает данные таблицы."""

		Status = ExecutionStatus(0)

		try:
			self._Manifest = Manifest(self._Path, ReadJSON(f"{self._Path}/manifest.json"))
			ListID = self._GetNotesID()
			for ID in ListID: self._ReadNote(ID)
			self._PostOpenMethod()

		except: Status = ERROR_UNKNOWN

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		Status = ExecutionStatus(0)

		try:
			OldPath = self._Path
			NewPath = self._Path.split("/")
			NewPath[-1] = name
			NewPath =  "/".join(NewPath)
			os.rename(OldPath, NewPath)
			self._Path = NewPath
			self._Name = name
			Status.message = "Table renamed."

		except: Status = ERROR_UNKNOWN

		return Status
	
class Module(Table):
	"""Базовый модуль."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "module"
	MANIFEST: dict = {
		"object": "module",
		"type": TYPE,
		"common": {
			"recycle_id": True
		},
		"metainfo_rules": {},
		"viewer": {},
		"custom": {}
	}

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def table(self) -> Table:
		"""Таблица, к которой привязан модуль."""

		return self._Table
	
	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ReadNote(self, note_id: int):
		"""
		Считывает содержимое записи.
			note_id – идентификатор записи.
		"""

		self._Notes[note_id] = self._Note(self, note_id)

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostCreateMethod(self):
		"""Метод, выполняющийся после создания таблицы."""

		pass

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = Note
		self._CLI = ModuleCLI

	def _PostOpenMethod(self):
		"""Метод, выполняющийся после чтения данных таблицы."""

		pass

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, storage: str, table: Table, name: str):
		"""
		Базовый модуль.
			storage_path – директория хранения таблиц;\n
			table – таблица, к которой привязан модуль;\n
			name – название таблицы.
		"""
		
		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._StorageDirectory = NormalizePath(storage)
		self._Table = table
		self._Name = name
		self._Path = f"{self._StorageDirectory}/{table.name}/{name}"
		self._Notes = dict()
		self._Manifest = None
		self._IsModule = True
		self._Note = None
		self._CLI = None

		#---> Пост-процессинг.
		#==========================================================================================#
		self._PostInitMethod()