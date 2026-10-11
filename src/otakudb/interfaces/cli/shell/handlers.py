import sys
from pathlib import Path
from typing import TYPE_CHECKING

from dublib.functions.system import clear

from ..base.handlers import BaseHandlersCollection

if TYPE_CHECKING:
	from dublib.cli.terminalyzer.parser.entities import CommandEntity

class DriverHandlers(BaseHandlersCollection):
	"""Driver level commands handlers."""

	def clear(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **clear**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		clear()

	def exit(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **exit**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		sys.exit()

	def help(self, entity: "CommandEntity"):
		"""
		Command handler: **help**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		arguments = entity.arguments

		if arguments:
			identifier: tuple[str, ...] = tuple(str(value) for value in entity.arguments)
			model = self._interface.terminalyzer.find_model(identifier)

			if not model:
				self.printer.error("Info for command not found.")
				return

			self.printer.emit(self._interface.helper.generate_model_info(model))

		else:
			self.printer.emit(self._interface.helper.generate_groups_list(self._interface.terminalyzer.groups))

	def mount(self, entity: "CommandEntity"):
		"""
		Command handler: **mount**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		storage_path: Path = entity.get_position_value("STORAGE", expected_type = Path, important = True)
		self._session.mount(storage_path)
