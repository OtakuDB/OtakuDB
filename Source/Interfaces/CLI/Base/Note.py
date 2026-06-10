from Source.Interfaces.CLI.Templates import PrintTable
from Source.Interfaces.CLI.Functions import Unstar
from Source.Core import Exceptions

from dublib.CLI.Terminalyzer import Command, ParametersTypes, ParsedCommandData
from dublib.CLI.Templates.Bus import PrintError, PrintWarning
from dublib.CLI.Templates import Confirmation
from dublib.CLI.TextStyler import FastStyler

from typing import TYPE_CHECKING
from pathlib import Path

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

		Com = Command("view", "View note.")
		CommandsList.append(Com)

		#---> Динамические команды: вложения.
		#==========================================================================================#
		
		if self._Note.table.manifest.attachments.rule > 0:
			Com = Command("attach", "Attach file to note.")
			ComPos = Com.create_position("FILE", description = "Path to file.", important = True)
			ComPos.set_argument(ParametersTypes.ValidPath)
			Com.base.add_key("--slot", description = "Slot name to attaching.")
			Com.base.add_flag("-c", description = "Attach copy of file.")
			CommandsList.append(Com)

			Com = Command("slots", "Print slots descriptions.")
			CommandsList.append(Com)

			Com = Command("unattach", "Attach file to note.")
			ComPos = Com.create_position("TARGET", description = "Target to unattaching.", important = True)
			ComPos.add_key("--slot", description = "Slot name to clear.")
			ComPos.set_argument()
			CommandsList.append(Com)

		#---> Динамические команды: метаданные.
		#==========================================================================================#
		if self._Note.table.manifest.metainfo_rules.rule:
			Com = Command("metafields", "Prints metainfo fields data.", "Metainfo")
			CommandsList.append(Com)

			Com = Command("metainfo", "Manage metainfo.", "Metainfo")
			ComPos = Com.create_position("FIELD", "Metainfo field name.", important = True)
			ComPos.set_argument()
			ComPos = Com.create_position("OPERATION", "Operation for metafield processing.", important = True)
			ComPos.add_flag("-c", description = "Clear field.")
			ComPos.add_key("--set", description = "Set field value.")
			ComPos.add_key("--append", description = "Append string or separated by ; string to same type field.")
			ComPos.add_key("--remove", description = "Remove string or separated by ; string from same type field.")
			CommandsList.append(Com)

		#---> Динамические команды: связи.
		#==========================================================================================#
		if self._Note.table.manifest.connections.bonds.names:
			Com = Command("bind", "Bint another note to current.")
			ComPos = Com.create_position("BOND_NAME", description = "Name of bond.", important = True)
			ComPos.set_argument()
			ComPos = Com.create_position("NOTE", description = "ID of current table note.", important = True)
			ComPos.set_argument(ParametersTypes.UnsignedInteger)
			Com.base.add_flag("-r", description = "Remove binding.")
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

	def _attach(self, path: str, slot: str | None, copy: bool):
		"""
		Прикрепляет вложение.

		:param path: Путь к вложению.
		:type path: str
		:param slot: Имя слота для прикрепления.
		:type slot: str | None
		:param copy: Указывает, нужно ли скопировать файл или переместить.
		:type copy: bool
		"""

		path = Path(path)

		try:
			if slot: self._Note.attachments.get_slot(slot).attach(path, copy)
			else: self._Note.attachments.attach(path, copy)
		except Exceptions.Note.AttachmentSlotAlreadyFilled: PrintError(f"Slot \"{slot}\" already filled.")
		except Exceptions.Note.AttachmentsDenied as ExceptionData: PrintError(ExceptionData)
		except Exceptions.Note.AttachmentSlotNotDescribed: PrintError(f"Slot \"{slot}\" not described in manifest.")

	def _bind(self, bond_name: str, note_id: int, remove: bool):
		"""
		Привязывает другую запись к текущей внутри той же таблицы.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param note_id: ID привязываемой записи.
		:type note_id: int
		:param remove: Указывает, нужно ли добавить связь или удалить.
		:type remove: bool
		"""
		
		try:
			if remove: self._Note.bonds.unbind(bond_name, note_id)
			else: self._Note.bonds.bind(bond_name, note_id)

		except Exceptions.Table.NoteNotFound: PrintError(f"Note with ID #{note_id} not found.")
		except Exceptions.Note.BondNotDescribed: PrintError(f"Bind connection \"{bond_name}\" not described in manifest.")
		except Exceptions.Note.MaxBindedNotesCountReached as ExceptionData: PrintError(ExceptionData)

	def _delete(self, confirm: bool = False):
		"""
		Удаляет таблицу.

		:param confirm: Отключает подтверждение удаления.
		:type confirm: bool
		"""
		
		if not confirm and not Confirmation("This note will be deleted."): return
		self._Note.delete()
		self._Interface.set_current_object(self._Note.table)

	def _metainfo(self, command: ParsedCommandData):
		"""
		Обрабатывает операцию с метаданными.
		
		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		Field = command.get_position_value("FIELD")

		try:
			if command.check_flag("-c"): self._Note.metainfo.clear_field(Field)
			elif command.check_key("--set"): self._Note.metainfo.set_field_value(Field, command.get_key_value("--set"))
			elif command.check_key("--append"): self._Note.metainfo.append_to_field(Field, command.get_key_value("--append"))
			elif command.check_key("--remove"): self._Note.metainfo.remove_from_field(Field, command.get_key_value("--remove"))

		except Exception as ExceptionData: PrintError(ExceptionData)

	def _metafields(self):
		"""Выводит описание полей метаданных."""

		MetainfoRules = self._Note.table.manifest.metainfo_rules

		FreeFieldsStatus = MetainfoRules.is_free_allowed
		if FreeFieldsStatus: FreeFieldsStatus = FastStyler("enabled").colorize.green
		else: FreeFieldsStatus = FastStyler("disabled").colorize.red
		print("Free fields:", FreeFieldsStatus)

		for Field in MetainfoRules.fields:
			print()
			print(FastStyler(Field.name).decorate.bold)
			print("Description:", FastStyler(Field.description).decorate.italic)
			
			Values = Field.values
			if Values != None:
				print("Values:")
				for Value in Values: print(" " * 4 + f" > {Value}")

	def _rename(self, name: str | None):
		"""
		Переименовывает запись.

		:param name: Имя записи.
		:type name: str | None
		"""

		if name:
			for CurrentNote in self._Note.table.notes:
				if CurrentNote.name == name:
					PrintWarning(f"Note #{CurrentNote.id} has same name.")

		self._Note.rename(name)

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

		for CurrentSlotInfo in SlotsInfo:
			Columns["Slot"].append(CurrentSlotInfo.name)
			Columns["Description"].append(CurrentSlotInfo.description or "")

		PrintTable(Columns, sort_by = "Slot")

	def _unattach(self, command: ParsedCommandData):
		"""
		Открепляет вложение.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		if command.check_key("--slot"):
			Slot = command.get_key_value("--slot")
			try: self._Note.attachments.get_slot(Slot).clear()
			except Exceptions.Note.AttachmentSlotNotDescribed: PrintError(f"Slot \"{Slot}\" not described in manifest.")

		else: self._Note.attachments.unnatach(command.get_position_value("TARGET"))

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
			case "attach": self._attach(command.get_position_value("FILE"), command.get_key_value("--slot"), command.check_flag("-c"))
			case "bind": self._bind(command.get_position_value("NOTE"), command.check_flag("-r"))
			case "close": self._Interface.set_current_object(self._Note.table)
			case "delete": self._delete(command.check_flag("-y"))
			case "metafields": self._metafields()
			case "metainfo": self._metainfo(command)
			case "rename": self._rename(Unstar(command.get_position_value("NAME")))
			case "view": self.view()
			case "slots": self._slots()
			case "unattach": self._unattach(command)

	def _SetMetainfo(self, key: str, value: int | float | str | None):
		"""
		Устанавливает значение поля метаданных, обрабатывая ошибки.

		:param key: Имя поля.
		:type key: str
		:param value: Значение. Символ `*` или `0` приводится к `None`.
		:type value: int | float | str | None
		"""

		if value in (0, "*"): value = None
		try: self._Note.metainfo.set_field_value(key, value)
		except Exceptions.Note.MetainfoBlocked as ExceptionData: PrintError(ExceptionData)

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

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ ПРОСМОТРА СОДЕРЖИМОГО <<<<< #
	#==========================================================================================#

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
			if Field not in self._Note.table.manifest.metainfo_rules.fields_names: Field = FastStyler(Field).colorize.blue

			if type(Value) == tuple:
				print(" " * 4 + f"{Field}:")
				for Element in Value: print(" " * 9 + f" > {Element}")

			else: print(" " * 4 + f"{Field}: {Value}")

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
	
	def validate(self):
		"""Производит валидацию записи и выводит результат в терминал."""

		for Error in self._Note.attachments.validate():
			Slot = f" on slot \"{Error.slot}\"" if Error.slot else ""
			PrintWarning(f"Attachment file \"{Error.file}\"{Slot} missing.")

	def view(self):
		"""Отображает запись."""

		self._ViewNote()
		if self._Note.metainfo.has_values: self._ViewMetainfo()
		if self._Note.attachments.count: self._ViewAttachments()
		