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
		Command handler: **go**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		virtual_path: Path = entity.get_position_value("PATH", expected_type = Path, important = True)
		self.navigator.navigate(virtual_path)

	def mkdir(self, entity: "CommandEntity"):
		"""
		Command handler: **mkdir**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		name: str = entity.get_position_value("NAME", expected_type = str, important = True)
		is_open: bool = entity.check_flag("-o")

		box = self.navigator.current_box.create_box(name)

		if is_open:
			self.navigator.navigate(box.virtual_path)

	def ls(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **ls**.

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

	def rmdir(self, entity: "CommandEntity"):
		"""
		Command handler: **rmdir**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		name: str = entity.get_position_value("NAME", expected_type = str, important = True)
		is_purge: bool = entity.check_flag("-p")

		box = self.navigator.current_box.get_box(name)
		box.delete(is_purge)

	def types(self, entity: "CommandEntity"): # noqa: ARG002
		"""
		Command handler: **types**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		tables_types: tuple[str, ...] = self.driver.available_tables_types

		if tables_types:
			self.printer.emit(", ".join(tables_types))

		else:
			self.printer.emit("No available tables types.")