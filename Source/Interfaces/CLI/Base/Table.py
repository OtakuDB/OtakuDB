from Source.Interfaces.CLI.Options.Local import TableInterfaceOptions
from Source.Interfaces.CLI.Templates import PrintTable
from Source.Core import Exceptions

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.Templates.Bus import PrintError
from dublib.CLI.Templates import Confirmation
from typing import TYPE_CHECKING

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
		ComPos.add_argument(ParametersTypes.Number)
		ComPos = Com.create_position("NEW_ID", description = "New note ID", important = True)
		ComPos.add_argument(ParametersTypes.Number)
		ComPos = Com.create_position("MODE", "Mode of ID changing.")
		ComPos.add_flag("o", "Overwtite exists note.")
		ComPos.add_flag("s", "Swipe with exists note.")
		ComPos.add_flag("i", "Insert to exists note place.")
		CommandsList.append(Com)

		Com = Command("close", "Close table.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete table.")
		Com.base.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("new", "Create new note.")
		Com.base.add_flag("o", "Open note after creation.")
		CommandsList.append(Com)

		Com = Command("open", "Open note CLI.")
		ComPos = Com.create_position("ID", "Note ID.", important = True)
		ComPos.add_argument(ParametersTypes.Number)
		CommandsList.append(Com)

		Com = Command("rename", "Rename table.")
		Com.base.add_argument(description = "New table name.")
		CommandsList.append(Com)

		Com = Command("search", "Search notes.")
		Com.base.add_argument(description = "Search query (part of name or another names).", important = True)
		CommandsList.append(Com)

		Com = Command("view", "Show list of notes.")
		Com.base.add_flag("r", "Reverse list.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def commands(self) -> list[Command]:
		"""Полный список команд интерпретатора."""

		return self.base_commands + self._GenerateCustomCommands()
	
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

		if command.check_flag("i"): Mode = "i"
		elif command.check_flag("o"): Mode = "o"
		elif command.check_flag("s"): Mode = "s"
		
		try: self._Table.change_note_id(NoteID, NewID, Mode)
		except Exceptions.Table.NoteNotFound: PrintError(f"Note with ID #{NoteID} not found.")
		except Exceptions.Table.OperationError as ExceptionData: PrintError(ExceptionData)

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

	def _ExecuteBaseCommand(self, command: ParsedCommandData):
		"""
		Обрабатывает базовую команду.
		
		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		match command.name:
			case "chid": self._chid(command)
			case "close": self._Interface.set_current_object(self._Session.navigator.current_box)
			case "delete": self._delete(command.check_flag("y"))
			case "new": self._new(command.check_flag("o"))
			case "open": self._open(command.arguments[0])
			case "rename": self._Table.rename(command.arguments[0])
			case "view": self.view(command.check_flag("r"))

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

		Notes = self._Table.notes
		if not Notes:
			print("Table is empty.")
			return
		
		#---> Поиск подходящих записей.
		#==========================================================================================#
		if search_query:
			print("Search by:", search_query)
			SearchResult = list()

			for CurrentNote in Notes:
				for String in CurrentNote.searchable_strings:
					if search_query in String:
						SearchResult.append(CurrentNote)
						break

			if not SearchResult: print("No results.")
			else: Notes = tuple(SearchResult)

		#---> Вывод записей.
		#==========================================================================================#
		RowData = {Key: None for Key in self._InterfaceOptions.columns.names}
		Columns = {Key: list() for Key in RowData.keys()}

		for CurrentNote in Notes:
			RowData = self._GenerateTableRow(RowData, CurrentNote)
			
			for ColumnName in Columns.keys():
				Value = RowData[ColumnName]
				if Value == None: Value = ""
				Columns[ColumnName].append(Value)

		PrintTable(Columns, reverse = reverse)