from .Templates import Columns

from Source.Core.Session.Structs import StorageLevels
from Source.Core.Base.Structs import Interfaces
from Source.Core.Bus import ExecutionStatus
from Source.Core.Base import Manifest

from dublib.CLI.Terminalyzer import Command, ParsedCommandData, Terminalyzer
from dublib.CLI.TextStyler import FastStyler
from dublib.Methods.System import Clear
from dublib.Exceptions.CLI import *
from dublib.CLI import readline

from typing import TYPE_CHECKING
import shlex

if TYPE_CHECKING:
	from Source.Core.Session import Session

class Interpreter:
	"""Обработчик интерфейса командной строки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = list()
		
		if self.__Session.storage_level is StorageLevels.DRIVER:

			Com = Command("create", "Create new table.", category = "Driver")
			Com.base.add_argument(description = "Table name.", important = True)
			Com.base.add_key("type", description = "Type of table.", important = True)
			CommandsList.append(Com)

			Com = Command("list", "Print list of tables.", category = "Driver")
			CommandsList.append(Com)

			Com = Command("mount", "Select storage directory.", category = "Driver")
			Com.base.add_argument(description = "Path to storage directory.")
			CommandsList.append(Com)

		elif self.__Session.storage_level is StorageLevels.TABLE:
			CommandsList = self.__Session.table.get_interface(Interfaces.CLI).commands
			for CurrentCommand in CommandsList: CurrentCommand.set_category("Table")

		elif self.__Session.storage_level is StorageLevels.MODULE:
			CommandsList = self.__Session.module.get_interface(Interfaces.CLI).commands
			for CurrentCommand in CommandsList: CurrentCommand.set_category("Module")

		elif self.__Session.storage_level is StorageLevels.NOTE:
			CommandsList = self.__Session.note.get_interface(Interfaces.CLI).commands
			for CurrentCommand in CommandsList:
				if not CurrentCommand.category: CurrentCommand.set_category("Note")

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
		CommandsList.append(Com)

		Com = Command("open", "Open path.")
		Com.base.add_argument(description = "Path to open.", important = True)
		CommandsList.append(Com)

		Com = Command("close", "Close current note, module or table.")
		CommandsList.append(Com)

		return CommandsList

	#==========================================================================================#
	# >>>>> ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def __ExecuteDriverCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus | None:
		"""
		Обрабатывает команды уровня: driver.
			parsed_command – данные команды.
		"""

		Status = ExecutionStatus()

		if parsed_command.name == "create":
			Status.emit_create_table(parsed_command.arguments[0], parsed_command.get_key_value("type"))

		elif parsed_command.name == "exit":
			exit(0)
		
		elif parsed_command.name == "list":
			Tables = sorted(self.__Driver.tables)

			if len(Tables):
				Content = {
					"Table": [],
					"Type": [],
					"Moduled": []
				}
				
				for Table in self.__Driver.tables:
					TableManifest: Manifest = self.__Driver.load_manifest(Table).value
					Content["Table"].append(Table)
					Content["Type"].append(FastStyler(TableManifest.type).decorate.italic)
					Content["Moduled"].append(FastStyler("true").colorize.green if TableManifest.modules else FastStyler("false").colorize.red)

				Columns(Content, sort_by = "Table")

			else:
				print("No tables.")

		elif parsed_command.name == "mount":
			StorageDir = parsed_command.arguments[0] if len(parsed_command.arguments) else "Data"
			Status = self.__Driver.mount(StorageDir)	

		return Status

	def __Execute(self, parsed_command: ParsedCommandData):
		"""
		Обрабатывает команды.
			parsed_command – данные команды.
		"""

		Status = ExecutionStatus()

		if parsed_command.name == "open": Status += self.__Session.open_objects(parsed_command.arguments[0])
		elif parsed_command.name == "clear": Clear()
		elif parsed_command.name == "close": self.__Session.close()
		elif parsed_command.name == "rename": Status += self.__Session.rename_current_object(parsed_command.arguments[0])
		
		else:

			match self.__Session.storage_level:
				case StorageLevels.DRIVER: Status += self.__ExecuteDriverCommands(parsed_command)
				case StorageLevels.TABLE: Status += self.__Session.table.get_interface(Interfaces.CLI).execute(parsed_command)
				case StorageLevels.MODULE: Status += self.__Session.module.get_interface(Interfaces.CLI).execute(parsed_command)
				case StorageLevels.NOTE: Status += self.__Session.note.get_interface(Interfaces.CLI).execute(parsed_command)

		if Status.close: self.__Session.close()
		if Status.create_table: Status += self.__Session.driver.create_table(Status.create_table.name, Status.create_table.type)
		if Status.initialize_module: Status += self.__Session.driver.initialize_module(Status.initialize_module, self.__Session.table)
		if Status.navigate: Status += self.__Session.open_objects(Status.navigate)

		Status.print_messages()

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GenerateSelector(self) -> str:
		"""Идентификатор ввода."""

		TableName = "-" + self.__Session.table.name if self.__Session.table else ""
		if self.__Session.module: TableName += ":" + self.__Session.module.name
		NoteID = "-" + str(self.__Session.note.id) if self.__Session.note else ""
		Selector = f"[OtakuDB{TableName}{NoteID}]-> "

		return Selector

	def __ParseCommandData(self, input_line: list[str]) -> ExecutionStatus:
		"""Парсит команду на составляющие."""

		Status = ExecutionStatus()

		try:
			Analyzer = Terminalyzer(input_line)
			Analyzer.helper.enable()
			Analyzer.helper.enable_sorting()
			Status.value = Analyzer.check_commands(self.commands)
			if not Status: Status.push_error(input_line[0]) 

		except NotEnoughParameters: Status.push_error("not_enough_parameters")
		except InvalidParameterType: Status.push_error("invalid_parameter_type")
		except TooManyParameters: Status.push_error("too_many_parameters")
		except UnknownFlag: Status.push_error("unknown_flag")
		except UnknownKey: Status.push_error("unknown_key")
		except MutuallyExclusiveParameters: Status.push_error("mutually_exclusive_parameters")
		except ZeroDivisionError as ExceptionData:
			Type = type(ExceptionData).__qualname__
			Status.push_error(f"{Type}: {ExceptionData}")

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, session: "Session"):
		"""
		Обработчик интерфейса командной строки.

		:param session: Сессия.
		:type session: Session
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Session = session
		self.__Driver = self.__Session.driver

		if self.__Session.driver.is_mounted: print(f"Mounted: \"{self.__Driver.storage_directory}\".")

	def run(self):
		"""Запускает CLI."""

		Clear()
		InputLine = None
		
		while True:
			Status = ExecutionStatus()

			try:
				InputLine = input(self.__GenerateSelector())
				InputLine = InputLine.strip()
				InputLine = shlex.split(InputLine) if len(InputLine) > 0 else None

			except KeyboardInterrupt:
				print("exit")
				exit()

			except ValueError as ExceptionData:

				if str(ExceptionData) == "No closing quotation":
					Status.push_error("No closing quotation.")
					InputLine = None
					Status.print_messages()

				else: raise ValueError(str(ExceptionData))

			if InputLine:
				Status = self.__ParseCommandData(InputLine)
				if Status: self.__Execute(Status.value)	
				else: Status.print_messages()		