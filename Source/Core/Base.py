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
	def is_active(self) -> bool:
		"""Состояние: активирован ли модуль."""

		return self.__Data["is_active"]

	@property
	def name(self) -> str:
		"""Название модуля."""

		return self.__Data["name"]
	
	@property
	def requirements(self) -> list[str]:
		"""Список зависимостей модуля."""

		return self.__Data["requirements"]

	@property
	def type(self) -> str:
		"""Тип модуля."""

		return self.__Data["type"]

	def __init__(self, data: dict, manifest: "Manifest"):
		"""
		Данные модуля.
			data – словарь описания;\n
			manifest – манифест.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Data = data
		self.__Requirements = list()
		self.__Manifest = manifest

		if "requirements" in self.__Data.keys(): self.__Requirements = self.__Data["requirements"]

	def activate(self):
		"""Активирует модуль."""

		self.__Data["is_active"] = True
		self.__Manifest.save()

	def deactivate(self):
		"""Деактивирует модуль."""

		self.__Data["is_active"] = False
		self.__Manifest.save()

class Attachments:
	"""Вложения."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def dictionary(self) -> dict:
		"""Словарное представление вложений."""

		Dictionary = {"slots": self.__Slots, "other": self.__Other}
		if self.__Slots == None: del Dictionary["slots"]
		if self.__Other == None: del Dictionary["other"]

		return Dictionary

	@property
	def other(self) -> list[str] | None:
		"""Список других вложений."""

		return self.__Other

	@property
	def slots(self) -> list[str] | None:
		"""Список слотов."""

		Slots = self.__Slots.keys() if self.__Slots != None else None

		return Slots

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckDirectoryForEmpty(self):
		"""Проверяет, пустая ли директория, и удаляет её в случае истинности."""

		if not os.listdir(self.__Path): os.rmdir(self.__Path)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, path: str, data: dict):
		"""
		Вложения.
			path – путь к каталогу вложений записи;\n
			data – словарь вложений.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Path = path
		self.__Slots = data["slots"] if "slots" in data.keys() else None
		self.__Other = data["other"] if "other" in data.keys() else None

	def attach(self, path: str, force: bool = False):
		"""
		Прикрепляет файл к записи.
			force – включает перезапись существующего файла.
		"""

		if self.__Other == None: raise AttachmentsDenied(slot = False)
		path = NormalizePath(path)
		Filename = path.split("/")[-1]
		TargetPath = f"{self.__Path}/{Filename}"
		IsFileExists = os.path.exists(TargetPath)
		if IsFileExists and force: os.remove(TargetPath)
		elif IsFileExists: raise FileExistsError(TargetPath)
		self.__Other.append(Filename)
		os.replace(path, TargetPath)

	def attach_to_slot(self, path: str, slot: str, force: bool = False):
		"""
		Помещает файл в слот.
			slot – слот;\n
			force – включает перезапись существующего файла.
		"""

		if self.__Slots == None: raise AttachmentsDenied(slot = True)
		path = NormalizePath(path)
		Filename = path.split("/")[-1]
		TargetPath = f"{self.__Path}/{Filename}"
		IsFileExists = os.path.exists(TargetPath)
		if IsFileExists and force: os.remove(TargetPath)
		elif IsFileExists: raise FileExistsError(TargetPath)
		os.replace(path, f"{self.__Path}/{Filename}")
		self.__Slots[slot] = Filename

	def clear_slot(self, slot: str):
		"""
		Очищает слот.
			slot – слот.
		"""

		if self.check_slot_occupation(slot):
			os.remove(f"{self.__Path}/{self.__Slots[slot]}")
			self.__Slots[slot] = None
			self.__CheckDirectoryForEmpty()

	def check_slot_occupation(self, slot: str) -> bool:
		"""
		Проверяет, занят ли слот файлом.
			slot – слот.
		"""

		if not self.__Slots[slot]: return False

		return True

	def get_slot_filename(self, slot: str) -> str:
		"""
		Возвращает название файла в слоте.
			slot – слот.
		"""

		return self.__Slots[slot]

	def unattach(self, filename: str):
		"""
		Удаляет вложение.
			filename – имя файла.
		"""

		os.remove(f"{self.__Path}/{filename}")
		self.__Other.remove(filename)
		self.__CheckDirectoryForEmpty()

#==========================================================================================#
# >>>>> МАНИФЕСТ <<<<< #
#==========================================================================================#

class CommonOptions:
	"""Общие опции таблицы."""

	@property
	def is_attachments_enabled(self) -> bool:
		"""Указывает, разрешено ли прикреплять файлы к записям."""

		return self.__Data["attachments"]

	@property
	def recycle_id(self) -> bool:
		"""Указывает, необходимо ли занимать освободившиеся ID."""

		return self.__Data["recycle_id"]

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
			for Module in self.__Data["modules"]: Modules.append(ModuleData(Module, self))

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
			for Module in self.__Modules: ModulesBuffer.append({"name": Module.name, "type": Module.type, "is_active": Module.is_active})
			self.__Data["modules"] = ModulesBuffer
			WriteJSON(self.__Path, self.__Data)
			
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

		Com = Command("attach", "Attach files to note.")
		ComPos = Com.create_position("FILE", important = True)
		ComPos.add_argument(ParametersTypes.ValidPath, description = "Path to file.")
		Com.add_flag("f", "Enable attachments overwrite.")
		Com.add_key("slot", ParametersTypes.Text, "Name of slot for attachment.")
		CommandsList.append(Com)

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

		Com = Command("unattach", "Unattach files from note.")
		ComPos = Com.create_position("FILE", important = True)
		ComPos.add_argument(description = "Attachment name.")
		ComPos.add_key("slot", ParametersTypes.Text, "Name of attachment slot.")
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
			#---> Вывод описания.
			#==========================================================================================#
			if self._Note.name: StyledPrinter(self._Note.name, decorations = [Styles.Decorations.Bold])

			#---> Вывод вложений.
			#==========================================================================================#
			Attachments = self._Note.attachments

			if Attachments.slots or Attachments.other:
				StyledPrinter("ATTACHMENTS:", decorations = [Styles.Decorations.Bold])

				if Attachments.slots != None:
					for Slot in Attachments.slots: print(f"    {Slot}: " + TextStyler(Attachments.get_slot_filename(Slot), decorations = [Styles.Decorations.Italic]))

				if Attachments.other != None:
					for Filename in Attachments.other: print("    " + TextStyler(Filename, decorations = [Styles.Decorations.Italic]))

			#---> Вывод метаданных.
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

		if parsed_command.name == "attach":
			Slot = parsed_command.get_key_value("slot")
			Force = parsed_command.check_flag("f")
			Status = self._Note.attach(parsed_command.arguments[0], Slot, Force)

		elif parsed_command.name == "clear":
			Clear()

		elif parsed_command.name == "close":
			Status["interpreter"] = "module" if self._Table.is_module else "table"

		elif parsed_command.name == "exit":
			exit(0)

		elif parsed_command.name == "delete":
			Response = parsed_command.check_flag("y")
			if not Response: Response = Confirmation(f"Are you sure to delete #{self._Note.id} note?")
			
			if Response:
				Status = self._Table.delete_note(self._Note.id)
				if Status.code == 0: Status["interpreter"] = "module" if self._Table.is_module else "table"

		elif parsed_command.name == "meta":
			if parsed_command.check_flag("set"): Status = self._Note.set_metainfo(parsed_command.arguments[0], parsed_command.arguments[1])
			if parsed_command.check_flag("del"): Status = self._Note.remove_metainfo(parsed_command.arguments[0])

		elif parsed_command.name == "rename":
			Status = self._Note.rename(parsed_command.arguments[0])

		elif parsed_command.name == "unattach":
			Slot = parsed_command.get_key_value("slot")
			Filename = parsed_command.arguments[0] if len(parsed_command.arguments) else None
			Status = self._Note.unattach(Filename, Slot)

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

		Com = Command("chid", "Change ID of note.")
		ComPos = Com.create_position("NOTE", important = True)
		ComPos.add_argument(ParametersTypes.Number, "Exists note ID.")
		ComPos = Com.create_position("ID", important = True)
		ComPos.add_argument(ParametersTypes.Number, "New note ID")
		ComPos = Com.create_position("MODE", "Mode of ID changing.")
		ComPos.add_flag("o", "Overwtite exists note.")
		ComPos.add_flag("s", "Swipe with exists note.")
		ComPos.add_flag("i", "Insert to exists note place.")
		CommandsList.append(Com)

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
				SortBy = "ID"
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

			except ZeroDivisionError: Status = ERROR_UNKNOWN

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

		if parsed_command.name == "chid":
			Mode = None
			if parsed_command.check_flag("i"): Mode = "i"
			elif parsed_command.check_flag("o"): Mode = "o"
			elif parsed_command.check_flag("s"): Mode = "s"
			Status = self._Table.change_note_id(parsed_command.arguments[0], parsed_command.arguments[1], Mode)

		elif parsed_command.name == "clear":
			Clear()

		elif parsed_command.name == "close":
			Status["interpreter"] = "driver"

		elif parsed_command.name == "exit":
			exit(0)

		elif parsed_command.name == "init":
			Modules = self._Table.manifest.modules

			if Modules:
				Type = None

				for Module in Modules:
					if Module.name == parsed_command.arguments[0]: Type = Module.type

				if Type: Status["initialize_module"] = Type
				else: Status = DRIVER_ERROR_NO_TYPE

			else: Status = DRIVER_ERROR_NO_MODULES_IN_TABLE

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

		Com = Command("chid", "Change ID of note.")
		ComPos = Com.create_position("NOTE", important = True)
		ComPos.add_argument(ParametersTypes.Number, "Exists note ID.")
		ComPos = Com.create_position("ID", important = True)
		ComPos.add_argument(ParametersTypes.Number, "New note ID")
		ComPos = Com.create_position("MODE", "Mode of ID changing.")
		ComPos.add_flag("o", "Overwtite exists note.")
		ComPos.add_flag("s", "Swipe with exists note.")
		ComPos.add_flag("i", "Insert to exists note place.")
		CommandsList.append(Com)

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

		if parsed_command.name == "chid":
			Mode = None
			if parsed_command.check_flag("i"): Mode = "i"
			elif parsed_command.check_flag("o"): Mode = "o"
			elif parsed_command.check_flag("s"): Mode = "s"
			Status = self._Module.change_note_id(parsed_command.arguments[0], parsed_command.arguments[1], Mode)

		elif parsed_command.name == "clear":
			Clear()

		elif parsed_command.name == "close":
			Status["interpreter"] = "table"

		elif parsed_command.name == "exit":
			exit(0)

		elif parsed_command.name == "list":
			Status = self._List(parsed_command)

		elif parsed_command.name == "new":
			Status = self._Module.create_note()
			if parsed_command.check_flag("o") and Status.code == 0: Status["open_note"] = Status["note_id"]

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
	def attachments(self) -> Attachments:
		"""Данные вложений."""

		AttachmentsData = None
		Path = self.__GeneratePath(point = f".attachments/{self._ID}")
		AttachmentsDictionary = dict()
		if "attachments" in self._Data: AttachmentsDictionary = self._Data["attachments"]
		AttachmentsData = Attachments(Path, AttachmentsDictionary)

		return AttachmentsData

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

	def __GeneratePath(self, point: str | None = None) -> str:
		"""
		Генерирует используемый путь.
			point – добавляемое к пути таблицы значение.
		"""

		Path = None
		if not point: point = ""
		if self._Table.is_module: Path = f"{self._Table.storage}/{self._Table.table.name}/{self._Table.name}/{point}"
		else: Path = f"{self._Table.storage}/{self._Table.name}/{point}"
		Path = NormalizePath(Path)

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
		self._Path = self.__GeneratePath(point = f"{note_id}.json")
		self._Data = ReadJSON(self._Path)
		self._CLI = None

		#---> Пост-процессинг.
		#==========================================================================================#
		self._PostInitMethod()

	def attach(self, path: str, slot: str | None = None, force: bool = False) -> ExecutionStatus:
		"""
		Прикрепляет файл к записи.
			path – путь к файлу;\n
			slot – именной слот для файла;\n
			force – включает режим перезаписи.
		"""

		Status = ExecutionStatus(0)

		try:
			if not self._Table.manifest.common.is_attachments_enabled: return NOTE_ERROR_ATTACHMENTS_BLOCKED
			path = NormalizePath(path)

			if not os.path.exists(path):
				Status = NOTE_ERROR_BAD_ATTACHMENT_PATH
				Status["print"] = path
				return Status
			
			Path = self.__GeneratePath(point = f".attachments/{self._ID}")
			if not os.path.exists(Path): os.makedirs(Path)
			AttachmentsData = self._Data["attachments"] if "attachments" in self._Data.keys() else None
			AttachmentsObject = Attachments(Path, AttachmentsData)

			if slot:
				AttachmentsObject.attach_to_slot(path, slot, force)
				Status.message = f"File \"{path}\" attached to #{self._ID} note on slot \"{slot}\"."

			else:
				AttachmentsObject.attach(path, force)
				Status.message = f"File \"{path}\" attached to #{self._ID} note."

			self._Data["attachments"] = AttachmentsObject.dictionary
			self.save()
			
		except AttachmentsDenied:
			if slot: Status = NOTE_ERROR_SLOT_ATTACHMENTS_DENIED
			else: Status = NOTE_ERROR_OTHER_ATTACHMENTS_DENIED

		except: Status = ERROR_UNKNOWN

		return Status

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

		try: WriteJSON(self._Path, self._Data)
		except: Status = ERROR_UNKNOWN

		return Status

	def set_id(self, id: int) -> ExecutionStatus:
		"""
		Задаёт новое значение ID.
			id – идентификатор.
		"""

		Status = ExecutionStatus(0)

		try:
			self._ID = id
			OldPath = self._Path
			self._Path = self.__GeneratePath()
			os.rename(OldPath, self._Path)
			Status.message = "ID changed."

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
			if data.isdigit(): data = int(data)
			self._Data["metainfo"][key] = data
			self._Data["metainfo"] = dict(sorted(self._Data["metainfo"].items()))
			self.save()
			Status.message = "Metainfo field updated."

		except MetainfoBlocked: Status = NOTE_ERROR_METAINFO_BLOCKED
		except: Status = ERROR_UNKNOWN

		return Status

	def unattach(self, filename: str | None = None, slot: str | None = None) -> ExecutionStatus:
		"""
		Удаляет вложение по имени файла или слоту.
			filename – имя файла;\n
			slot – слот.
		"""

		Status = ExecutionStatus(0)

		if not filename and not slot:
			Status = ExecutionError(-1, "no_filename_or_slot_to_unattach")
			return Status

		try:
			Path = self.__GeneratePath(point = f".attachments/{self._ID}")
			AttachmentsData = self._Data["attachments"] if "attachments" in self._Data.keys() else None
			AttachmentsObject = Attachments(Path, AttachmentsData)

			if filename:
				AttachmentsObject.unattach(filename)
				Status.message = f"File \"{filename}\" unattached."

			else: 
				AttachmentsObject.clear_slot(slot)
				Status.message = f"Attachment slot \"{slot}\" cleared."

			self._Data["attachments"] = AttachmentsObject.dictionary
			self.save()

			AttachmentsDirectory = self.__GeneratePath(point = ".attachments")
			if not os.listdir(AttachmentsDirectory): os.rmdir(AttachmentsDirectory)

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
			"recycle_id": True,
			"attachments": False
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
		self._Notes: list[Note] = dict()
		self._Manifest = None
		self._IsModule = False
		self._Note = None
		self._CLI = None

		#---> Пост-процессинг.
		#==========================================================================================#
		self._PostInitMethod()

	def change_note_id(self, note: int, new_id: int, mode: str | None = None) -> ExecutionStatus:
		"""
		Изменяет ID записи согласно указанному режиму.
			note – ID существующей записи;\n
			new_id – новый ID;\n
			mode – режим: i – вставка, o – перезапись, s – обмен.
		"""

		Status = ExecutionStatus(0)
		IsTargetNoteExists = new_id in self._Notes.keys()
		
		if note not in self._Notes.keys():
			Status = TABLE_ERROR_MISSING_NOTE
			Status["print"] = note
			return Status

		if IsTargetNoteExists and not mode:
			Status = TABLE_ERROR_NOTE_ALREADY_EXISTS
			Status["print"] = new_id
			return Status
		
		if mode not in [None, "i", "o", "s"]:
			Status = ExecutionError(-1, "unknown_mode")
			Status["print"] = mode
			return Status
		
		if IsTargetNoteExists:
			
			if mode == "i":
				NotesID = list(self._Notes.keys())
				NotesID = sorted(NotesID)
				Buffer = list(NotesID)

				for ID in Buffer:
					if ID < new_id: NotesID.remove(ID)

				Buffer = list(NotesID)
				NewBuffer = list()
				IsFirst = True

				for ID in Buffer:

					if ID + 1 in Buffer:
						NewBuffer.append(ID)

					elif IsFirst: 
						NewBuffer.append(ID)
						break

				NotesID = NewBuffer
				if note in NotesID: NotesID.remove(note)
				NotesID.reverse()
				input(NotesID)
				self.change_note_id(note, 0)
				for ID in NotesID:
					Status = self.change_note_id(ID, ID + 1)
					if Status.code != 0: return Status

				self.change_note_id(0, new_id)
				Status.message = f"Note #{note} inserted to position #{new_id}."

			elif mode == "o":
				self.delete_note(new_id)
				self._Notes[note].set_id(new_id)
				Status.message = f"Note #{new_id} overwritten."

			elif mode == "s":
				self._Notes[0] = self._Notes[new_id]
				self._Notes[0].set_id(0)

				self._Notes[new_id] = self._Notes[note]
				self._Notes[new_id].set_id(new_id)
				
				self._Notes[note] = self._Notes[0]
				self._Notes[note].set_id(note)

				del self._Notes[0]

				Status.message = f"Note #{note} and #{new_id} swiped."

		else:
			self._Notes[new_id] = self._Notes[note]
			self._Notes[new_id].set_id(new_id)
			del self._Notes[note]
			Status.message = f"Note #{note} changed ID to #{new_id}."

		return Status

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
			BaseNoteStruct = self._Note.BASE_NOTE.copy()
			if self.manifest.common.is_attachments_enabled: BaseNoteStruct["attachments"] = {"slots": {}, "other": []}
			WriteJSON(f"{self._Path}/{ID}.json", BaseNoteStruct)
			self._ReadNote(ID)
			Status["note_id"] = ID
			Status.message = f"Note #{ID} created."

		except: Status = ERROR_UNKNOWN

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
			AttachmentsDirectory = f"{self._Path}/.attachments"
			if not os.path.exists(AttachmentsDirectory) and self._Manifest.common.is_attachments_enabled: os.makedirs(AttachmentsDirectory)
			if os.path.exists(AttachmentsDirectory) and not os.listdir(AttachmentsDirectory): os.rmdir(AttachmentsDirectory)
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
			name – название модуля.
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