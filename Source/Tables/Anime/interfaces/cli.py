from ..note.Enums import Bases, Statusses

from Source.Interfaces.CLI.Base import BaseTableCLI, BaseNoteCLI
from Source.Interfaces.CLI.Functions import Unstar

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.TextStyler import FastStyler

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..note import Note

class TableCLI(BaseTableCLI):
	"""Интерпретатор CLI таблицы."""

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

	def _GenerateTableRow(self, container: dict[str, None], note: "Note") -> dict[str, str | None]:
		"""
		Генерирует данные для заполнения строки таблицы.

		:param container: Словарь, в котром ключи являются названиями колонок.
		:type container: dict[str, None]
		:param note: Запись.
		:type note: Note
		:return: Словарь с подставленными значениями.
		:rtype: dict[str, str | None]
		"""

		container["ID"] = note.id

		NoteStatus = note.status
		match NoteStatus:
			case Statusses.Announced: NoteStatus = FastStyler(NoteStatus.value).colorize.magenta
			case Statusses.Planned: NoteStatus = FastStyler(NoteStatus.value).colorize.cyan
			case Statusses.Watching: NoteStatus = FastStyler(NoteStatus.value).colorize.yellow
			case Statusses.Completed: NoteStatus = FastStyler(NoteStatus.value).colorize.green
			case Statusses.Dropped: NoteStatus = FastStyler(NoteStatus.value).colorize.red
		container["Status"] = NoteStatus

		container["Name"] = note.name
		container["Base"] = note.metainfo["base"]
		container["Estimation"] = note.estimation

		return container

class NoteCLI(BaseNoteCLI):
	"""Интерпретатор CLI записи."""

	def _ExecuteCustomCommand(self, command: ParsedCommandData):
		"""
		Обрабатывает кастомную команду.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		match command.name:
			case "base": self._Note.metainfo.set_field_value("base", Unstar(command.get_position_value("VALUE")))

	def _GenerateCustomCommands(self) -> list[Command]:
		"""
		Возвращает список кастомных команд интерпретатора.

		:return: Возвращает список кастомных команд интерпретатора.
		:rtype: list[Command]
		"""

		CommandsList = list()

		Com = Command("base", "Set anime base.", "Metainfo")
		BaesesNames = ", ".join(Element.value for Element in Bases)
		ComPos = Com.create_position("VALUE", description = f"One of values: {BaesesNames}. Put * to clear.", important = True)
		ComPos.set_argument(ParametersTypes.Alpha)
		CommandsList.append(Com)

		return CommandsList

	def _ViewNote(self):
		"""Отображает запись."""

		NoteName = self._Note.name or ""
		if NoteName: NoteName = NoteName + " "
		print(f"{NoteName}#{self._Note.id}")
