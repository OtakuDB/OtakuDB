from .Templates import Columns

from Source.Core.Bus import ExecutionStatus
from Source.Core.Messages import Errors
from Source.Core.Exceptions import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.TextStyler import Codes, FastStyler, TextStyler
from dublib.CLI.Templates import Confirmation
from dublib.Methods.System import Clear

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from Source.Core.Base.Objects import Table, Module, Note
	from Source.Core.Driver import Driver

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class NoteCLI:
	"""Интерпретатор интерфейса записи: CLI."""

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
		Com.base.add_flag("f", "Enable attachments overwrite.")
		Com.base.add_key("slot", ParametersTypes.Text, "Name of slot for attachment.")
		CommandsList.append(Com)

		Com = Command("bind", "Bind another note to this.")
		ComPos = Com.create_position("NOTE", "Target note for binding.", important = True)
		ComPos.add_argument(description = "Note identificator in module-id format.")
		Com.base.add_flag("r", "Remove binding if exists.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete note.")
		Com.base.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("meta", "Manage note metainfo fields.", category = "Metainfo")
		Com.base.add_argument(description = "Field name.", important = True)
		Com.base.add_argument(description = "Field value.")
		ComPos = Com.create_position("OPERATION", "Type of operation with metainfo.", important = True)
		ComPos.add_flag("set", description = "Create new or update exists field.")
		ComPos.add_flag("del", description = "Remove field.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename note.")
		Com.base.add_argument(description = "New name.", important = True)
		CommandsList.append(Com)

		Com = Command("slots", "Print slots info.")
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

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()

		return Status

	def _PrintAttachments(self):
		"""Выводит вложения."""

		Attachments = self._Note.attachments

		if Attachments.count:
			print(FastStyler("ATTACHMENTS:").decorate.bold)

			for Slot in Attachments.slots:
				print(f"    {Slot}: " + FastStyler(Attachments.get_slot_filename(Slot)).decorate.italic)

	def _PrintMetainfo(self):
		"""Выводит метаданные."""

		if self._Note.metainfo:
			print(FastStyler(f"METAINFO:").decorate.bold)
			MetaInfo = self._Note.metainfo
			
			for Key in MetaInfo.keys():
				Data: str = MetaInfo[Key]
				if Key == "author": Data = Data.replace(";", ", ")
				CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
				print(f"    {CustomMetainfoMarker}{Key}: {Data}")

	def _View(self) -> ExecutionStatus:
		"""Выводит форматированное представление записи."""

		Status = ExecutionStatus()

		try:
			#---> Вывод описания.
			#==========================================================================================#
			if self._Note.name: print(FastStyler(self._Note.name).decorate.bold)

			#---> Вывод связей.
			#==========================================================================================#
			
			if self._Note.binded_notes:
				print(FastStyler(f"BINDED NOTES:").decorate.bold)
				
				for Note in self._Note.binded_notes:
					Name = f". {Note.name}" if Note.name else ""
					print(f"    > {Note.id}{Name}")

			#---> Вывод вложений.
			#==========================================================================================#
			Attachments = self._Note.attachments

			if Attachments.count:
				print(FastStyler("ATTACHMENTS:").decorate.bold)

				if Attachments.slots != None:
					for Slot in Attachments.slots: print(f"    {Slot}: " + FastStyler(Attachments.get_slot_filename(Slot), decorations = Codes.Decorations.Italic))

				if Attachments.other != None:
					for Filename in Attachments.other: print("    " + TextStyler(Filename, decorations = Codes.Decorations.Italic))

			#---> Вывод метаданных.
			#==========================================================================================#

			if self._Note.metainfo:
				print(FastStyler(f"METAINFO:").decorate.bold)
				MetaInfo = self._Note.metainfo
				
				for Key in MetaInfo.keys():
					CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
					print(f"    {CustomMetainfoMarker}{Key}: " + str(MetaInfo[Key]))

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "Table", note: "Note"):
		"""
		Интерпретатор интерфейса записи: CLI.

		:param table: Таблица, к которой привязана запись.
		:type table: Table
		:param note: Запись.
		:type note: Note
		"""

		self._Driver = table.session.driver
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

		elif parsed_command.name == "slots":
			Info = self._Note.slots_info

			if Info:
				TableData = {
					"Slot": list(),
					"Description": list()
				}

				for Slot in Info.keys():
					TableData["Slot"].append(Slot)
					TableData["Description"].append(Info[Slot])

				Columns(TableData, sort_by = "Slot")

			else: print("No slots info.")

		elif parsed_command.name == "unattach":
			Slot = parsed_command.get_key_value("slot")
			Filename = parsed_command.arguments[0] if len(parsed_command.arguments) else None
			Status = self._Note.unattach(Filename, Slot)

		elif parsed_command.name == "view":
			if self._Table.manifest.interfaces_options.cli.autoclear: Clear()
			self._View()
			self._PrintMetainfo()
			self._PrintAttachments()

		else:
			Status = self._ExecuteCustomCommands(parsed_command)

		return Status

class BaseTableCLI:
	"""Интерпретатор интерфейса базовой таблицы: CLI."""

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

		Com = Command("columns", "Edit columns showing options.")
		ComPos = Com.create_position("OPERATION", "Type of operation for option. If not specified, prints current options.")
		ComPos.add_key("disable", description = "Hide column in list of notes.")
		ComPos.add_key("enable", description = "Show column in list of notes.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete table.")
		Com.base.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("new", "Create new note.")
		Com.base.add_flag("o", "Open new note.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename current table or module.")
		Com.base.add_argument(description = "New table or module name.", important = True)
		CommandsList.append(Com)

		Com = Command("search", "Search notes by part of name.")
		Com.base.add_argument(description = "Search query.", important = True)
		Com.base.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		Com = Command("view", "Show list of notes.")
		Com.base.add_flag("r", "Reverse list.")
		Com.base.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def base_commands_names(self) -> tuple[str]:
		"""Список названий базовых команд."""

		return tuple(Command.name for Command in self.base_commands)

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

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

	def _ExecuteBaseCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""
		
		Status = ExecutionStatus()

		if parsed_command.name == "chid":
			Mode = None
			if parsed_command.check_flag("i"): Mode = "i"
			elif parsed_command.check_flag("o"): Mode = "o"
			elif parsed_command.check_flag("s"): Mode = "s"
			Status = self._BaseTable.change_note_id(parsed_command.arguments[0], parsed_command.arguments[1], Mode)

		elif parsed_command.name == "columns":
			
			if parsed_command.check_key("disable"):
				ColumnName = parsed_command.get_key_value("disable")
				Status = self._BaseTable.edit_column_status(ColumnName, False)

			elif parsed_command.check_key("enable"):
				ColumnName = parsed_command.get_key_value("enable")
				Status = self._BaseTable.edit_column_status(ColumnName, True)

			else:
				Data = self._BaseTable.manifest.interfaces_options.cli.columns.to_dict()
				TableData = {
						"Column": [],
						"Status": []
					}
				
				for Name in Data.keys():
					ColumnStatus = Data[Name]
					ColumnStatus = FastStyler("enabled").colorize.green if ColumnStatus else FastStyler("disabled").colorize.red
					TableData["Column"].append(Name)
					TableData["Status"].append(ColumnStatus)

				Columns(TableData, sort_by = "Column")

		elif parsed_command.name == "new":
			Status = self._BaseTable.create_note()
			if parsed_command.check_flag("o") and Status: Status.emit_navigate(Status.value.id)

		elif parsed_command.name == "delete":
			Response = parsed_command.check_flag("y")
			if not Response: Response = Confirmation(f"Are you sure to delete \"{self._BaseTable.name}\" table?")
			
			if Response:
				Status = self._BaseTable.delete()

				if not Status.has_errors:
					Status.push_message("Module deleted." if self._Module else "Table deleted.")
					Status.emit_close()

		elif parsed_command.name == "search":
			Status = self._View(parsed_command, parsed_command.arguments[0])
		
		elif parsed_command.name == "view":
			Status = self._View(parsed_command)

		return Status

	def _View(self, parsed_command: ParsedCommandData, search: str | None = None) -> ExecutionStatus:
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
				for Column in self._BaseTable.manifest.interfaces_options.cli.columns.to_dict().keys(): Content[Column] = list()
				Notes: list["Note"] = self._Module.notes if self._Module else self._Table.notes

				if SortBy not in Content.keys():
						Status.push_error("no_column_to_sort")
						return Status

				if not Notes:
					Status.push_message("Table is empty.")
					return Status 
				
				if self._BaseTable.manifest.interfaces_options.cli.autoclear: Clear()
				
				if search:
					print("Search:", FastStyler(search).colorize.yellow)
					Notes = [Note for Note in Notes if any(search.lower() in Variant.lower() for Variant in Note.searchable)]
				
				for Note in Notes: Content = self._AddRowToTableContent(Content, Note)

				if Notes:

					for ColumnName in list(Content.keys()):
						if self._BaseTable.manifest.interfaces_options.cli.columns[ColumnName] == False: del Content[ColumnName]

					Columns(Content, SortBy, IsReverse)

				else: Status.push_message("Notes not found.")

			except: Status.push_error(Errors.UNKNOWN)

			return Status

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

	def __init__(self, table: "Table", module: "Module | None" = None):
		"""
		Интерпретатор интерфейса базовой таблицы: CLI.

		:param table: Таблица.
		:type table: Table
		:param module: Модуль.
		:type module: Module | None
		"""

		self._Driver = table.session.driver
		self._Table = table
		self._Module = module

		self._BaseTable = module or table

class TableCLI(BaseTableCLI):
	"""Интерпретатор интерфейса таблицы: CLI."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def moduled_commands(self) -> list[Command]:
		"""Список дескрипторов команд для таблицы с модулями."""

		CommandsList = list()

		Com = Command("init", "Initialize module.")
		ComPos = Com.create_position("MODULE", "Module name.", important = True)
		ComPos.add_argument()
		Com.base.add_flag("o", "Open initialized module.")
		CommandsList.append(Com)

		Com = Command("list", "List of modules.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = self.base_commands + self._GenereateCustomCommands()
		if self._Table.manifest.modules: CommandsList += self.moduled_commands

		return CommandsList

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExecuteModuledTableCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды таблицы с модулями.
			parsed_command – описательная структура команды.
		"""
		
		Status = ExecutionStatus()

		if parsed_command.name == "init":
			Modules = self._Table.manifest.modules

			if Modules:
				Type = None

				for Module in Modules:
					if Module.name == parsed_command.arguments[0]: Type = Module.type

				if Type:
					Status.emit_initialize_module(Type)
					if parsed_command.check_flag("o"): Status.emit_navigate(parsed_command.arguments[0])

				else: Status.push_error(Errors.Driver.NO_MODULE_TYPE)

			else: Status.push_error(Errors.Driver.MODULES_NOT_SUPPORTED)

		elif parsed_command.name == "list":
			Modules = self._Table.manifest.modules

			if Modules:
				TableData = {
					"Module": [],
					"Type": [],
					"Status": []
				}

				for Module in Modules:
					ModuleStatus = TextStyler(text_color = Codes.Colors.Green).get_styled_text("active") 
					if not Module.is_active: ModuleStatus = TextStyler(text_color = Codes.Colors.Red).get_styled_text("inactive") 
					TableData["Module"].append(Module.name)
					TableData["Type"].append(FastStyler(Module.type).decorate.italic)
					TableData["Status"].append(ModuleStatus)
				
				Columns(TableData, sort_by = "Module")

			else: Status.push_message("No modules in table.")

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def execute(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()

		if parsed_command.name in self.base_commands_names: Status += self._ExecuteBaseCommands(parsed_command)
		elif self._Table.manifest.modules: Status += self._ExecuteModuledTableCommands(parsed_command)
		else: Status += self._ExecuteCustomCommands(parsed_command)

		return Status
	
class ModuleCLI(BaseTableCLI):
	"""Интерпретатор интерфейса модуля: CLI."""

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

		if parsed_command.name in self.base_commands_names: Status += self._ExecuteBaseCommands(parsed_command)
		else: Status += self._ExecuteCustomCommands(parsed_command)

		return Status