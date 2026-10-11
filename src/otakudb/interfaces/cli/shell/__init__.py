import importlib
import shlex
import sys
from types import ModuleType
from typing import TYPE_CHECKING, Literal

from dublib.cli import readline as readline
from dublib.cli.terminalyzer import ModelsGroup, Terminalyzer
from dublib.cli.terminalyzer.helper import Helper
from dublib.functions.system import clear
from dublib.validators import ValidableTypes

from ....core import exceptions
from .. import common
from ..base import viewers
from ..base.processor import BaseCLI
from ..enums import InteractionLevels
from ..exceptions import ObjectUnavailableError
from ..options import CommonInterfaceOptions, InterfaceOptions, TableInterfaceOptions
from .handlers import DriverHandlers
from .printer import Printer
from .prompt import PromptGenerator

if TYPE_CHECKING:
	from dublib.cli.terminalyzer.parser.entities import CommandEntity

	from ....core.session import Session

class Interface:
	"""Interface processor."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def helper(self) -> Helper:
		"""Commands info generator."""

		return self.__helper

	@property
	def level(self) -> InteractionLevels:
		"""Current interaction level."""

		if not self.__session.navigator:
			return InteractionLevels.Driver

		if self.__session.navigator.current_note:
			return InteractionLevels.Note

		if self.__session.navigator.current_table:
			return InteractionLevels.Table

		return InteractionLevels.Box

	@property
	def printer(self) -> Printer:
		"""Output operator."""

		return self.__printer

	@property
	def prompt(self) -> str:
		"""CLI prompt."""

		return self.__prompt_generator.prompt

	@property
	def reserved_groups(self) -> tuple[str, ...]:
		"""Reserved groups names."""

		return (self.__global_group_name,)

	@property
	def session(self) -> "Session":
		"""Interaction session."""

		return self.__session

	@property
	def options(self) -> InterfaceOptions:
		"""Interface options."""

		if not self.__session.navigator or not self.__session.navigator.current_table:
			raise ObjectUnavailableError(InteractionLevels.Table)

		table_options_data = self.__session.navigator.current_table.manifest.interfaces_options
		table_options = TableInterfaceOptions(table_options_data)

		return InterfaceOptions(
			common = self.__common_interface_options,
			table = table_options,
		)

	@property
	def terminalyzer(self) -> Terminalyzer:
		"""Commands processor."""

		return self.__terminalyzer

	#==========================================================================================#
	# >>>>> PRIVATE METHODS <<<<< #
	#==========================================================================================#

	def __get_level_command_groups(self) -> tuple[ModelsGroup, ...]:
		"""
		Return interaction level commands models groups.

		:return: Interaction level commands models groups.
		:rtype: tuple[ModelsGroup, ...]
		"""

		groups: tuple[ModelsGroup, ...] = (self.__global_group,)

		match self.level:

			case InteractionLevels.Box:
				groups += self.__box_cli.groups

			case InteractionLevels.Table:
				groups += self.__common_table_cli.groups + self.__import_commands_groups(InteractionLevels.Table)

			case InteractionLevels.Note:
				groups += self.__common_note_cli.groups + self.__import_commands_groups(InteractionLevels.Note)

		return groups

	def __generate_global_group(self, name: str) -> ModelsGroup:
		"""
		Generate global group.

		:param name: Global group name.
		:type name: str
		:return: Global models group.
		:rtype: ModelsGroup
		"""

		group: ModelsGroup = ModelsGroup(name)

		model = group.create_model("clear", description = "Clear terminal.")
		model.register_handler(self.__handlers.clear)

		model = group.create_model("exit", "Exit from OtakuDB CLI.")
		model.register_handler(self.__handlers.exit)

		model = group.create_model("help", "Show commands list. Add command to more info.")
		model.base.add_argument()
		model.base.add_argument()
		model.register_handler(self.__handlers.help)

		model = group.create_model("mount", "Mount storage directory.")
		position = model.create_position("STORAGE", "Path to storage directory.", important = True)
		position.set_argument(ValidableTypes.ValidPath)
		model.register_handler(self.__handlers.mount)

		return group

	def __import_commands_groups(self, interaction_level: Literal[InteractionLevels.Note, InteractionLevels.Table]) -> tuple[ModelsGroup, ...]:
		"""
		Import note or table commands groups.

		:param interaction_level: Interaction level.
		:type interaction_level: Literal[InteractionLevels.Note, InteractionLevels.Table]
		:return: Note or table commands groups.
		:rtype: tuple[ModelsGroup, ...]
		:raises TypeError: Table CLI has incorrect type.
		"""

		if not self.__session.navigator or not self.__session.navigator.current_table:
			return ()

		table_type: str = self.__session.navigator.current_table.manifest.table_type
		module_path: str = f"otakudb.tables.{table_type}.interfaces.cli.{interaction_level.value}"

		try:
			module: ModuleType = importlib.import_module(module_path)
			ElementCLI: type[BaseCLI] = getattr(module, f"{interaction_level.name}CLI")

		except (ImportError, AttributeError):
			return ()

		if not issubclass(ElementCLI, BaseCLI):
			raise TypeError("Element CLI has incorrect type.")

		return ElementCLI(self).groups

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, session: "Session"):
		"""
		Interface processor.

		:param session: Interaction session.
		:type session: Session
		"""

		self.__session: Session = session

		self.__printer: Printer = Printer()
		self.__common_interface_options: CommonInterfaceOptions = CommonInterfaceOptions(self.__session.data)

		self.__terminalyzer: Terminalyzer = Terminalyzer()
		self.__helper: Helper = Helper()

		self.__handlers: DriverHandlers = DriverHandlers(self)
		self.__prompt_generator: PromptGenerator = PromptGenerator(self.__session)

		self.__global_group_name: str = "Global"
		self.__global_group: ModelsGroup = self.__generate_global_group(self.__global_group_name)

		self.__box_cli: common.BoxCLI = common.BoxCLI(self)
		self.__common_table_cli: common.TableCLI = common.TableCLI(self)
		self.__common_note_cli: common.NoteCLI = common.NoteCLI(self)

		clear()

		if self.__session.data.last_mounted_storage:
			driver = self.__session.mount(self.__session.data.last_mounted_storage)
			self.printer.emit(f"Mounted: \"{driver.storage_path}\".")

	def load_table_viewer(self) -> viewers.BaseTableViewer:
		"""
		Load custom or default table viewer.

		:return: Table viewer.
		:rtype: BaseTableViewer
		:raises ObjectUnavailableError: Object unavailable.
		"""

		if not self.__session.navigator or not self.__session.navigator.current_table:
			raise ObjectUnavailableError(InteractionLevels.Table)

		table_type: str = self.__session.navigator.current_table.manifest.table_type
		module_path: str = f"otakudb.tables.{table_type}.interfaces.cli.table.viewer"

		try:
			module: ModuleType = importlib.import_module(module_path)
			TableViewer: type[viewers.BaseTableViewer] = module.TableViewer

		except (ImportError, AttributeError):
			return viewers.BaseTableViewer(self, self.__session.navigator.current_table.table)

		if not issubclass(TableViewer, viewers.BaseTableViewer):
			raise TypeError("Table viewer has incorrect type.")

		return TableViewer(self, self.__session.navigator.current_table.table)

	def load_note_viewer(self) -> viewers.BaseNoteViewer:
		"""
		Load custom or default note viewer.

		:return: Note viewer.
		:rtype: BaseNoteViewer
		:raises ObjectUnavailableError: Object unavailable.
		:raises StorageUnmountedError: Storage unmounted.
		"""

		if not self.__session.navigator:
			raise exceptions.session.StorageUnmountedError()

		if not self.__session.navigator.current_table:
			raise ObjectUnavailableError(InteractionLevels.Table)

		if not self.__session.navigator.current_note:
			raise ObjectUnavailableError(InteractionLevels.Note)

		table_type: str = self.__session.navigator.current_table.manifest.table_type
		module_path: str = f"otakudb.tables.{table_type}.interfaces.cli.note.viewer"

		try:
			module: ModuleType = importlib.import_module(module_path)
			NoteViewer: type[viewers.BaseNoteViewer] = module.NoteViewer

		except (ImportError, AttributeError):
			return viewers.BaseNoteViewer(self, self.__session.navigator.current_note)

		if not issubclass(NoteViewer, viewers.BaseNoteViewer):
			raise TypeError("Table viewer has incorrect type.")

		return NoteViewer(self, self.__session.navigator.current_note)

	def run(self):
		"""Run CLI processing."""

		while True:
			input_line: str | None = None

			try:
				input_line = input(self.prompt)
			except KeyboardInterrupt:
				print("\nInterrupted by [Ctrl + C] keyboard shortcut.")
				sys.exit()

			input_line = input_line.strip()
			lines: list[str] | None = shlex.split(input_line) if input_line else None

			if lines:
				models_groups: tuple[ModelsGroup, ...] = self.__get_level_command_groups()
				self.__terminalyzer.set_models_groups(models_groups)
				entity: "CommandEntity | None" = self.__terminalyzer.parse_command(lines)

				if entity is None:
					self.printer.error("Command not found.")
