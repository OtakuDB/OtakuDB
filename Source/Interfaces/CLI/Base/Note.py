from Source.Interfaces.CLI.Templates import PrintTable
from Source.Interfaces.CLI.Functions import Unstar

from dublib.CLI.Terminalyzer import Command, ParsedCommandData
from dublib.CLI.Templates import Confirmation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from Source.Interfaces.CLI import Interface
	from Source.Core.Base.Note import BaseNote
	from Source.Core.Session import Session

class BaseNoteCLI:
	"""Базовый интерпретатор CLI записи."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def base_commands(self) -> list[Command]:
		"""Список базовых команд контейнера."""

		CommandsList = list()

		Com = Command("close", "Close note.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete note.")
		Com.base.add_flag("-y", description = "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename note.")
		ComPos = Com.create_position("NAME", "New note name or * to clear.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("slots", "Print slots descriptions.")
		CommandsList.append(Com)

		Com = Command("view", "View note.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def commands(self) -> list[Command]:
		"""Полный список команд интерпретатора."""

		return self.base_commands + self._GenerateCustomCommands()
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def _delete(self, confirm: bool = False):
		"""
		Удаляет таблицу.

		:param confirm: Отключает подтверждение удаления.
		:type confirm: bool
		"""
		
		if not confirm and not Confirmation("This note will be deleted."): return
		self._Note.delete()
		self._Interface.set_current_object(self._Note.table)

	def _slots(self):
		"""Выводит описания слотов."""

		SlotsInfo = self._Note.table.manifest.attachments.slots

		if not SlotsInfo:
			print("Slots info not provided.")
			return
		
		Columns = {
			"Slot": list(),
			"Description": list()
		}

		for Name, Description in SlotsInfo.items():
			Columns["Slot"].append(Name)
			Columns["Description"].append(Description or "")

		PrintTable(Columns, sort_by = "Slot")

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
			case "close": self._Interface.set_current_object(self._Note.table)
			case "delete": self._delete(command.check_flag("-y"))
			case "rename": self._Note.rename(Unstar(command.get_position_value("NAME")))
			case "view": self.view()
			case "slots": self._slots()

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

	def _ViewNote(self):
		"""Отображает запись."""

		NoteName = self._Note.name or ""
		if NoteName: NoteName = NoteName + " "
		print(f"{NoteName}#{self._Note.id}")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, session: "Session", interface: Interface, note: "BaseNote"):
		"""
		Базовый интерпретатор CLI записи.

		:param session: Сессия взаимодействия.
		:type session: Session
		:param interface: Интерфейс CLI.
		:type interface: Interface
		"""

		self._Session = session
		self._Interface = interface
		self._Note = note

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
	
	def view(self):
		"""Отображает запись."""

		self._ViewNote()