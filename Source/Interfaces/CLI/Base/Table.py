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