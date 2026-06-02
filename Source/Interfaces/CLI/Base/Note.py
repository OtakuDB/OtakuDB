from Source.Interfaces.CLI.Templates import PrintTable
from Source.Interfaces.CLI.Functions import Unstar
from Source.Core import Exceptions

from dublib.CLI.Terminalyzer import Command, ParametersTypes, ParsedCommandData
from dublib.CLI.Templates.Bus import PrintError
from dublib.CLI.Templates import Confirmation
from dublib.CLI.TextStyler import FastStyler

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
		
		if self._Note.table.manifest.common.binds:
			Com = Command("bind", "Bint another note to current.")
			ComPos = Com.create_position("NOTE", description = "ID of current table note.", important = True)
			ComPos.set_argument(ParametersTypes.UnsignedInteger)
			Com.base.add_flag("-r", description = "Remove binding.")
			CommandsList.append(Com)

		Com = Command("delete", "Delete note.")
		Com.base.add_flag("-y", description = "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename note.")
		ComPos = Com.create_position("NAME", "New note name or * to clear.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		if self._Note.table.manifest.attachments.slots:
			Com = Command("slots", "Print slots descriptions.")
			CommandsList.append(Com)

		Com = Command("view", "View note.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def commands(self) -> list[Command]:
		"""Полный список команд интерпретатора."""

		CustomCommands = self._GenerateCustomCommands()
		for Index in range(len(CustomCommands)):
			if not CustomCommands[Index].category: CustomCommands[Index].set_category("Note")

		return self.base_commands + CustomCommands
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def _bind(self, note_id: int, remove: bool):
		"""
		Привязывает другую запись к текущей внутри той же таблицы.

		:param note_id: ID привязываемой записи.
		:type note_id: int
		:param remove: Указывает, нужно ли добавить связь или удалить.
		:type remove: bool
		"""
		
		try:
			TargetNote = self._Note.table.get_note(note_id)
			if remove: self._Note.table.binder.local.unbind(self._Note.id, TargetNote.id)
			else: self._Note.table.binder.local.bind(self._Note.id, TargetNote.id)

		except Exceptions.Table.NoteNotFound: PrintError(f"Note with ID #{note_id} not found.")
		except Exceptions.Note.LocalBindsDenied: PrintError("Same table notes binding denied.")

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
			case "bind": self._bind(command.get_position_value("NOTE"), command.check_flag("-r"))
			case "close": self._Interface.set_current_object(self._Note.table)
			case "delete": self._delete(command.check_flag("-y"))
			case "rename": self._Note.rename(Unstar(command.get_position_value("NAME")))
			case "view": self.view()
			case "slots": self._slots()

	def _SetMetainfo(self, key: str, value: int | float | str | None):
		"""
		Устанавливает значение поля метаданных, обрабатывая ошибки.

		:param key: Имя поля.
		:type key: str
		:param value: Значение. Символ `*` приводится к `None`.
		:type value: int | float | str | None
		"""

		try: self._Note.metainfo.set_field_value(key, Unstar(value))
		except Exceptions.Note.MetainfoBlocked: PrintError("Metainfo blocked by manifest rule.")

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

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _ViewAttachments(self):
		"""Выводит данные вложений."""

		print(FastStyler("ATTACHMENTS:").decorate.bold)

		for Slot in self._Note.attachments.slots:
			File = FastStyler(Slot.file).decorate.italic
			print(" " * 4 + f"{Slot.name}: {File}")

	def _ViewMetainfo(self):
		"""Выводит значения полей метаданных."""

		print(FastStyler(f"METAINFO:").decorate.bold)
		
		for Field in self._Note.metainfo.fields:
			Value = self._Note.metainfo[Field]
			if Value == None: continue
			if Field not in self._Note.table.manifest.metainfo_rules.fields: Field = FastStyler(Field).colorize.blue
			print(" " * 4 + f"{Field}: {Value}")

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

		self._PostInitMethod()

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
		if self._Note.metainfo.has_values: self._ViewMetainfo()
		if self._Note.attachments.count: self._ViewAttachments()
		