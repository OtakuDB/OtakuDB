import shlex
import sys
from typing import TYPE_CHECKING

from dublib.cli.terminalyzer import ModelsGroup, Terminalyzer
from dublib.functions.system import clear
from dublib.validators import ValidableTypes

from ..box import BoxCLI
from ..enums import InterractionLevels
from .handlers import DriverHandlers
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
	def level(self) -> InterractionLevels:
		"""Current interaction level."""

		return self.__level

	@property
	def reserved_groups(self) -> tuple[str, ...]:
		"""Reserved groups names."""

		return (self.__global_group_name,)

	@property
	def prompt(self) -> str:
		"""CLI prompt."""
		
		return self.__prompt_generator.prompt

	@property
	def session(self) -> "Session":
		"""Interaction session."""

		return self.__session

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

		match self.__level:
			case InterractionLevels.Box: groups += self.__box_cli.groups

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

		model = group.create_model("mount", "Mount storage directory.")
		position = model.create_position("STORAGE", "Path to storage directory.", important = True)
		position.set_argument(ValidableTypes.ValidPath)
		model.register_handler(self.__handlers.mount)

		return group


	# def __import_cli_module(self, table_type: str, level: InterractionLevels) -> ModuleType | None:
	# 	"""
	# 	Импортирует модуль CLI целевой таблицы.

	# 	:param table_type: Тип таблицы.
	# 	:type table_type: str
	# 	:return: Модуль CLI таблицы.
	# 	:rtype: ModuleType | None
	# 	"""

	# 	module: ModuleType | None = None

	# 	try:
	# 		module = importlib.import_module(f"otakudb.tables.{table_type}.interfaces.cli")
	# 		module.TableCLI
	# 		module.NoteCLI
	# 	except ImportError: PrintCritical(f"Table \"{table_type}\" doesn't support CLI.")
	# 	except AttributeError: PrintCritical(f"Table \"{table_type}\" doesn't provide all CLI interpretators.")

	# 	return module

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

		self.__terminalyzer: Terminalyzer = Terminalyzer()
		self.__handlers: DriverHandlers = DriverHandlers(self)
		self.__level: InterractionLevels = InterractionLevels.Driver
		self.__prompt_generator: PromptGenerator = PromptGenerator(self.__session)
		
		self.__global_group_name: str = "Global"
		self.__global_group: ModelsGroup = self.__generate_global_group(self.__global_group_name)

		self.__box_cli: BoxCLI = BoxCLI(self)

		clear()

		if self.__session.data.last_mounted_storage:
			driver = self.__session.mount(self.__session.data.last_mounted_storage)
			self.__level = InterractionLevels.Box
			print(f"Mounted: \"{driver.storage_path}\".")

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
					print("Command not found.")
