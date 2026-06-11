from ..Options.Local import TableInterfaceOptions

from Source.Core import Exceptions

from dublib.CLI.Terminalyzer import Command, ValidableTypes, ParsedCommandData
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

		Com = Command("cd", "Change directory (box).")
		ComPos = Com.create_position("PATH", "Virtual path to box like POSIX.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("create", "Create table.")
		ComPos = Com.create_position("TYPE", "Type of table.", important = True)
		ComPos.set_argument(ValidableTypes.Alpha)
		ComPos = Com.create_position("NAME", "Name of table. Used type name as default.")
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("ls", "List box content.")
		CommandsList.append(Com)

		Com = Command("mkdir", "Make directory (box).")
		ComPos = Com.create_position("NAME", "Name of box.", important = True)
		ComPos.set_argument()
		Com.base.add_flag("-o", description = "Go to new box after creation.")
		CommandsList.append(Com)

		Com = Command("open", "Load table data and open CLI.")
		ComPos = Com.create_position("TABLE", "Name of table.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("rmdir", "Delete directory (box). By default only for empty boxes.")
		ComPos = Com.create_position("NAME", "Name of box.", important = True)
		ComPos.set_argument()
		Com.base.add_flag("-p", description = "Purge all data in box if exists.")
		CommandsList.append(Com)

		Com = Command("tables", "Prints all tables types.")
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

		try:
			NewBox = self._Session.navigator.navigate(Path(target_path))
			self._Interface.set_current_object(NewBox)

		except Exceptions.Driver.ItemNotFound as ExceptionData: PrintError(f"Item not found by path: \"{ExceptionData}\".")

	def _create(self, table_type: str, name: str | None):
		"""
		Создаёт новую таблицу.

		:param table_type: Тип таблицы.
		:type table_type: str
		:param name: Имя таблицы. По умолчанию будет использован тип.
		:type name: str | None
		"""

		Name = name or table_type
		
		try:
			Descriptor = self._Session.navigator.current_box.create_table(Name, table_type)
			TIO = TableInterfaceOptions(Descriptor.manifest.interfaces_options)
			TIO.save()

		except Exceptions.Driver.ItemAlreadyExists: PrintError("Item already exists.")
		except Exceptions.Driver.IncorrectTableType: PrintError(f"Missing \"{table_type}\" table type.")

	def _mkdir(self, name: str, open: bool):
		"""
		Создаёт контейнер.

		:param name: Имя контейнера.
		:type name: str
		:param open: Указывает, нужно ли перейти в новый контейнер после создания.
		:type open: bool
		"""
		
		try:
			NewBox = self._Session.driver.create_box(self._Session.navigator.current_box, name)
			if open: self._Interface.set_current_object(NewBox)

		except FileExistsError: PrintError("Item with same name already exists.")

	def _ls(self):
		"""Выводит содержимое текущего контейнера."""

		CurrentBox = self._Session.navigator.current_box
		Boxes: list[Box] = list()
		Descriptors: "list[TableDescriptor]" = list()


		for Item in CurrentBox.items:
			if Item.__class__.__name__ == "Box": Boxes.append(Item)
			else: Descriptors.append(Item)

		Boxes = sorted(Boxes, key = lambda CurrentBox: CurrentBox.name)
		Descriptors = sorted(Descriptors, key = lambda CurrentDescriptor: CurrentDescriptor.name)
		
		if CurrentBox.virtual_path != Path(): print("↩️  ..")
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

	def _rmdir(self, name: str, purge: bool):
		"""
		Удаляет контейнер.

		:param name: Имя контейнера.
		:type name: str
		:param purge: Указывает, нужно ли удалить содержимое контейнера, если он не пуст.
		:type purge: bool
		"""
		
		
		CurrentBox = self._Session.navigator.current_box
		TargetBox: Box | None = None

		try: 
			Item = CurrentBox.get_item(name)

			if self._Session.driver.is_box(Item.virtual_path): TargetBox = Item
			else:
				PrintError("Unable delete table, only boxes.")
				return

		except KeyError:
			PrintError("Box not found.")
			return
		
		try:
			TargetBox.delete(purge)
			self._Interface.set_current_object(TargetBox.parent)

		except Exceptions.Driver.BoxNotEmpty: PrintError("Box isn't empty.")
		except Exceptions.Driver.ItemNotFound: PrintError("Item not found.")

	def _tables(self):
		"""Выводит список доступных типов таблиц."""

		Types = self._Session.driver.tables_types

		if not Types: print("No tables available.")
		else: print(", ".join(Types))

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
			case "create": self._create(command.get_position_value("TYPE"), command.get_position_value("NAME"))
			case "mkdir": self._mkdir(command.get_position_value("NAME"), command.check_flag("-o"))
			case "ls": self._ls()
			case "open": self._open(command.get_position_value("TABLE"))
			case "rmdir": self._rmdir(command.get_position_value("NAME"))
			case "tables": self._tables()

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