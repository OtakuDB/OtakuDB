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

	def mount(self, entity: "CommandEntity"):
		"""
		Command handler: **mount**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		storage_path: Path = entity.get_position_value("STORAGE", expected_type = Path, important = True)
		self._session.mount(storage_path)