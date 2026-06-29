from Source.Interfaces.CLI.Options.Local import TableInterfaceOptions
from Source.Core import Exceptions

from dublib.CLI.Terminalyzer import ValidableTypes, Command, ParsedCommandData
from dublib.CLI.Templates.Bus import PrintError, PrintWarning
from dublib.CLI.Templates import Confirmation
from dublib.CLI.TextStyler import FastStyler
from dublib.Methods.System import Clear

from typing import TYPE_CHECKING

from prettytable import PLAIN_COLUMNS, PrettyTable
import questionary

if TYPE_CHECKING:
	from Source.Core.Base.Table import BaseTable
	from Source.Interfaces.CLI import Interface
	from Source.Core.Base.Note import BaseNote
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

		Com = Command("chid", "Change ID of note.")
		ComPos = Com.create_position("NOTE_ID", description = "Exists note ID.", important = True)
		ComPos.set_argument(ValidableTypes.UnsignedInteger)
		ComPos = Com.create_position("NEW_ID", description = "New note ID.", important = True)
		ComPos.set_argument(ValidableTypes.UnsignedInteger)
		ComPos = Com.create_position("MODE", description = "Mode of ID changing. By default may insert only on free index.")
		ComPos.add_flag("-o", description = "Overwtite exists note.")
		ComPos.add_flag("-s", description = "Swipe with exists note.")
		ComPos.add_flag("-i", description = "Insert to filled note place with offset. If index is free same as default.")
		CommandsList.append(Com)

		Com = Command("close", "Close table.")
		CommandsList.append(Com)

		Com = Command("column", "Manage column viewing options.")
		ComPos = Com.create_position("COLUMN", "Column name (case insensitive).", important = True)
		ComPos.set_argument(ValidableTypes.Alpha)
		ComPos = Com.create_position("OPERATION", "Management operation.", important = True)
		ComPos.add_flag("-e", "Enable column.")
		ComPos.add_flag("-d", "Disable column.")
		ComPos.add_key("--max-width", type = ValidableTypes.UnsignedInteger, description = "Maximal width of column content. Put 0 to clear.")
		CommandsList.append(Com)

		Com = Command("columns", "Runs columns visibility manager.", "TUI")
		CommandsList.append(Com)

		Com = Command("delete", "Delete table.")
		Com.base.add_flag("-y", description = "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("new", "Create new note.")
		Com.base.add_flag("-o", description = "Open note after creation.")
		CommandsList.append(Com)

		Com = Command("open", "Open note CLI.")
		ComPos = Com.create_position("ID", "Note ID.", important = True)
		ComPos.set_argument(ValidableTypes.UnsignedInteger)
		CommandsList.append(Com)

		Com = Command("rename", "Rename table.")
		ComPos = Com.create_position("NAME", description = "New table name.")
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("search", "Search notes.")
		ComPos = Com.create_position("QUERY", description = "Search query (part of name or another names).", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("view", "Show list of notes.")
		Com.base.add_flag("-r", description = "Reverse list.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def commands(self) -> list[Command]:
		"""Полный список команд интерпретатора."""

		CustomCommands = self._GenerateCustomCommands()
		for Index in range(len(CustomCommands)):
			if not CustomCommands[Index].category: CustomCommands[Index].set_category("Table")

		return self.base_commands + CustomCommands
	
	@property
	def interface_options(self) -> TableInterfaceOptions:
		"""Параметры интерфейса таблицы"""

		return self._InterfaceOptions

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def _chid(self, command: ParsedCommandData):
		"""
		Изменяет ID записи.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		NoteID = command.arguments[0]
		NewID = command.arguments[1]
		Mode = None

		if command.check_flag("-i"): Mode = "i"
		elif command.check_flag("-o"): Mode = "o"
		elif command.check_flag("-s"): Mode = "s"
		
		try: self._Table.change_note_id(NoteID, NewID, Mode)
		except Exceptions.Table.NoteNotFound: PrintError(f"Note with ID #{NoteID} not found.")
		except Exceptions.Table.OperationError as ExceptionData: PrintError(ExceptionData)

	def _column(self, command: ParsedCommandData):
		"""
		Редактирует параметры отображения колонки.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		Column = command.get_position_value("COLUMN")
		ColumnOptions = None
		
		try: ColumnOptions = self._InterfaceOptions.columns.get_column_options(Column)
		except KeyError:
			PrintError(f"Options for column \"{Column}\" not found.")
			return
		
		if command.check_flag("-e"): ColumnOptions.set_status(True)
		elif command.check_flag("-d"): ColumnOptions.set_status(False)
		elif command.check_key("--max-width"): ColumnOptions.set_max_width(command.get_key_value("--max-width") or None)

	def _columns(self):
		"""Запускает диалог для переключения видимости колонок."""

		ColumnsOptions = self._InterfaceOptions.columns
		
		EnabledColumns = questionary.checkbox(
			message = "Choose displayed columns:",
			choices = tuple(questionary.Choice(Option.name, checked = Option.is_enabled) for Option in ColumnsOptions.options),
			instruction = "Navigate by <Up>, <Down> keys, switch by <Space>, save by <Enter>."
		).ask()

		if EnabledColumns is None: return
		for Column in ColumnsOptions.names: ColumnsOptions.get_column_options(Column).set_status(Column in EnabledColumns)

	def _delete(self, confirm: bool = False):
		"""
		Удаляет таблицу.

		:param confirm: Отключает подтверждение удаления.
		:type confirm: bool
		"""
		
		if not confirm and not Confirmation("This table will be deleted with all data."): return
		self._Table.delete()
		self._Interface.set_current_object(self._Session.navigator.current_box)

	def _new(self, open: bool = False):
		"""
		Создаёт новую запись.

		:param open: Указывает, нужно ли открыть запись после создания.
		:type open: bool, optional
		"""
		
		NewNote = self._Table.create_note()
		if open: self._Interface.set_current_object(NewNote)
		print(f"New note ID is #{NewNote.id}.")

	def _open(self, note_id: int):
		"""
		Открывает запись.

		:param note_id: ID записи.
		:type note_id: int
		"""

		try: self._Interface.set_current_object(self._Table.get_note(note_id))
		except Exceptions.Table.NoteNotFound: PrintError("Note not found.")

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenerateCellFromMetainfo(self, note: "BaseNote", column: str, field: str) -> str | None:
		"""
		Генерирует содержимое ячейки таблицы из поля метаданных. Автоматически обрабатывает наборы значений и максимульную ширину столбика.

		:param note: Запись
		:type note: BaseNote
		:param column: Имя колонки.
		:type column: str
		:param field: Имя поля метаданных.
		:type field: str
		:return: Значение ячейки.
		:rtype: str | None
		:raises MetainfoFieldNotDescribed: Поле метаданных отсутствует.
		"""

		Value = note.metainfo.get_field_value(field)
		
		if type(Value) is list:
			ElementsCount = len(Value)
			Value = Value[0]

			OtherCount = ElementsCount - 1
			OtherLabel = f" (and {OtherCount} other)"
			MaxColumnWidth = self._InterfaceOptions.columns.get_column_options(column).max_width
			if OtherCount:
				if not MaxColumnWidth or len(Value + OtherLabel) <= MaxColumnWidth: Value += OtherLabel

		else: 
			Value = str(Value)

		return Value

	def _ExecuteBaseCommand(self, command: ParsedCommandData):
		"""
		Обрабатывает базовую команду.
		
		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		match command.name:
			case "chid": self._chid(command)
			case "close": self._Interface.set_current_object(self._Session.navigator.current_box)
			case "column": self._column(command)
			case "columns": self._columns()
			case "delete": self._delete(command.check_flag("-y"))
			case "new": self._new(command.check_flag("-o"))
			case "open": self._open(command.arguments[0])
			case "rename": self._Table.rename(command.arguments[0])
			case "view": self.view(reverse = command.check_flag("-r"))
			case "search": self.view(command.get_position_value("QUERY"))

	def _PrintTable(self, columns: dict[str, list], sort_by: str | None = None, reverse: bool = False):
		"""
		Выводит таблицу в консоль.

		:param columns: Словарь, в которором ключи – названия колнок, а значения – списки значений.
		:type columns: dict[str, list]
		:param sort_by: Указывает название колонки, по которой идёт сортировка.
		:type sort_by: str | None
		:param reverse: Переключает реверсирование отображаемого контента.
		:type reverse: bool
		"""

		TableObject = PrettyTable()
		TableObject.set_style(PLAIN_COLUMNS)
		TableObject.left_padding_width = 0
		TableObject.right_padding_width = 3

		for ColumnName in columns.keys():
			Options = self._InterfaceOptions.columns.get_column_options(ColumnName)
			if not Options.is_enabled: continue

			if Options.max_width:
				for Index in range(len(columns[ColumnName])):
					if columns[ColumnName][Index] == None: columns[ColumnName][Index] = ""
					elif type(columns[ColumnName][Index]) != str: columns[ColumnName][Index] = str(columns[ColumnName][Index])

					if len(columns[ColumnName][Index]) > Options.max_width:
						columns[ColumnName][Index] = columns[ColumnName][Index][:Options.max_width].rstrip() + "…"

			Buffer = FastStyler(ColumnName).decorate.bold
			TableObject.add_column(Buffer, columns[ColumnName])

		TableObject.align = "l"
		TableObject.reversesort = reverse

		if sort_by:
			ColumnOptions = self._InterfaceOptions.columns.get_column_options(sort_by)
			if ColumnOptions.is_enabled: TableObject.sortby = FastStyler(sort_by).decorate.bold
			else: PrintWarning(f"Column \"{sort_by}\" disabled. Impossible to sort.")

		print(TableObject)

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

		return list()

	def _GenerateTableRow(self, container: dict[str, None], note: "BaseNote") -> dict[str, str | None]:
		"""
		Генерирует данные для заполнения строки таблицы.

		:param container: Словарь, в котром ключи являются названиями колонок.
		:type container: dict[str, None]
		:param note: Запись.
		:type note: BaseNote
		:return: Словарь с подставленными значениями.
		:rtype: dict[str, str | None]
		"""

		container["ID"] = note.id
		container["Name"] = note.name

		return container

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

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

		self._InterfaceOptions = TableInterfaceOptions(self._Table.manifest.interfaces_options)

		self._PostInitMethod()

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
	
	def view(self, search_query: str | None = None, reverse: bool = False):
		"""Выводит список записей таблицы."""

		if self._InterfaceOptions.autoclear: Clear()

		Notes = self._Table.notes
		if not Notes:
			print("Table is empty.")
			return
		
		#---> Поиск подходящих записей.
		#==========================================================================================#
		if search_query:
			print("Search by:", search_query)
			SearchResult = list()
			search_query = search_query.lower()

			for CurrentNote in Notes:
				for String in CurrentNote.searchable_strings:
					if search_query in String.lower():
						SearchResult.append(CurrentNote)
						break

			if SearchResult: Notes = tuple(SearchResult)
			else:
				print("No results.")
				return

		#---> Вывод записей.
		#==========================================================================================#
		RowData = {Key: None for Key in self._InterfaceOptions.columns.names}
		Columns = {Key: list() for Key in RowData.keys()}

		for CurrentNote in Notes:
			RowData = self._GenerateTableRow(RowData, CurrentNote)
			
			for ColumnName in Columns.keys():
				Value = RowData[ColumnName]
				if Value is None: Value = ""
				Columns[ColumnName].append(Value)

		self._PrintTable(Columns, sort_by = "ID", reverse = reverse)