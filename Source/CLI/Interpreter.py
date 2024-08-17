from Source.CLI.Templates import Columns
from Source.Core.Warnings import *
from Source.Core.Errors import *
from Source.Driver import Driver

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData, Terminalyzer
from dublib.CLI.Templates import Confirmation, PrintExecutionStatus
from dublib.Engine.Bus import ExecutionError, ExecutionWarning, ExecutionStatus
from dublib.CLI.StyledPrinter import Styles, TextStyler
from dublib.CLI.Templates import Confirmation
from dublib.Methods.System import Clear
from dublib.Exceptions.CLI import *

import readline
import shlex

class Interpreter:
	"""Обработчик интерфейса командной строки."""

	#==========================================================================================#
	# >>>>> ГЕНЕРАТОРЫ УРОВНЕЙ КОМАНД <<<<< #
	#==========================================================================================#

	def __GenerateDriverCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: driver."""

		CommandsList = list()

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("create", "Create new table.")
		Com.add_argument(description = "Table name.", important = True)
		Com.add_key("type", description = "Type of table.", important = True)
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
		CommandsList.append(Com)

		Com = Command("list", "Print list op tables.")
		CommandsList.append(Com)

		Com = Command("mount", "Select storage directory.")
		Com.add_argument(description = "Path to storage directory.")
		CommandsList.append(Com)

		Com = Command("open", "Open table.")
		Com.add_argument(description = "Table name.", important = True)
		CommandsList.append(Com)

		return CommandsList

	def __GenerateTableCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: table."""

		CommandsList = list()

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("close", "Close table.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete table.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
		CommandsList.append(Com)

		Com = Command("init", "Initialize module.")
		Com.add_argument(description = "Module name.", important = True)
		CommandsList.append(Com)

		Com = Command("modules", "List of modules.")
		CommandsList.append(Com)

		Com = Command("open", "Open note or module.")
		ComPos = Com.create_position("TARGET", "Target for opening.", important = True)
		ComPos.add_argument(description = "Note ID or module name.")
		ComPos.add_flag("m", description = "Open note with max ID.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename table.")
		Com.add_argument(description = "Table name.", important = True)
		CommandsList.append(Com)

		CommandsList += self.__Table.cli.commands

		return CommandsList

	def __GenerateModuleCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: table."""

		CommandsList = list()

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("close", "Close module.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete module.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
		CommandsList.append(Com)

		Com = Command("open", "Open note.")
		ComPos = Com.create_position("NOTE", "Note identificator.", important = True)
		ComPos.add_argument(ParametersTypes.Number, description = "Note ID.")
		ComPos.add_flag("m", description = "Open note with max ID.")
		CommandsList.append(Com)

		Com = Command("switch", "Switch to other table module.")
		Com.add_argument(description = "Module name.",)
		CommandsList.append(Com)

		CommandsList += self.__Module.cli.commands

		return CommandsList

	def __GenerateNoteCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: note."""

		CommandsList = list()

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("close", "Close note.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete note.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuDB.")
		CommandsList.append(Com)

		CommandsList += self.__Note.cli.commands

		return CommandsList

	#==========================================================================================#
	# >>>>> ОБРАБОТЧИКИ УРОВНЕЙ КОМАНД <<<<< #
	#==========================================================================================#

	def __ProcessDriverCommands(self, command_data: ParsedCommandData):
		"""
		Обрабатывает команды уровня: driver.
			command_data – данные команды.
		"""

		Status = None
		
		if command_data.name == "clear":
			Clear()

		if command_data.name == "create":
			Status = self.__Driver.create_table(command_data.arguments[0], command_data.get_key_value("type"))

		if command_data.name == "exit":
			exit(0)
		
		if command_data.name == "list":
			Tables = sorted(self.__Driver.tables)

			if len(Tables):
				Content = {
					"Table": [],
					"Type": []
				}
				
				for Table in self.__Driver.tables:
					Manifest = self.__Driver.get_manifest(Table).value
					Content["Table"].append(Table)
					Content["Type"].append(TextStyler(Manifest["type"], decorations = [Styles.Decorations.Italic]))

				Columns(Content, sort_by = "Table")

			else:
				print("No tables.")

		if command_data.name == "mount":
			StorageDir = command_data.arguments[0] if len(command_data.arguments) else "Data"
			Status = self.__Driver.mount(StorageDir)
			
		if command_data.name == "open":
			Status = self.__Driver.open_table(command_data.arguments[0])

			if Status.code == 0:
				self.__Table = Status.value
				self.__InterpreterLevel = "table"		

		PrintExecutionStatus(Status)

	def __ProcessTableCommands(self, command_data: ParsedCommandData):
		"""
		Обрабатывает команды уровня: table.
			command_data – данные команды.
		"""

		Status = ExecutionStatus(0)

		if command_data.name == "clear":
			Clear()

		elif command_data.name == "close":
			self.__Table = None
			self.__InterpreterLevel = "driver"

		elif command_data.name == "exit":
			self.exit()

		elif command_data.name == "init":
			Modules = self.__Table.modules
			if Modules: Status = self.__Driver.create_module(self.__Table, command_data.arguments[0])
			else: Status = ExecutionWarning(-1, "Table doesn't contain modules.")

		elif command_data.name == "modules":
			Modules: list[dict] = self.__Table.modules

			if Modules:

				for Module in Modules:
					ModuleStatus = TextStyler("ON", text_color = Styles.Colors.Green) if Module["active"] else TextStyler("OFF", text_color = Styles.Colors.Red)
					print(f"{Module["name"]}: {ModuleStatus}")

			else: Status = ExecutionWarning(-1, "Table doesn't contain modules.")

		elif command_data.name == "open":

			if command_data.arguments[0].isdigit():
				NoteID = None

				if command_data.check_flag("m") and self.__Table.notes_id:
					NoteID = max(self.__Table.notes_id)
				
				else:
					NoteID = int(command_data.arguments[0])

				Status = self.__OpenNote(NoteID)

			else:
				Modules = self.__Table.modules

				if Modules:
					Status = self.__Driver.open_module(self.__Table, command_data.arguments[0])

					if Status.code == 0:
						self.__Module = Status.value
						self.__InterpreterLevel = "module"

				else: Status = TABLE_WARNING_NO_MODULES

		elif command_data.name == "delete":
			Response = Confirmation("Are you sure to delete \"" + self.__Table.name + "\" table?")
			
			if Response:
				Status = self.__Driver.delete_table(self.__Table.name)

				if Status.code == 0:
					self.__Table = None
					self.__InterpreterLevel = "driver"

		elif command_data.name == "rename":
			Status = self.__Table.rename(command_data.arguments[0])

		else:
			Status = self.__Table.cli.execute(command_data)

		if Status and Status.code == 0 and Status.check_data("open_note"): Status = self.__OpenNote(Status["note_id"])

		PrintExecutionStatus(Status)

	def __ProcessModuleCommands(self, command_data: ParsedCommandData):
		"""
		Обрабатывает команды уровня: table.
			command_data – данные команды.
		"""

		Status = ExecutionStatus(0)

		if command_data.name == "clear":
			Clear()

		elif command_data.name == "close":
			Status = self.__Driver.open_table(self.__Module.table_name)

			if Status.code == 0:
				self.__Module = None
				self.__Table = Status.value
				self.__InterpreterLevel = "table"

		elif command_data.name == "exit":
			self.exit()

		elif command_data.name == "init":
			Modules = self.__Table.modules
			if Modules: Status = self.__Driver.create_module(self.__Table, command_data.arguments[0])
			else: Status = ExecutionWarning(-1, "Table doesn't contain modules.")

		elif command_data.name == "modules":
			Modules = self.__Table.modules

			if Modules:

				for Module in Modules:
					ModuleStatus = TextStyler("ON", text_color = Styles.Colors.Green) if Module["path"] else TextStyler("OFF", text_color = Styles.Colors.Red)
					print(Module["name"] + ":", ModuleStatus)

			else: Status = ExecutionStatus(0, "Table doesn't contain modules.")

		elif command_data.name == "open":
			NoteID = None

			if command_data.check_flag("m") and self.__Module.notes_id:
				NoteID = max(self.__Module.notes_id)
			
			else:
				NoteID = int(command_data.arguments[0])

			Status = self.__OpenNote(NoteID)

		elif command_data.name == "delete":
			Response = Confirmation("Are you sure to delete \"" + self.__Module.name + "\" module?")
			
			if Response:
				Status = self.__Driver.delete_module(self.__Table, self.__Module.name)

				if Status.code == 0:
					self.__Module = None
					self.__InterpreterLevel = "table"

		elif command_data.name == "switch":
			Status = self.__Table.rename(command_data.arguments[0])

		else:
			Status = self.__Module.cli.execute(command_data)

		if Status and Status.code == 0 and Status.check_data("open_note"): Status = self.__OpenNote(Status["note_id"])

		PrintExecutionStatus(Status)

	def __ProcessNoteCommands(self, command_data: ParsedCommandData):
		"""
		Обрабатывает команды уровня: note.
			command_data – данные команды.
		"""

		Status = None

		if command_data.name == "clear":
			Clear()

		elif command_data.name == "close":
			self.__Note = None
			self.__InterpreterLevel = "module" if self.__Module else "table"

		elif command_data.name == "exit":
			self.exit()

		elif command_data.name == "delete":
			Response = Confirmation("Are you sure to delete #" + str(self.__Note.id) + " note?")
			
			if Response:
				if self.__Module: Status = self.__Module.delete_note(self.__Note.id)
				else: Status = self.__Table.delete_note(self.__Note.id)

				if Status.code == 0:
					self.__Note = None
					self.__InterpreterLevel = "module" if self.__Module else "table" 

		else:
			Status = self.__Note.cli.execute(command_data)

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

	def __Selector(self) -> str:
		"""Создаёт идентификатор ввода в зависимости от уровня интерпретации."""

		TableName = "-" + self.__Table.name if self.__Table else ""
		if self.__Module: TableName += ":" + self.__Module.name
		NoteID = "-" + str(self.__Note.id) if self.__Note else ""
		Selector = f"[OtakuDB{TableName}{NoteID}]-> "

		return Selector

	def __ParseCommandData(self, input_line: list[str]) -> ExecutionStatus:
		"""Парсит команду на составляющие."""

		Status = ExecutionStatus(0)

		try:
			Analyzer = Terminalyzer(input_line)
			Analyzer.enable_help(True)
			Analyzer.help_translation.important_note = ""
			Status.value = Analyzer.check_commands(self.__CommandsGenerators[self.__InterpreterLevel]())

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

		except:
			Status = ExecutionError(-1, "unknown_terminalyzer_error")

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
		self.__CommandsGenerators = {
			"driver": self.__GenerateDriverCommands,
			"table": self.__GenerateTableCommands,
			"module": self.__GenerateModuleCommands,
			"note": self.__GenerateNoteCommands
		}
		self.__Processors = {
			"driver": self.__ProcessDriverCommands,
			"table": self.__ProcessTableCommands,
			"module": self.__ProcessModuleCommands,
			"note": self.__ProcessNoteCommands
		}
		self.__Table = None
		self.__Module = None
		self.__Note = None

	def exit(self, print_command: bool = False):
		"""
		Закрывает OtakuDB.
			print_command – указывает, добавить ли команду в вывод.
		"""

		if print_command: print("exit")
		print("Exiting...")
		exit(0)

	def run(self):
		"""Запускает оболочку CLI."""

		InputLine = None
		Clear()

		while True:

			try:
				InputLine = input(self.__Selector())
				InputLine = InputLine.strip()
				InputLine = shlex.split(InputLine) if len(InputLine) > 0 else [""]

			except KeyboardInterrupt: self.exit(True)

			if InputLine != [""]:
				Status = self.__ParseCommandData(InputLine)
				PrintExecutionStatus(Status)
				if Status.code == 0: self.__Processors[self.__InterpreterLevel](Status.value)					