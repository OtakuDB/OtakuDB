from typing import TYPE_CHECKING, Literal

from otakudb.interfaces.cli.base.handlers import BaseHandlersCollection

from ....note.enums import PartsTypes

if TYPE_CHECKING:
	from dublib.cli.terminalyzer.parser.entities import CommandEntity

	from ....note import Note as Note
	from ....note.part import Part
	from ....table import Table as Table

class NoteHandlers(BaseHandlersCollection["Table", "Note"]):
	"""Note handlers."""

	def altname(self, entity: "CommandEntity"):
		"""
		Command handler: **altname**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		name: str = entity.get_position_value("ALT_NAME", expected_type = str, important = True)
		is_remove: bool = entity.check_flag("-r")

		if is_remove: self.note.remove_another_name(name)
		else: self.note.add_another_name(name)

	def base(self, entity: "CommandEntity"):
		"""
		Command handler: **base**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		base: str = entity.get_position_value("BASE", expected_type = str, important = True)
		self._set_metainfo("base", base)

	def delpart(self, entity: "CommandEntity"):
		"""
		Command handler: **delpart**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		index: int = entity.get_position_value("INDEX", expected_type = int, important = True)

		try:
			self.note.remove_part(index)
		except IndexError:
			self.printer.error(f"Part with index {index} not found.")

	def drop(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **drop**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		self.note.drop()

	def editpart(self, entity: "CommandEntity"):  # noqa: C901
		"""
		Command handler: **editpart**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		index: int = entity.get_position_value("INDEX", expected_type = int, important = True)
		part: Part | None = None

		try:
			part = self.note.get_part(index)
		except IndexError:
			self.printer.error(f"Part with index {index} not found.")
			return

		if entity.check_key("--name"):
			part.rename(self._unstar(entity.get_key_value("--name", expected_type = str)))

		if entity.check_key("--comment"):
			part.set_comment(self._unstar(entity.get_key_value("--comment", expected_type = str)))

		if entity.check_key("--number"):
			part.set_number(entity.get_key_value("--number", expected_type = int) or None)

		if entity.check_key("--series"):
			series: int | None = entity.get_key_value("--series", expected_type = int) or None

			try:
				part.set_series_count(series)
			except ValueError as exception:
				self.printer.error(exception)

		status_flag: str | None = entity.get_position_value("STATUS", expected_type = str)

		if status_flag:
			try:
				match status_flag:
					case "-a": part.set_viewed(-2)
					case "-s": part.set_viewed(-1)
					case "-u": part.set_viewed(0)
					case "-w":
						if not part.series:
							self.printer.warning("No series count specified to mark as fully watched.")
						else:
							part.set_viewed(part.series)

			except ValueError as exception:
				self.printer.error(exception)

	def estimate(self, entity: "CommandEntity"):
		"""
		Command handler: **estimate**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		estimation: int = entity.get_position_value("ESTIMATION", expected_type = int, important = True)

		try:
			self.note.estimate(estimation or None)
		except ValueError as exception:
			self.printer.error(exception)

	def mark(self, entity: "CommandEntity"):
		"""
		Command handler: **mark**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		index: int = entity.get_position_value("INDEX", expected_type = int, important = True)
		mark: int = entity.get_position_value("MARK", expected_type = int, important = True)

		part: Part | None = None

		try:
			part = self.note.get_part(index)
		except IndexError:
			self.printer.error(f"Part with index {index} not found.")
			return

		if part.type is PartsTypes.Film and mark > 1:
			mark = 1

		try:
			part.set_viewed(mark)
		except ValueError as exception:
			self.printer.error(exception)

	def move(self, entity: "CommandEntity"):
		"""
		Command handler: **move**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		index: int = entity.get_position_value("INDEX", expected_type = int, important = True)
		operation: Literal["up", "down"] | None = None
		count: int | None = None

		try:
			self.note.get_part(index)
		except IndexError:
			self.printer.error(f"Part with index {index} not found.")
			return

		if entity.check_flag("-up"):
			operation = "up"
		elif entity.check_key("--up"): operation, count = "up", entity.get_key_value("--up", expected_type = int)
		elif entity.check_flag("-down"): operation = "down"
		elif entity.check_key("--down"): operation, count = "down", entity.get_key_value("--up", expected_type = int)

		if count is None:
			count = 1

		try:
			match operation:
				case "up": self.note.up_part(index, count)
				case "down": self.note.down_part(index, count)

		except ValueError:
			self.printer.error("Incorrect operations count.")

	def newpart(self, entity: "CommandEntity"):
		"""
		Command handler: **newpart**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		part_type_name: str = entity.get_position_value("TYPE", expected_type = str, important = True)

		try:
			part_type = PartsTypes(part_type_name)

		except Exception:
			self.printer.error(f"Unsupported type \"{part_type_name}\".")
			return

		index: int = self.note.create_part(part_type)
		self.printer.emit(f"Created {part_type.value} with index {index}.")

	def ptypes(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **ptypes**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		self.printer.emit(", ".join(str(element) for element in PartsTypes))

	def tag(self, entity: "CommandEntity"):
		"""
		Command handler: **tag**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		tag: str = entity.get_position_value("TAG", expected_type = str, important = True)
		is_remove: bool = entity.check_flag("-r")

		if is_remove: self.note.remove_tag(tag)
		else: self.note.add_tag(tag)

