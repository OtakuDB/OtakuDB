from dublib.CLI.Terminalyzer import Command, ParsedCommandData
from dublib.CLI.Templates.Bus import PrintError

from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
	from Source.Core.Session.TableDescriptor import TableDescriptor
	from Source.Interfaces.CLI import Interface
	from Source.Core.Session.Box import Box
	from Source.Core.Session import Session

class BaseBoxCLI:
	"""Базовый интерпретатор CLI контейнера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def base_commands(self) -> list[Command]:
		"""Список базовых команд контейнера."""

		CommandsList = list()

		Com = Command("cd", "Change box directory.")
		ComPos = Com.create_position("PATH", "Virtual path to box like POSIX.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("ls", "List box content.")
		CommandsList.append(Com)

		Com = Command("open", "Load table data and open CLI.")
		ComPos = Com.create_position("TABLE", "Name of table.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		return CommandsList

	@property
	def commands(self) -> list[Command]:
		"""Полный список команд интерпретатора."""

		return self.base_commands + self._GenerateCustomCommands()
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def _cd(self, target_path: str):
		"""
		Открывает контейнер по указанному пути.

		:param target_path: Вирутальный путь с поддержкой POSIX стандарта.
		:type target_path: str
		"""

		NewBox = self._Session.navigator.navigate(Path(target_path))
		self._Interface.set_current_object(NewBox)

	def _ls(self):
		"""Выводит содержимое текущего контейнера."""

		Items = self._Session.navigator.current_box.items
		Boxes: list[Box] = list()
		Descriptors: "list[TableDescriptor]" = list()

		for Item in Items:
			if Item.__class__.__name__ == "Box": Boxes.append(Item)
			else: Descriptors.append(Item)

		Boxes = sorted(Boxes, key = lambda CurrentBox: CurrentBox.name)
		Descriptors = sorted(Descriptors, key = lambda CurrentDescriptor: CurrentDescriptor.name)
		
		for CurrentBox in Boxes: print("📁", CurrentBox.name)
		for CurrentDescriptor in Descriptors: print("📦", CurrentDescriptor.name)

	def _open(self, table_name: str):
		"""
		Загружает данные таблицы и открывает её CLI.

		:param table_name: Имя таблицы.
		:type table_name: str
		"""

		CurrentBox = self._Session.navigator.current_box
		Descriptor: "TableDescriptor | None" = None
		
		try:
			Descriptor = CurrentBox.get_item(table_name)

			if Descriptor.__class__.__name__ == "Box":
				PrintError(f"Object \"{table_name}\" is box. Unable to use load operation.")
				return

		except KeyError:
			PrintError(f"Current box doesn't contain table \"{table_name}\".")
			return
		
		Descriptor.table.load_data()
		self._Interface.set_current_object(Descriptor.table)

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
			case "cd": self._cd(command.get_position_value("PATH"))
			case "ls": self._ls()
			case "open": self._open(command.get_position_value("TABLE"))

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

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, session: "Session", interface: Interface, box: "Box"):
		"""
		Базовый интерпретатор CLI контейнера.

		:param session: Сессия взаимодействия.
		:type session: Session
		:param interface: Интерфейс CLI.
		:type interface: Interface
		"""

		self._Session = session
		self._Interface = interface
		self._Box = box

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