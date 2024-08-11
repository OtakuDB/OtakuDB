from Source.CLI.Templates import Columns
from Source.Driver import Driver

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData, Terminalyzer
from dublib.CLI.Templates import Confirmation, PrintExecutionStatus
from dublib.Engine.Bus import ExecutionError, ExecutionStatus
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

		Com = Command("exit", "Exit from OtakuBD.")
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

		Com = Command("exit", "Exit from OtakuBD.")
		CommandsList.append(Com)

		Com = Command("open", "Open note.")
		ComPos = Com.create_position("NOTE", "Note identificator.", important = True)
		ComPos.add_argument(ParametersTypes.Number, description = "Note ID.")
		ComPos.add_flag("m", description = "Open note with max ID.")
		CommandsList.append(Com)

		Com = Command("remove", "Remove table.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename table.")
		Com.add_argument(description = "Table name.", important = True)
		CommandsList.append(Com)

		Com = Command("switch", "Switch to other table submodule.")
		Com.add_argument(description = "Submodule name.",)
		CommandsList.append(Com)

		CommandsList += self.__Table.cli.commands

		return CommandsList

	def __GenerateNoteCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: note."""

		CommandsList = list()

		Com = Command("clear", "Clear console.")
		CommandsList.append(Com)

		Com = Command("close", "Close note.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuBD.")
		CommandsList.append(Com)

		Com = Command("remove", "Remove note.")
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

		Status = None

		if command_data.name == "clear":
			Clear()

		elif command_data.name == "close":
			self.__Table = None
			self.__InterpreterLevel = "driver"

		elif command_data.name == "exit":
			self.exit()

		elif command_data.name == "open":
			NoteID = None

			if command_data.check_flag("m") and self.__Table.notes_id:
				NoteID = max(self.__Table.notes_id)
			
			else:
				NoteID = int(command_data.arguments[0])

			Status = self.__OpenNote(NoteID)

		elif command_data.name == "delete":
			Response = Confirmation("Are you sure to delete \"" + self.__Table.name + "\" table?")
			
			if Response:
				Status = self.__Driver.delete_table(self.__Table.name)

				if Status.code == 0:
					self.__Table = None
					self.__InterpreterLevel = "driver"

		elif command_data.name == "rename":
			Status = self.__Table.rename(command_data.arguments[0])

		elif command_data.name == "switch":
			Status = self.__Table.rename(command_data.arguments[0])

		else:
			Status = self.__Table.cli.execute(command_data)

		if Status and Status.check_data("open_note"): 
			Status = self.__OpenNote(Status["note_id"])

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
			self.__InterpreterLevel = "table"

		elif command_data.name == "exit":
			self.exit()

		elif command_data.name == "remove":
			Response = Confirmation("Are you sure to remove #" + str(self.__Note.id) + " note?")
			
			if Response:
				Status = self.__Table.remove_note(self.__Note.id)

				if Status.code == 0:
					self.__Note = None
					self.__InterpreterLevel = "table"

		else:
			Status = self.__Note.cli.execute(command_data)

		PrintExecutionStatus(Status)

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __OpenNote(self, note_id: int) -> ExecutionStatus:
		Status = self.__Table.get_note(note_id)

		if Status.code == 0:
			self.__Note = Status.value
			self.__InterpreterLevel = "note"

		return Status

	def __Selector(self) -> str:
		"""Создаёт идентификатор ввода в зависимости от уровня интерпретации."""

		TableName = "-" + self.__Table.name if self.__Table else ""
		NoteID = "-" + str(self.__Note.id) if self.__Note else ""
		Selector = f"[OtakuBD{TableName}{NoteID}]-> "

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
			Status = ExecutionError(-5, "not_enough_parameters")

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
			"note": self.__GenerateNoteCommands
		}
		self.__Processors = {
			"driver": self.__ProcessDriverCommands,
			"table": self.__ProcessTableCommands,
			"note": self.__ProcessNoteCommands
		}
		self.__Table = None
		self.__Note = None

	def exit(self, print_command: bool = False):
		"""
		Закрывает OtakuBD.
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