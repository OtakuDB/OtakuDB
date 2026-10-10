from pathlib import Path
from typing import TYPE_CHECKING

from ....core.session.box import Box, RootBox
from ..base.handlers import BaseHandlersCollection

if TYPE_CHECKING:
	from dublib.cli.terminalyzer.parser.entities import CommandEntity

	from ....core.session.table_descriptor import TableDescriptor

class BoxHandlers(BaseHandlersCollection):
	"""Box commands handlers."""

	def go(self, entity: "CommandEntity"):
		"""
		Navigate by virtual path.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		virtual_path: Path = entity.get_position_value("PATH", expected_type = Path, important = True)
		self.navigator.navigate(virtual_path)

	def ls(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		List box items.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		current_box: Box | RootBox = self.navigator.current_box
		boxes: list[Box] = []
		descriptors: list[TableDescriptor] = []

		for item in current_box.items:
			if isinstance(item, Box): boxes.append(item)
			else: descriptors.append(item)

		boxes = sorted(boxes, key = lambda box: box.name)
		descriptors = sorted(descriptors, key = lambda descriptor: descriptor.name)
		
		if current_box.virtual_path != Path(): self.printer.emit("↩️  ..")
		for box in boxes: self.printer.emit(f"📁 {box.name}")
		for descriptor in descriptors: self.printer.emit(f"📦 {descriptor.name}")

	def types(self, entity: "CommandEntity"): # noqa: ARG002
		"""
		Command handler: **types**.

		:param entity: Command entity.
		:type entity: CommandEntity
		:param session: Interaction session.
		:type session: Session
		"""

		tables_types: tuple[str, ...] = self.driver.available_tables_types

		if tables_types:
			self.printer.emit(", ".join(tables_types))

		else:
			self.printer.emit("No available tables types.")