from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from Source.Core.Base.Table import BaseTable
	from Source.Interfaces.CLI import Interface
	from Source.Core.Session import Session

class BaseTableCLI:
	"""Базовый интерпретатор CLI таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def base_commands(self) -> list[Command]:
		"""Список базовых команд контейнера."""

		CommandsList = list()

		Com = Command("close", "Close table.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename table.")
		Com.base.add_argument(description = "New table name.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def commands(self) -> list[Command]:
		"""Полный список команд интерпретатора."""

		return self.base_commands + self._GenerateCustomCommands()
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#



	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExecuteBaseCommand(self, command: ParsedCommandData):
		"""
		Обрабатывает базовую команду.
		
		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		match command.name:
			case "rename": self._Table.rename(command.arguments[0])
			case "close": self._Interface.set_current_object(self._Session.driver.current_box)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExecuteCustomCommand(self, command: ParsedCommandData):
		"""
		Обрабатывает кастомную команду.
		
		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		pass

	def _GenerateCustomCommands(self) -> list[Command]:
		"""
		Возвращает список кастомных команд интерпретатора.

		:return: Возвращает список кастомных команд интерпретатора.
		:rtype: list[Command]
		"""

		CommandsList = list()

		Com = Command("rename", "Change table name.")
		ComPos = Com.create_position("NAME")
		ComPos.add_argument(description = "New table name.")
		CommandsList.append(Com)

		return CommandsList

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, session: "Session", interface: Interface, table: "BaseTable"):
		"""
		Базовый интерпретатор CLI таблицы.

		:param session: Сессия взаимодействия.
		:type session: Session
		:param interface: Интерфейс CLI.
		:type interface: Interface
		:param table: Таблица.
		:type table: BaseTable
		"""

		self._Session = session
		self._Interface = interface
		self._Table = table

	def execute(self, command: ParsedCommandData) -> bool:
		"""
		Обрабатывает команду.

		:param command: Данные команды.
		:type command: ParsedCommandData
		:return: Возвращает `True` при обнаружении команды в списке интерпретируемых.
		:rtype: bool
		"""

		self._ExecuteBaseCommand(command)
		self._ExecuteCustomCommand(command)

		return command.name in tuple(CurrentCommand.name for CurrentCommand in self.commands)



class BaseTableCLI2:
	"""Интерпретатор CLI таблицы."""

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

		Com = Command("search", "Search notes by part of name.")
		Com.base.add_argument(description = "Search query.", important = True)
		Com.base.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		Com = Command("view", "Show list of notes.")
		Com.base.add_flag("r", "Reverse list.")
		Com.base.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		return CommandsList

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
			Status = self.view(parsed_command.get_key_value("sort"), parsed_command.arguments[0], parsed_command.check_flag("r"))
		
		elif parsed_command.name == "view":
			Status = self.view(parsed_command.get_key_value("sort"), None, parsed_command.check_flag("r"))

		return Status

	#==========================================================================================#
	# >>>>> ЗАЩИЩЁННЫЕ ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
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

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def view(self, sort_by: str | None = None, search: str | None = None, reverse: bool = False) -> ExecutionStatus:
		"""
		Выводит список записей. 

		Переопределите данный метод для реализации кастомного вывода.

		:param sort_by: Название колонки, по содержимому которой требуется отсортировать вывод.
		:type sort_by: str | None
		:param search: Поисковый запрос для фильтрации записей.
		:type search: str | None
		:param reverse: Указывает, следует ли инвертировать вывод.
		:type reverse: bool
		:return: Отчёт о выполнении.
		:rtype: ExecutionStatus
		"""
			
		Status = ExecutionStatus()

		try:
			Content = dict()
			sort_by = sort_by or "ID"

			for Column in self._BaseTable.manifest.interfaces_options.cli.columns.to_dict().keys(): Content[Column] = list()
			Notes: list["Note"] = self._Module.notes if self._Module else self._Table.notes

			if sort_by not in Content:
				Status.push_error("no_column_to_sort")
				return Status

			if not Notes:
				Status.push_message("Table is empty.")
				return Status 
			
			if search:
				print("Search:", FastStyler(search).colorize.yellow)
				Notes = [Note for Note in Notes if any(search.lower() in Variant.lower() for Variant in Note.searchable)]
			
			for Note in Notes: Content = self._AddRowToTableContent(Content, Note)

			if Notes:

				for ColumnName in list(Content.keys()):
					if self._BaseTable.manifest.interfaces_options.cli.columns[ColumnName] == False: del Content[ColumnName]

				Columns(Content, sort_by, reverse)

			else: Status.push_message("Notes not found.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status
