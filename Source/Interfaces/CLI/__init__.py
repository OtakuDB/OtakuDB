from .Base import BaseBoxCLI, BaseTableCLI, BaseNoteCLI
from .Options.Local import TableInterfaceOptions
from .Enums import InterractionLevels

from dublib.CLI.Terminalyzer import Command, ParametersTypes,ParsedCommandData, Terminalyzer
from dublib.CLI.Templates.Bus import PrintCritical, PrintError
from dublib.CLI.TextStyler import Codes, TextStyler
from dublib.Methods.System import Clear
from dublib.CLI import readline
from dublib import Exceptions

from typing import TYPE_CHECKING
from types import ModuleType
from pathlib import Path
from os import PathLike
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

		Com = Command("clear", "Clear terminal.", "Global")
		CommandsList.append(Com)

		Com = Command("exit", "Exit from OtakuBD CLI.", "Global")
		CommandsList.append(Com)

		Com = Command("mount", "Mount storage directory.", "Global")
		ComPos = Com.create_position("PATH", "Path to storage directory.", important = True)
		ComPos.set_argument(ParametersTypes.ValidPath)
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
			case "mount": self.__MountStorage(command.get_position_value("PATH"))

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

		try:
			Module = importlib.import_module(f"Source.Tables.{table_type}.interfaces.cli")
			Module.TableCLI
			Module.NoteCLI
		except ImportError: PrintCritical(f"Table \"{table_type}\" doesn't support CLI.")
		except AttributeError: PrintCritical(f"Table \"{table_type}\" doesn't provide all CLI interpretators.")

		return Module

	def __MountStorage(self, path: PathLike):
		"""
		Монтирует директорию хранилища.

		:param path: Путь к директории хранилища.
		:type path: PathLike
		"""

		try:
			self.__Session.mount(path)
			self.set_current_object(self.__Session.navigator.current_box)

		except ZeroDivisionError: PrintError("Storage directory not found.")

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
			Analyzer.helper.set_category("Global")
			CommandData = Analyzer.check_commands(self.__GetInterractionLevelCommands())

			if not CommandData: PrintError("Command not found.")
			else: return CommandData

		except Exceptions.CLI.Terminalyzer.NotEnoughParameters: PrintError("Not enough parameters.", origin = "CLI")
		except Exceptions.CLI.Terminalyzer.InvalidParameterType: PrintError("Invalid parameter type.", origin = "CLI")
		except Exceptions.CLI.Terminalyzer.TooManyParameters: PrintError("Too many parameters.", origin = "CLI")
		except Exception as ExceptionData: PrintError(str(ExceptionData), origin = type(ExceptionData).__qualname__)

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

		self.__InterractionLevel = InterractionLevels.Driver
		self.__Interpreter: BaseBoxCLI | BaseTableCLI | BaseNoteCLI | None = None
		self.__CurrentObject = None

		Clear()
		print("OtakuDB v0.2.0-beta")

		if self.__Session.data.last_mounted_storage:
			self.__MountStorage(self.__Session.data.last_mounted_storage)
			print(f"Mounted: \"{self.__Driver.storage_directory}\".")

	def get_selector_string(self) -> str:
		"""
		Возвращает строку-индикатор ввода.

		:return: Строка-индикатор ввода.
		:rtype: str
		"""

		BoldGreen = TextStyler(decorations = Codes.Decorations.Bold, text_color = Codes.Colors.Green)
		if not self.__Session.navigator: return BoldGreen.get_styled_text("(DRIVER) -> ")

		Storage = ""
		VirtualPath = Path()
		Note = ""

		if self.__Driver.storage_directory: Storage = self.__Driver.storage_directory.name
		if self.__Session.navigator.current_box: VirtualPath = self.__Session.navigator.current_box.virtual_path


		if self.__InterractionLevel == InterractionLevels.Table:
			VirtualPath = VirtualPath / self.__CurrentObject.name

		elif self.__InterractionLevel == InterractionLevels.Note:
			VirtualPath = VirtualPath / self.__CurrentObject.table.name
			Note = str(self.__CurrentObject.id)

		VirtualPath = VirtualPath.as_posix()
		if VirtualPath == ".": VirtualPath = ""
		Selector = "-".join((Storage, VirtualPath, Note)).strip("-")

		return BoldGreen.get_styled_text(f"{Selector} -> ")

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

			case "Box" | "RootBox":
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
					self.__Interpreter.validate()

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