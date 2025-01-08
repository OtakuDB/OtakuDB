from Source.CLI.Templates import Columns
from Source.Core.Warnings.ModuleWarnings import *
from Source.Core.Errors import *
from Source.Driver import Driver

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData, Terminalyzer
from dublib.CLI.Templates import PrintExecutionStatus
from dublib.Engine.Bus import ExecutionError, ExecutionWarning, ExecutionStatus
from dublib.CLI.TextStyler import Styles, TextStyler
from dublib.Methods.System import Clear
from dublib.Exceptions.CLI import *

import readline
import shlex

class Interpreter:
	"""Обработчик интерфейса командной строки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = list()

		if self.__InterpreterLevel == "driver":

			Com = Command("clear", "Clear console.")
			CommandsList.append(Com)

			Com = Command("create", "Create new table.")
			Com.add_argument(description = "Table name.", important = True)
			Com.add_key("type", description = "Type of table.", important = True)
			CommandsList.append(Com)

			Com = Command("exit", "Exit from OtakuDB.")
			CommandsList.append(Com)

			Com = Command("list", "Print list of tables.")
			CommandsList.append(Com)

			Com = Command("mount", "Select storage directory.")
			Com.add_argument(description = "Path to storage directory.")
			CommandsList.append(Com)

			Com = Command("open", "Open table.")
			Com.add_argument(description = "Table name.", important = True)
			CommandsList.append(Com)

		elif self.__InterpreterLevel == "table":
			CommandsList = self.__Table.cli(self.__Driver, self.__Table).commands

		elif self.__InterpreterLevel == "module":
			CommandsList = self.__Module.cli(self.__Driver, self.__Table, self.__Module).commands

		elif self.__InterpreterLevel == "note":
			CommandsList = self.__Note.cli(self.__Driver, self.__Table, self.__Note).commands

		return CommandsList

	@property
	def selector(self) -> str:
		"""Идентификатор ввода."""

		TableName = "-" + self.__Table.name if self.__Table else ""
		if self.__Module: TableName += ":" + self.__Module.name
		NoteID = "-" + str(self.__Note.id) if self.__Note else ""
		Selector = f"[OtakuDB{TableName}{NoteID}]-> "

		return Selector

	#==========================================================================================#
	# >>>>> ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def __ExecuteDriverCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus | None:
		"""
		Обрабатывает команды уровня: driver.
			parsed_command – данные команды.
		"""

		Status = ExecutionStatus(0)
		
		if parsed_command.name == "clear":
			Clear()

		if parsed_command.name == "create":
			Status["create_table"] = parsed_command.arguments[0]
			Status["table_type"] = parsed_command.get_key_value("type")

		if parsed_command.name == "exit":
			exit(0)
		
		if parsed_command.name == "list":
			Tables = sorted(self.__Driver.tables)

			if len(Tables):
				Content = {
					"Table": [],
					"Type": []
				}
				
				for Table in self.__Driver.tables:
					Manifest = self.__Driver.load_manifest(Table).value
					Content["Table"].append(Table)
					Content["Type"].append(TextStyler(Manifest.type).decorate.italic)

				Columns(Content, sort_by = "Table")

			else:
				print("No tables.")

		if parsed_command.name == "mount":
			StorageDir = parsed_command.arguments[0] if len(parsed_command.arguments) else "Data"
			Status = self.__Driver.mount(StorageDir)
			
		if parsed_command.name == "open":
			Status["open_table"] = parsed_command.arguments[0]		

		return Status

	def __Execute(self, parsed_command: ParsedCommandData):
		"""
		Обрабатывает команды.
			parsed_command – данные команды.
		"""

		Status = ExecutionStatus(0)
		if self.__InterpreterLevel == "driver": Status = self.__ExecuteDriverCommands(parsed_command)
		if self.__InterpreterLevel == "table": Status: ExecutionStatus = self.__Table.cli(self.__Driver, self.__Table).execute(parsed_command)
		if self.__InterpreterLevel == "module": Status: ExecutionStatus = self.__Module.cli(self.__Driver, self.__Table, self.__Module).execute(parsed_command)
		if self.__InterpreterLevel == "note": Status: ExecutionStatus = self.__Note.cli(self.__Driver, self.__Module if self.__Module else self.__Table, self.__Note).execute(parsed_command)
		
		if Status.code == 0:

			if Status.check_data("create_table"):
				Status = self.__Driver.create(Status["create_table"], type = Status["table_type"])

			if Status.check_data("initialize_module"):
				Status = self.__Driver.create(Status["initialize_module"], table = self.__Table)

			if Status.check_data("open_table"):
				Status = self.__Driver.open(Status["open_table"])

				if Status.code == 0:
					self.__Table = Status.value
					self.__InterpreterLevel = "table"

			if Status.check_data("open_module"):
				Status = self.__Driver.open(Status["open_module"], self.__Table)

				if Status.code == 0:
					self.__Module = Status.value
					self.__InterpreterLevel = "module"
			
			if Status.check_data("open_note"):
				Status = self.__OpenNote(Status["open_note"])

			if Status.check_data("interpreter"):
				self.__InterpreterLevel = Status["interpreter"]

				if self.__InterpreterLevel == "driver":
					self.__Table = None
					self.__Module = None
					self.__Note = None

				if self.__InterpreterLevel == "table":
					self.__Module = None
					self.__Note = None

				if self.__InterpreterLevel == "module":
					self.__Note = None

		PrintExecutionStatus(Status)

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __OpenNote(self, note_id: int) -> ExecutionStatus:
		"""
		Открывает запись.
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus(0)
		if self.__Module: Status = self.__Module.get_note(note_id)
		else: Status = self.__Table.get_note(note_id)

		if Status.code == 0:
			self.__Note = Status.value
			self.__InterpreterLevel = "note"

		return Status

	def __ParseCommandData(self, input_line: list[str]) -> ExecutionStatus:
		"""Парсит команду на составляющие."""

		Status = ExecutionStatus(0)

		try:
			Analyzer = Terminalyzer(input_line)
			Analyzer.enable_help(True)
			Analyzer.help_translation.important_note = ""
			Status.value = Analyzer.check_commands(self.commands)

			if not Status.value:
				Status = ExecutionError(-2, "unknown_command")
				Status["print"] = input_line[0]

		except NotEnoughParameters:
			Status = ExecutionError(-3, "not_enough_parameters")

		except InvalidParameterType as ExceptionData:
			Type = str(ExceptionData).split("\"")[-2]
			Status = ExecutionError(-4, "invalid_parameter_type")
			Status["print"] = Type

		except TooManyParameters:
			Status = ExecutionError(-5, "too_many_parameters")

		except UnknownFlag as ExceptionData:
			Flag = str(ExceptionData).split("\"")[-2].lstrip("-")
			Status = ExecutionError(-6, "unknown_flag")
			Status["print"] = Flag

		except UnknownKey as ExceptionData:
			Key = str(ExceptionData).split("\"")[-2].lstrip("-")
			Status = ExecutionError(-7, "unknown_key")
			Status["print"] = Key

		except MutuallyExclusiveParameters:
			Status = ExecutionError(-8, "mutually_exclusive_parameters")

		except: Status = ExecutionError(-1, "mutually_exclusive_parameters")

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Обработчик интерфейса командной строки."""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Driver = Driver(mount = True)
		if self.__Driver.is_mounted: print(f"Mounted: \"{self.__Driver.storage_directory}\"." )
		self.__InterpreterLevel = "driver"
		self.__Table = None
		self.__Module = None
		self.__Note = None

	def run(self):
		"""Запускает CLI."""

		Clear()
		InputLine = None
		
		while True:

			try:
				InputLine = input(self.selector)
				InputLine = InputLine.strip()
				InputLine = shlex.split(InputLine) if len(InputLine) > 0 else None

			except KeyboardInterrupt:
				print("exit")
				exit()

			except ValueError as ExceptionData:

				if str(ExceptionData) == "No closing quotation":
					Status = ExecutionError(-1, "no_closing_quotation")
					InputLine = None
					PrintExecutionStatus(Status)

				else: raise ValueError(str(ExceptionData))

			if InputLine:
				Status = self.__ParseCommandData(InputLine)
				if Status.code == 0: self.__Execute(Status.value)	
				else: PrintExecutionStatus(Status)				