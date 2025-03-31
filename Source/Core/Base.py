from Source.Core.Bus import ExecutionStatus
from Source.CLI.Templates import Columns
from Source.Core.Messages import Errors
from Source.Core.Exceptions import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.Methods.Filesystem import NormalizePath, ReadJSON, WriteJSON
from dublib.CLI.TextStyler import Styles, TextStyler 
from dublib.CLI.Templates import Confirmation

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
	def count(self) -> int:
		"""Количество вложений."""

		Count = 0
		if os.path.exists(self.__Path): Count = len(os.listdir(self.__Path))

		return Count

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
# >>>>> МЕНЕДЖЕР СВЯЗЕЙ <<<<< #
#==========================================================================================#

class TableBinds:
	"""Табличные связи записей."""

	def __init__(self, table: "Table | Module"):
		"""
		Табличные связи записей.
			table – родительская таблица.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Table = table

		self.__Path = f"{self.__Table.path}/binds.json"
		self.__Data = dict()

		if os.path.exists(self.__Path): self.__Data = ReadJSON(self.__Path)

	def bind_note(self, parent_note_id: int, child_note_id: int) -> ExecutionStatus:
		"""
		Привязывает к родительской записи дочернюю.
			parent_note_id – ID записи, к которой выполняется привязка;\n
			child_note_id – ID записи, которую привязывают.
		"""

		Status = ExecutionStatus()

		if child_note_id not in self.__Table.notes_id:
			Status.push_error(Errors.Table.NO_NOTE)
			return Status

		Binds = list(self.get_binded_notes_id(parent_note_id))
		Binds.append(child_note_id)
		Binds = tuple(set(Binds))
		self.__Data[str(parent_note_id)] = Binds
		self.save()

		return Status

	def fix_bindings(self, note_id: int, new_note_id: int, save: bool = False):
		"""
		Заменяет все вхождения ID записи на новый ID.
			note_id – текущий ID записи;\n
			new_note_id – новый ID записи;\n
			save – выполнить автоматическое сохранение (может привести к ошибке записи JSON, если не все изменения внесены в связи).
		"""

		Data = self.__Data.copy()

		for NoteID in Data.keys():
			if str(note_id) == NoteID:
				self.__Data[str(new_note_id)] = self.__Data[NoteID]
				del self.__Data[NoteID]

		Data = self.__Data.copy()

		for NoteID in Data.keys():
			if note_id in self.__Data[NoteID]: self.__Data[NoteID] = [new_note_id if ID == note_id else ID for ID in self.__Data[NoteID]]

		if save: self.save()

	def get_binded_notes(self, note_id: int) -> tuple["Note"]:
		"""
		Возвращает объекты привязанных записей.
			note_id – ID записи, для которой запрашиваются связанные объекты.
		"""

		Binds = self.get_binded_notes_id(note_id)
		BindsObjects = list()
		
		for NoteID in Binds: BindsObjects.append(self.__Table.get_note(NoteID).value)

		return tuple(BindsObjects)

	def get_binded_notes_id(self, note_id: int) -> tuple[int]:
		"""
		Возвращает последовательность ID привязанных записей.
			note_id – ID записи, для которой запрашиваются связи.
		"""

		Binds = tuple()

		for ParentNoteID in self.__Data.keys():

			if int(ParentNoteID) == note_id:
				Binds = tuple(self.__Data[ParentNoteID])
				break

		if Binds: Binds = tuple(sorted(Binds))

		return Binds
	
	def remove_binding(self, parent_note_id: int, child_note_id: int):
		"""
		Удаляет привязку дочерней записи.
			parent_note_id – ID записи, у которой удаляется привязка;\n
			child_note_id – ID записи, привязку которой удаляют.
		"""

		Binds = list(self.get_binded_notes_id(parent_note_id))
		try: Binds.remove(child_note_id)
		except ValueError: pass
		if Binds: self.__Data[str(parent_note_id)] = Binds
		else: del self.__Data[str(parent_note_id)]
		self.save()

	def save(self):
		"""Сохраняет табличные связи в JSON."""

		if not self.__Data and os.path.exists(self.__Path):
			os.remove(self.__Path)

		else:
			WriteJSON(self.__Path, self.__Data)

class Binder:
	"""Менеджер связей объектов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def general(self) -> None:
		"""Глобальные связи объектов."""

		return self.__General
	
	@property
	def local(self) -> TableBinds:
		"""Табличные связи записей."""

		return self.__Local

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "Table | Module"):
		"""
		Менеджер связей объектов.
			table – родительская таблица.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Table = table

		self.__General = None
		self.__Local = TableBinds(self.__Table)

#==========================================================================================#
# >>>>> МАНИФЕСТ <<<<< #
#==========================================================================================#

class ColumnsOptions:
	"""Опции отображения колонок таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def important_columns(self) -> list[str]:
		"""Список обязательных колонок."""

		return ["ID", "Name"]

	@property
	def is_available(self) -> bool:
		"""Указывает, доступны ли настройки отображения колонок таблицы."""

		IsAvailable = False
		if len(list(self.__Data.keys())): IsAvailable = True

		return IsAvailable

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest", data: dict):
		"""
		Опции отображения колонок таблицы.
			manifest – манифест таблицы;\n
			data – словарь опций.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Manifest = manifest
		self.__Data: dict[str, bool] = data

		for Column in self.important_columns: self.__Data[Column] = True

	def __getitem__(self, column: str) -> bool | None:
		"""
		Возвращает статус отображения колонки.
			column – название колонки в любом регистре.
		"""

		IsEnabled = None
		if column in self.__Data.keys(): IsEnabled = self.__Data[column]

		return IsEnabled

	def check_column(self, column: str) -> bool:
		"""
		Проверяет, описано ли правило для колонки.
			column – название колонки в любом регистре.
		"""

		return column in self.__Data.keys()
	
	def edit_column_status(self, column: str, status: bool):
		"""
		Проверяет, описано ли правило для колонки.
			column – название колонки в любом регистре;\n
			status – статус опции.
		"""

		if column not in self.__Data.keys(): raise KeyError(column)
		self.__Data[column] = status
		self.__Manifest.save()

	def to_dict(self) -> dict:
		"""Возвращает словарь опций отображения."""

		return self.__Data.copy()

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

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def autoclear(self) -> bool | None:
		"""Указывает, следует ли очищать консоль перед выводом списков и просмотром содержимого."""

		Option = None
		if "autoclear" in self.__Data.keys(): Option = self.__Data["autoclear"]

		return Option
	
	@property
	def colorize(self) -> bool | None:
		"""Указывает, следует ли окрашивать элементы консольного интерфейса."""

		Option = None
		if "colorize" in self.__Data.keys(): Option = self.__Data["colorize"]

		return Option

	@property
	def columns(self) -> ColumnsOptions:
		"""Опции отображения колонок таблицы."""

		return self.__Columns

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest", data: dict):
		"""
		Опции просмоторщика записей.
			manifest – манифест таблицы;\n
			data – словарь опций.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Data = data

		if "columns" not in self.__Data.keys(): self.__Data["columns"] = dict()
		self.__Columns = ColumnsOptions(manifest, self.__Data["columns"])

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
		self.__ViewerOptions = ViewerOptions(self, data["viewer"]) if "viewer" in data.keys() else None
		self.__Custom = CustomOptions(data["custom"]) if "custom" in data.keys() else None

	def save(self) -> ExecutionStatus:
		"""Сохраняет манифест."""

		Status = ExecutionStatus()

		try:
			ModulesBuffer = list()
			for Module in self.__Modules: ModulesBuffer.append({"name": Module.name, "type": Module.type, "is_active": Module.is_active})
			self.__Data["modules"] = ModulesBuffer
			WriteJSON(f"{self.__Path}/manifest.json", self.__Data)
			
		except: Status.push_error(Errors.UNKNOWN)

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

		Com = Command("bind", "Bind another note to this.")
		ComPos = Com.create_position("NOTE_ID", "ID of the binded note.", important = True)
		ComPos.add_argument(ParametersTypes.Number, "Note ID.")
		Com.add_flag("r", "Remove binding if exists.")
		CommandsList.append(Com)

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete note.")
		Com.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
		CommandsList.append(Com)

		Com = Command("meta", "Manage note metainfo fields.")
		Com.add_argument(description = "Field name.", important = True)
		Com.add_argument(description = "Field value.")
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
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
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

		Status = ExecutionStatus()

		return Status

	def _View(self) -> ExecutionStatus:
		"""Выводит форматированное представление записи."""

		Status = ExecutionStatus()

		try:
			#---> Вывод описания.
			#==========================================================================================#
			if self._Note.name: print(TextStyler(self._Note.name).decorate.bold)

			#---> Вывод связей.
			#==========================================================================================#
			
			if self._Note.binded_notes:
				print(TextStyler(f"BINDED NOTES:").decorate.bold)
				
				for Note in self._Note.binded_notes:
					Name = f". {Note.name}" if Note.name else ""
					print(f"    > {Note.id}{Name}")

			#---> Вывод вложений.
			#==========================================================================================#
			Attachments = self._Note.attachments

			if Attachments.slots or Attachments.other:
				print(TextStyler("ATTACHMENTS:").decorate.bold)

				if Attachments.slots != None:
					for Slot in Attachments.slots: print(f"    {Slot}: " + TextStyler(Attachments.get_slot_filename(Slot), decorations = [Styles.Decorations.Italic]))

				if Attachments.other != None:
					for Filename in Attachments.other: print("    " + TextStyler(Filename, decorations = [Styles.Decorations.Italic]))

			#---> Вывод метаданных.
			#==========================================================================================#

			if self._Note.metainfo:
				print(TextStyler(f"METAINFO:").decorate.bold)
				MetaInfo = self._Note.metainfo
				
				for Key in MetaInfo.keys():
					CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
					print(f"    {CustomMetainfoMarker}{Key}: " + str(MetaInfo[Key]))

		except: Status.push_error(Errors.UNKNOWN)

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

		Status = ExecutionStatus()

		if parsed_command.name == "attach":
			Slot = parsed_command.get_key_value("slot")
			Force = parsed_command.check_flag("f")
			Status = self._Note.attach(parsed_command.arguments[0], Slot, Force)

		elif parsed_command.name == "bind":
			if parsed_command.check_flag("r"): self._Note.remove_note_binding(parsed_command.arguments[0])
			else: self._Note.bind_note(parsed_command.arguments[0])

		elif parsed_command.name == "clear":
			Clear()

		elif parsed_command.name == "exit":
			exit(0)

		elif parsed_command.name == "delete":
			Response = parsed_command.check_flag("y")
			if not Response: Response = Confirmation(f"Are you sure to delete #{self._Note.id} note?")
			
			if Response:
				Status = self._Table.delete_note(self._Note.id)
				if Status: Status["interpreter"] = "module" if self._Table.is_module else "table"

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
			if self._Table.manifest.viewer.autoclear: Clear()
			self._View()

		else:
			Status = self._ExecuteCustomCommands(parsed_command)

		return Status

class BaseTableCLI:
	"""Базовый CLI таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def base_commands(self) -> list[Command]:
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

		Com = Command("columns", "Edit columns showing options.")
		ComPos = Com.create_position("OPERATION", "Type of operation for option. If not specified, prints current options.")
		ComPos.add_key("disable", description = "Hide column in list of notes.")
		ComPos.add_key("enable", description = "Show column in list of notes.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete table.")
		Com.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
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

		Com = Command("search", "Search notes by part of name.")
		Com.add_argument(description = "Search query.", important = True)
		Com.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def base_commands_names(self) -> list[str]:
		"""Список названий базовых команд."""

		Names = list()
		for Command in self.base_commands: Names.append(Command.name)

		return Names

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExecuteBaseCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus | None:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""
		
		if parsed_command.name not in self.base_commands_names: return None

		Status = ExecutionStatus()

		if parsed_command.name == "chid":
			Mode = None
			if parsed_command.check_flag("i"): Mode = "i"
			elif parsed_command.check_flag("o"): Mode = "o"
			elif parsed_command.check_flag("s"): Mode = "s"
			Status = self._BaseTable.change_note_id(parsed_command.arguments[0], parsed_command.arguments[1], Mode)

		elif parsed_command.name == "clear":
			Clear()

		elif parsed_command.name == "columns":
			
			if parsed_command.check_key("disable"):
				ColumnName = parsed_command.get_key_value("disable")
				Status = self._BaseTable.edit_column_status(ColumnName, False)

			elif parsed_command.check_key("enable"):
				ColumnName = parsed_command.get_key_value("enable")
				Status = self._BaseTable.edit_column_status(ColumnName, True)

			else:
				Data = self._BaseTable.manifest.viewer.columns.to_dict()
				TableData = {
						"Column": [],
						"Status": []
					}
				
				for Name in Data.keys():
					ColumnStatus = Data[Name]
					ColumnStatus = TextStyler("enabled").colorize.green if ColumnStatus else TextStyler("disabled").colorize.red
					TableData["Column"].append(Name)
					TableData["Status"].append(ColumnStatus)

				Columns(TableData, sort_by = "Column")

		elif parsed_command.name == "exit":
			exit(0)

		elif parsed_command.name == "list":
			Status = self._List(parsed_command)

		elif parsed_command.name == "new":
			Status = self._BaseTable.create_note()
			if parsed_command.check_flag("o") and Status: Status["open_note"] = Status["note_id"]

		elif parsed_command.name == "open":

			if parsed_command.check_flag("m"):
				NoteID = max(self._BaseTable.notes_id)
				Status["open_note"] = NoteID

			elif parsed_command.arguments[0].isdigit():
				Status["open_note"] = int(parsed_command.arguments[0])

			else:
				Status["open_module"] = parsed_command.arguments[0]
				Status["interpreter"] = "module"

		elif parsed_command.name == "delete":
			Response = parsed_command.check_flag("y")
			if not Response: Response = Confirmation("Are you sure to delete \"" + self._BaseTable.name + "\" table?")
			
			if Response:
				Status = self._BaseTable.delete()

				if not Status.has_errors and self._Module:
					Status.push_message("Module deleted.")
					Status["interpreter"] = "table"

				else:
					Status.push_message("Table deleted.")
					Status["interpreter"] = "driver"

		elif parsed_command.name == "rename":
			Status = self._BaseTable.rename(parsed_command.arguments[0])

		elif parsed_command.name == "search":
			Status = self._List(parsed_command, parsed_command.arguments[0])
		
		return Status

	def _List(self, parsed_command: ParsedCommandData, search: str | None = None) -> ExecutionStatus:
			"""
			Выводит список записей.
				parsed_command – описательная структура команды;\n
				search – поисковый запрос.
			"""

			Status = ExecutionStatus()

			try:
				Content = dict()
				SortBy = parsed_command.check_key("sort") or "ID"
				IsReverse = parsed_command.check_flag("r")
				for Column in self._BaseTable.manifest.viewer.columns.to_dict().keys(): Content[Column] = list()
				Notes: list["Note"] = self._Module.notes if self._Module else self._Table.notes

				if SortBy not in Content.keys():
						Status.push_error("no_column_to_sort")
						return Status

				if not Notes:
					Status.push_message("Table is empty.")
					return Status 
				
				if self._BaseTable.manifest.viewer.autoclear: Clear()
				
				if search:
					print("Search:", TextStyler(search).colorize.yellow)
					Notes = [Note for Note in Notes if any(search.lower() in Variant.lower() for Variant in Note.searchable)]
				
				for Note in Notes: Content = self._AddRowToTableContent(Content, Note)

				if Notes:

					for ColumnName in list(Content.keys()):
						if self._BaseTable.manifest.viewer.columns[ColumnName] == False: del Content[ColumnName]

					Columns(Content, SortBy, IsReverse)

				else: Status.push_message("Notes not found.")

			except ZeroDivisionError: Status.push_error(Errors.UNKNOWN)

			return Status

	def _AddRowToTableContent(self, content: dict[str, list], note: "Note") -> dict[str, list]:
		"""
		Добавляет строчку в таблицу и выполняет проверки содержимого.
			content – содержимое таблицы;\n
			row – данные строчки.
		"""

		Row = self._BuildNoteRow(note)

		for Column in content.keys():
			Data = ""
			if Column in Row.keys() and Row[Column] != None: Data = Row[Column]
			if Column == "Name": Data = Data if len(Data) < 60 else Data[:60] + "…"
			content[Column].append(Data)

		return content

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _BuildNoteRow(self, note: "Note") -> dict[str, str]:
		"""
		Строит строку описания записи для таблицы и возвращает словарь в формате: название колонки – данные.
			note – обрабатываемая запись.
		"""

		Row = dict()
		Row["ID"] = note.id
		Row["Name"] = note.name

		return Row

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

		Status = ExecutionStatus()

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: "Table", module: "Module | None" = None):
		"""
		Базовый CLI таблицы.
			driver – драйвер таблиц;\n
			table – таблица;\n
			module – модуль.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._Driver = driver
		self._Table = table
		self._Module = module

		self._BaseTable = module if module else table

class TableCLI(BaseTableCLI):
	"""CLI таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = list()

		Com = Command("init", "Initialize module.")
		Com.add_argument(description = "Module name.", important = True)
		CommandsList.append(Com)

		Com = Command("modules", "List of modules.")
		CommandsList.append(Com)

		return self.base_commands + CommandsList + self._GenereateCustomCommands()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def execute(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()

		if parsed_command.name == "init":
			Modules = self._Table.manifest.modules

			if Modules:
				Type = None

				for Module in Modules:
					if Module.name == parsed_command.arguments[0]: Type = Module.type

				if Type: Status["initialize_module"] = Type
				else: Status = DRIVER_ERROR_NO_TYPE

			else: Status = DRIVER_ERROR_NO_MODULES_IN_TABLE

			Status["initialize_module"] = parsed_command.arguments[0]

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

			else: Status.push_message("No modules in table.")

		else:
			Status = self._ExecuteBaseCommands(parsed_command)
			if Status == None: Status = self._ExecuteCustomCommands(parsed_command)

		return Status
	
class ModuleCLI(TableCLI):
	"""CLI модуля."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		return self.base_commands + self._GenereateCustomCommands()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def execute(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()
		Status = self._ExecuteBaseCommands(parsed_command)
		if Status == None: Status = self._ExecuteCustomCommands(parsed_command)

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
	def binded_notes(self) -> tuple["Note"]:
		"""Связанные записи."""

		return self._Table.binder.local.get_binded_notes(self._ID)

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
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def searchable(self) -> list[str]:
		"""Список строк, которые представляют контент для поисковых запросов."""

		Strings = list()

		Strings.append(self._Data["name"])
		if "localized_name" in self._Data.keys(): Strings.append(self._Data["localized_name"])
		if "another_name" in self._Data.keys() and type(self._Data["another_name"]) == str: Strings.append(self._Data["another_name"])
		if "another_names" in self._Data.keys() and type(self._Data["another_names"]) == list: Strings += self._Data["another_names"]

		Strings = list(filter(lambda Element: bool(Element), Strings))

		return Strings

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
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
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

		Status = ExecutionStatus()

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
				Status.push_message(f"File \"{path}\" attached to #{self._ID} note on slot \"{slot}\".")

			else:
				AttachmentsObject.attach(path, force)
				Status.push_message(f"File \"{path}\" attached to #{self._ID} note.")

			self._Data["attachments"] = AttachmentsObject.dictionary
			self.save()
			
		except AttachmentsDenied:
			if slot: Status = NOTE_ERROR_SLOT_ATTACHMENTS_DENIED
			else: Status = NOTE_ERROR_OTHER_ATTACHMENTS_DENIED

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def bind_note(self, note_id: int) -> ExecutionStatus:
		"""Привязывает другую запись к текущей."""

		Status = self._Table.binder.local.bind_note(self.id, note_id)

		return Status

	def remove_metainfo(self, key: str) -> ExecutionStatus:
		"""
		Удаляет поле метаданных.
			key – ключ поля.
		"""

		Status = ExecutionStatus()

		try:
			del self._Data["metainfo"][key]
			self.save()
			Status.push_message("Metainfo field removed.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def remove_note_binding(self, note_id: int) -> ExecutionStatus:
		"""Удаляет привязку записи к текущей."""

		Status = ExecutionStatus()
		self._Table.binder.local.remove_binding(self.id, note_id)

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает запись.
			name – название записи.
		"""

		Status = ExecutionStatus()

		try:
			self._Data["name"] = name
			self.save()
			Status.push_message("Note renamed.")

		except:
			Status.push_error(Errors.UNKNOWN)

		return Status

	def save(self) -> ExecutionStatus:
		"""Сохраняет запись."""

		Status = ExecutionStatus()

		try: WriteJSON(self._Path, self._Data)
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_id(self, id: int) -> ExecutionStatus:
		"""
		Задаёт новое значение ID.
			id – идентификатор.
		"""

		Status = ExecutionStatus()

		try:
			
			OldPath = self._Path
			self._Path = self.__GeneratePath(f"{id}.json")
			os.rename(OldPath, self._Path)
			
			if self.attachments.count > 0:
				OldPath = self.__GeneratePath(f".attachments/{self._ID}")
				NewPath = self.__GeneratePath(f".attachments/{id}")
				shutil.move(OldPath, NewPath)

			self._Table.binder.local.fix_bindings(self._ID, id, save = True)
			self._ID = id

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_metainfo(self, key: str, data: str) -> ExecutionStatus:
		"""
		Задаёт значение поля метаданных.
			key – ключ поля;\n
			data – значение.
		"""

		Status = ExecutionStatus()

		try:
			Rules = self._Table.manifest.metainfo_rules
			if key in Rules.fields and Rules[key] and data not in Rules[key]: raise MetainfoBlocked()
			if data.isdigit(): data = int(data)
			self._Data["metainfo"][key] = data
			self._Data["metainfo"] = dict(sorted(self._Data["metainfo"].items()))
			self.save()
			Status.push_message("Metainfo field updated.")

		except MetainfoBlocked: Status = NOTE_ERROR_METAINFO_BLOCKED
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def unattach(self, filename: str | None = None, slot: str | None = None) -> ExecutionStatus:
		"""
		Удаляет вложение по имени файла или слоту.
			filename – имя файла;\n
			slot – слот.
		"""

		Status = ExecutionStatus()

		if not filename and not slot:
			Status.push_error("no_filename_or_slot_to_unattach")
			return Status

		try:
			Path = self.__GeneratePath(point = f".attachments/{self._ID}")
			AttachmentsData = self._Data["attachments"] if "attachments" in self._Data.keys() else None
			AttachmentsObject = Attachments(Path, AttachmentsData)

			if filename:
				AttachmentsObject.unattach(filename)
				Status.push_message(f"File \"{filename}\" unattached.")

			else: 
				AttachmentsObject.clear_slot(slot)
				Status.push_message(f"Attachment slot \"{slot}\" cleared.")

			self._Data["attachments"] = AttachmentsObject.dictionary
			self.save()

			AttachmentsDirectory = self.__GeneratePath(point = ".attachments")
			if not os.listdir(AttachmentsDirectory): os.rmdir(AttachmentsDirectory)

		except: Status.push_error(Errors.UNKNOWN)

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
		"common": {
			"recycle_id": True,
			"attachments": False
		},
		"metainfo_rules": {},
		"viewer": {
			"autoclear": False,
			"colorize": True,
			"columns": {}
		},
		"custom": {}
	}

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def binder(self) -> Binder:
		"""Менеджер связей объектов."""

		return self._Binder

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
	def path(self) -> str:
		"""Путь к директории таблицы."""

		return self._Path

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
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
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
		self._Notes: dict[int, Note] = dict()
		self._Manifest = None
		self._Binder = Binder(self)
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

		Status = ExecutionStatus()
		IsTargetNoteExists = new_id in self._Notes.keys()
		
		if note not in self._Notes.keys():
			Status.push_error(Errors.Table.NO_NOTE)
			Status["print"] = note
			return Status

		if IsTargetNoteExists and not mode:
			Status.push_error("Table.ERROR_NOTE_ALREADY_EXISTS")
			return Status
		
		if mode not in [None, "i", "o", "s"]:
			Status.push_error("Table.UNKNOWN_CHID_MODE")
			return Status
		
		if IsTargetNoteExists:
			
			if mode == "i":
				self.change_note_id(note, 0)
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

				for ID in NotesID: Status = self.change_note_id(ID, ID + 1)
				if Status.has_errors: return Status
				Status = self.change_note_id(0, new_id)
				if Status.has_errors: return Status
				Status.push_message(f"Note #{note} inserted to position #{new_id}.")

			elif mode == "o":
				self.delete_note(new_id)
				self._Notes[note].set_id(new_id)
				Status.push_message(f"Note #{new_id} overwritten.")

			elif mode == "s":
				self._Notes[0] = self._Notes[new_id]
				self._Notes[0].set_id(0)

				self._Notes[new_id] = self._Notes[note]
				self._Notes[new_id].set_id(new_id)
				
				self._Notes[note] = self._Notes[0]
				self._Notes[note].set_id(note)

				del self._Notes[0]

				Status.push_message(f"Note #{note} and #{new_id} swiped.")

		else:
			self._Notes[new_id] = self._Notes[note]
			self._Notes[new_id].set_id(new_id)
			del self._Notes[note]
			Status.push_message(f"Note #{note} changed ID to #{new_id}.")

		return Status

	def create(self) -> ExecutionStatus:
		"""Создаёт таблицу."""

		Status = ExecutionStatus()

		try:

			if not os.path.exists(self._Path):
				os.makedirs(self._Path)

			else:
				Status.push_error(Errors.Driver.TABLE_ALREADY_EXISTS)
				return Status

			WriteJSON(f"{self._Path}/manifest.json", self.MANIFEST)
			self._PostCreateMethod()
			Status.value = self

		except: Status.print_messages(Errors.UNKNOWN)

		return Status

	def create_note(self) -> ExecutionStatus:
		"""Создаёт запись."""

		Status = ExecutionStatus()

		try:
			ID = self._GenerateNewID(self._Notes.keys())
			BaseNoteStruct = self._Note.BASE_NOTE.copy()
			if self.manifest.common.is_attachments_enabled: BaseNoteStruct["attachments"] = {"slots": {}, "other": []}
			WriteJSON(f"{self._Path}/{ID}.json", BaseNoteStruct)
			self._ReadNote(ID)
			Status.emit_navigate_signal(ID)
			Status.push_message(f"Note #{ID} created.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def delete(self) -> ExecutionStatus:
		"""Удаляет таблицу."""

		Status = ExecutionStatus()

		try: shutil.rmtree(self._Path)
		except FileNotFoundError: Status.push_error(Errors.Driver.PATH_NOT_FOUND)

		return Status

	def delete_note(self, note_id: int) -> ExecutionStatus:
		"""
		Удаляет запись из таблицы. 
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus()

		try:
			note_id = int(note_id)
			del self._Notes[note_id]
			os.remove(f"{self._Path}/{note_id}.json")
			Status.emit_close_signal()
			Status.push_message(f"Note #{note_id} deleted.")

		except KeyError: Status = Errors.Table.NO_NOTE
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def edit_column_status(self, column: str, status: bool) -> ExecutionStatus:
		"""
		Переключает отображение колонки при просмотре списка записей.
			column – название колонки в любом регистре;\n
			status – статус отображения.
		"""

		Status = ExecutionStatus()
		Columns = self._Manifest.viewer.columns

		if Columns.is_available:
			
			if Columns.check_column(column):
				Columns.edit_column_status(column, status)
				Status.push_message("Column status changed.")

			else:
				ColumnBold = TextStyler(column).decorate.bold
				Status = ExecutionWarning(1, f"Option for {ColumnBold} not available or column missing")

		else: Status.push_message("Colums options not available for this table.")

		return Status

	def get_note(self, note_id: int) -> ExecutionStatus:
		"""
		Возвращает запись.
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus()

		try:
			note_id = int(note_id)
			if note_id in self._Notes.keys(): Status.value = self._Notes[note_id]
			else: Status.push_error(Errors.Table.NO_NOTE)

		except ValueError: Status.push_error(Errors.Table.INCORRECT_NOTE_ID)
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def open(self) -> ExecutionStatus:
		"""Загружает данные таблицы."""

		Status = ExecutionStatus()

		try:
			self._Manifest = Manifest(self._Path, ReadJSON(f"{self._Path}/manifest.json"))
			ListID = self._GetNotesID()
			for ID in ListID: self._ReadNote(ID)
			AttachmentsDirectory = f"{self._Path}/.attachments"
			if not os.path.exists(AttachmentsDirectory) and self._Manifest.common.is_attachments_enabled: os.makedirs(AttachmentsDirectory)
			if os.path.exists(AttachmentsDirectory) and not os.listdir(AttachmentsDirectory): os.rmdir(AttachmentsDirectory)
			self._PostOpenMethod()
			Status.value = self

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		Status = ExecutionStatus()

		try:
			OldPath = self._Path
			NewPath = self._Path.split("/")
			NewPath[-1] = name
			NewPath =  "/".join(NewPath)
			os.rename(OldPath, NewPath)
			self._Path = NewPath
			self._Name = name
			Status.push_message("Table renamed.")

		except: Status.push_error(Errors.UNKNOWN)

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
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
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
		self._Binder = Binder(self)
		self._IsModule = True
		self._Note = None
		self._CLI = None

		#---> Пост-процессинг.
		#==========================================================================================#
		self._PostInitMethod()