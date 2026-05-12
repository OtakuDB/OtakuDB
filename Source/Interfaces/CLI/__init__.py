from .Base import BaseBoxCLI, BaseTableCLI, BaseNoteCLI
from .Enums import InterractionLevels

from dublib.CLI.Terminalyzer import Command, ParametersTypes,ParsedCommandData, Terminalyzer
from dublib.CLI.Templates.Bus import PrintCritical, PrintError
from dublib.Exceptions import CLI as TerminalyzerExceptions
from dublib.CLI.TextStyler import FastStyler
from dublib.Methods.System import Clear
from dublib.CLI import readline

from typing import TYPE_CHECKING
from types import ModuleType
from pathlib import Path
import importlib
import shlex

if TYPE_CHECKING:
	from Source.Core.Base.Table import BaseTable, BaseNote
	from Source.Core.Session.Box import Box
	from Source.Core.Session import Session

class Interface:
	"""Обработчик интерфейса командной строки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def global_commands(self) -> list[Command]:
		"""Список глобальных команд."""

		CommandsList = list()

		Com = Command("clear", "Clear terminal.")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuBD CLI.")
		CommandsList.append(Com)

		Com = Command("mount", "Mount storage directory.")
		ComPos = Com.create_position("PATH", "Path to storage directory.", important = True)
		ComPos.add_argument(ParametersTypes.ValidPath)
		CommandsList.append(Com)

		return CommandsList

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Execute(self, command: ParsedCommandData):
		"""
		Обрабатывает команду.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		if not self.__ExecuteGlobalCommands(command): self.__Interpreter.execute(command)

	def __ExecuteGlobalCommands(self, command: ParsedCommandData) -> bool:
		"""
		Обрабатывает глобальные команды.

		:param command: Данные команды.
		:type command: ParsedCommandData
		:return: Возвращает `True`, если команда была сопоставлена по имени с глобальной.
		:rtype: bool
		"""

		match command.name:
			case "clear": Clear()
			case "exit": exit()

			case "mount":

				try:
					self.__Driver.mount(command.arguments[0])
					print(f"Mounted: \"{self.__Driver.storage_directory}\".")

				except FileNotFoundError: print("Storage directory not found.")

		return command.name in tuple(CurrentCommand.name for CurrentCommand in self.global_commands)

	def __GetInterractionLevelCommands(self) -> list[Command]:
		"""
		Возвращает набор команд для текущего уровня взаимодействия.

		:return: Набор команд для текущего уровня взаимодействия.
		:rtype: list[Command]
		"""

		if self.__InterractionLevel == InterractionLevels.Driver: return self.global_commands
		else: return self.global_commands + self.__Interpreter.commands

	def __ImportModuleCLI(self, table_type: str) -> ModuleType | None:
		"""
		Импортирует модуль CLI целевой таблицы.

		:param table_type: Тип таблицы.
		:type table_type: str
		:return: Модуль CLI таблицы.
		:rtype: ModuleType | None
		"""

		Module: ModuleType | None = None

		try: Module = importlib.import_module(f"Source.Tables.{table_type}.interfaces.cli")
		except ImportError: PrintCritical(f"Table \"{table_type}\" doesn't support CLI.")

		try:
			Module.TableCLI
			Module.NoteCLI
		except AttributeError: PrintCritical(f"Table \"{table_type}\" doesn't provide all CLI interpretators.")

		return Module

	def __ParseCommandData(self, parameters: list[str]) -> ParsedCommandData | None:
		"""
		Парсит команду.

		:param parameters: Список параметров.
		:type parameters: list[str]
		:return: Данные команды или `None` в случае ошибки.
		:rtype: ParsedCommandData | None
		"""

		try:
			Analyzer = Terminalyzer(parameters)
			Analyzer.helper.enable()
			Analyzer.helper.enable_sorting()
			CommandData = Analyzer.check_commands(self.__GetInterractionLevelCommands())

			if not CommandData: PrintError("Command not found.")
			else: return CommandData

		except TerminalyzerExceptions.NotEnoughParameters: PrintError("Not enough parameters.", origin = "terminalyzer")
		except TerminalyzerExceptions.InvalidParameterType: PrintError("Invalid parameter type.", origin = "terminalyzer")
		except TerminalyzerExceptions.TooManyParameters: print("too_many_parameters")
		except TerminalyzerExceptions.UnknownFlag: print("unknown_flag")
		except TerminalyzerExceptions.UnknownKey: print("unknown_key")
		except TerminalyzerExceptions.MutuallyExclusiveParameters: print("mutually_exclusive_parameters")
		except ZeroDivisionError as ExceptionData:
			Type = type(ExceptionData).__qualname__
			print(f"{Type}: {ExceptionData}")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, session: "Session"):
		"""
		Обработчик интерфейса командной строки.

		:param session: Сессия.
		:type session: Session
		"""

		self.__Session = session

		self.__Driver = self.__Session.driver
		self.__Navigator = self.__Session.navigator

		self.__InterractionLevel = InterractionLevels.Driver
		self.__Interpreter: BaseBoxCLI | BaseTableCLI | BaseNoteCLI | None = None
		self.__CurrentObject = None

		Clear()
		print("OtakuDB v0.2.0-alpha")

		if self.__Driver.storage_directory:
			print(f"Mounted: \"{self.__Driver.storage_directory}\".")
			self.set_current_object(self.__Navigator.current_box)

	def get_selector_string(self) -> str:
		"""
		Возвращает строку-индикатор ввода.

		:return: Строка-индикатор ввода.
		:rtype: str
		"""

		Storage = ""
		VirtualPath = Path()
		Note = ""

		if self.__Driver.storage_directory: Storage = self.__Driver.storage_directory.name
		if self.__Navigator.current_box: VirtualPath = self.__Navigator.current_box.path


		if self.__InterractionLevel == InterractionLevels.Table:
			VirtualPath = VirtualPath / self.__CurrentObject.name

		elif self.__InterractionLevel == InterractionLevels.Note:
			VirtualPath = VirtualPath / self.__CurrentObject.table.name
			Note = str(self.__CurrentObject.id)

		VirtualPath = VirtualPath.as_posix()
		if VirtualPath == ".": VirtualPath = ""
		Selector = "-".join((Storage, VirtualPath, Note)).strip("-")

		return FastStyler(f"{Selector} -> ").decorate.bold

	def set_current_object(self, object: "Box | BaseTable | BaseNote | None"):
		"""
		Устанавливает текущий рабочий объект.

		:param object: Текущий рабочий объект.
		:type object: Box | BaseTable | BaseNote | None
		"""

		self.__CurrentObject = object

		match object.__class__.__name__:

			case None:
				self.__InterractionLevel = InterractionLevels.Driver
				self.__Interpreter = None

			case "Box":
				object: "Box"
				self.__InterractionLevel = InterractionLevels.Box
				self.__Interpreter = BaseBoxCLI(self.__Session, self, object)

			case "Table":
				object: "BaseTable"
				Module = self.__ImportModuleCLI(object.manifest.type)

				if Module:
					self.__Interpreter = Module.TableCLI(self.__Session, self, object)
					self.__InterractionLevel = InterractionLevels.Table

			case "Note":
				object: "BaseNote"
				Module = self.__ImportModuleCLI(object.table.manifest.type)

				if Module:
					self.__Interpreter = Module.NoteCLI(self.__Session, self, object)
					self.__InterractionLevel = InterractionLevels.Note

	def run(self):
		"""Запускает CLI."""

		while True:
			InputLine = None

			try: InputLine = input(self.get_selector_string())
			except KeyboardInterrupt: 
				print("exit")
				exit()

			InputLine = InputLine.strip()
			InputLine = shlex.split(InputLine) if len(InputLine) > 0 else None

			if InputLine:
				CommandData = self.__ParseCommandData(InputLine)
				if CommandData: self.__Execute(CommandData)