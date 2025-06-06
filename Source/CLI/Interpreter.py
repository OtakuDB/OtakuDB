from Source.Core.Session import Session, StorageLevels
from Source.Core.Bus import ExecutionStatus
from Source.CLI.Templates import Columns
from Source.Core.Base import Manifest

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData, Terminalyzer
from dublib.CLI.TextStyler import TextStyler
from dublib.Methods.System import Clear
from dublib.Exceptions.CLI import *
from dublib.CLI import readline

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

		if self.__Session.storage_level is StorageLevels.DRIVER:

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

		elif self.__Session.storage_level is StorageLevels.TABLE:
			CommandsList = self.__Session.table.cli(self.__Session.driver, self.__Session.table).commands

			Com = Command("rename", "Rename table.")
			Com.add_argument(description = "Table name.", important = True)
			CommandsList.append(Com)

		elif self.__Session.storage_level is StorageLevels.MODULE:
			CommandsList = self.__Session.module.cli(self.__Session.driver, self.__Session.table, self.__Session.module).commands

			Com = Command("rename", "Rename module.")
			Com.add_argument(description = "Module name.", important = True)
			CommandsList.append(Com)

		elif self.__Session.storage_level is StorageLevels.NOTE:
			CommandsList = self.__Session.note.cli(self.__Session.driver, self.__Session.table, self.__Session.note).commands

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("close", "Close current note, module or table.")
		CommandsList.append(Com)

		Com = Command("open", "Open path.")
		Com.add_argument(description = "Path to open.", important = True)
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
					Content["Type"].append(TextStyler(TableManifest.type).decorate.italic)
					Content["Moduled"].append(TextStyler("true").colorize.green if TableManifest.modules else TextStyler("false").colorize.red)

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
				case StorageLevels.TABLE: Status += self.__Session.table.cli(self.__Session.driver, self.__Session.table).execute(parsed_command)
				case StorageLevels.MODULE: Status += self.__Session.module.cli(self.__Session.driver, self.__Session.table, self.__Session.module).execute(parsed_command)
				case StorageLevels.NOTE: Status += self.__Session.note.cli(self.__Session.driver, self.__Session.module if self.__Session.module else self.__Session.table, self.__Session.note).execute(parsed_command)

		if Status.navigate: self.__Session.open_objects(Status.navigate)
		if Status.close: self.__Session.close()
		if Status.create_table: Status += self.__Session.driver.create_table(Status.create_table.name, Status.create_table.type)
		if Status.initialize_module: Status += self.__Session.driver.initialize_module(Status.initialize_module, self.__Session.table)

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
			Analyzer.enable_help(True)
			Analyzer.help_translation.important_note = ""
			Status.value = Analyzer.check_commands(self.commands)
			if not Status: Status.push_error(input_line[0]) 

		except NotEnoughParameters: Status.push_error("not_enough_parameters")
		except InvalidParameterType: Status.push_error("invalid_parameter_type")
		except TooManyParameters: Status.push_error("too_many_parameters")
		except UnknownFlag: Status.push_error("unknown_flag")
		except UnknownKey: Status.push_error("unknown_key")
		except MutuallyExclusiveParameters: Status.push_error("mutually_exclusive_parameters")
		except: Status.push_error("unkonw_cli_error")

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Обработчик интерфейса командной строки."""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Session = Session()
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