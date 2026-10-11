from typing import TYPE_CHECKING, override

from dublib.validators import ValidableTypes

from otakudb.interfaces.cli.base.note import BaseNoteCLI

from ....note.enums import Bases, PartsTypes
from .handlers import NoteHandlers

if TYPE_CHECKING:
	from dublib.cli.terminalyzer import ModelsGroup

	from ....note import Note as Note
	from ....table import Table as Table

class NoteCLI(BaseNoteCLI["Table", "Note", NoteHandlers]):
	"""Table CLI processor."""

	@override
	def _build_note_models(self, group: "ModelsGroup"):
		"""Build note models and register handlers."""

		model = group.create_model("altname", "Manage alternative names.")
		position = model.create_position("ALT_NAME", "Alternative name.", important = True)
		position.set_argument()
		model.base.add_flag("-r", description = "Remove another name if exists.")
		model.register_handler(self.handlers.altname)

		model = group.create_model("base", "Set anime base.")
		bases: str = ", ".join(element.value for element in Bases)
		position = model.create_position("VALUE", description = f"One of values: {bases}. Put * to clear.", important = True)
		position.set_argument(ValidableTypes.Alpha)
		# group.create_modelsList.append(Com)

		model = group.create_model("delpart", "Delete part.")
		position = model.create_position("INDEX", "Part index.", important = True)
		position.set_argument(ValidableTypes.Integer)
		model.base.add_flag("-y", description = "Automatically confirms deletion.")
		model.register_handler(self.handlers.delpart)

		model = group.create_model("drop", "Switch drop status")
		model.register_handler(self.handlers.drop)

		model = group.create_model("editpart", "Edit part data.")
		position = model.create_position("INDEX", "Part index.", important = True)
		position.set_argument(ValidableTypes.Integer)
		position = model.create_position("STATUS", "Status of viewing.")
		position.add_flag("-a", description = "Mark part as announced.")
		position.add_flag("-s", description = "Mark part as skipped.")
		position.add_flag("-u", description = "Mark part as unwatched.")
		position.add_flag("-w", description = "Mark part as fully watched.")
		model.base.add_key("--comment", description = "Comment to part. Put * to clear.")
		model.base.add_key("--name", description = "Name of part. Put * to clear.")
		model.base.add_key("--number", value_type = ValidableTypes.Number, description = "Number of part. Not index! Put 0 to clear.")
		model.base.add_key("--series", value_type = ValidableTypes.Integer, description = "Series count. Put 0 to clear.")
		model.register_handler(self.handlers.editpart)

		model = group.create_model("estimate", "Set estimation.")
		MaxEstimation = self.note.table.manifest.custom.max_estimation
		position = model.create_position("ESTIMATION", f"Estimation from 1 to {MaxEstimation}. Put 0 to clear.", important = True)
		position.set_argument(ValidableTypes.Integer)
		model.register_handler(self.handlers.estimate)

		model = group.create_model("mark", "Set mark of viewing progress to part.")
		position = model.create_position("INDEX", "Part index.", important = True)
		position.set_argument(ValidableTypes.Integer)
		position = model.create_position("MARK", "Last watched episode number.", important = True)
		position.set_argument(ValidableTypes.Integer)
		model.register_handler(self.handlers.mark)

		model = group.create_model("move", "Move part.")
		position = model.create_position("INDEX", "Part index.", important = True)
		position.set_argument(ValidableTypes.Integer)
		position = model.create_position("OPERATION", "Operation type.", important = True)
		position.add_flag("-up", description = "Up part (index decrease).")
		position.add_key("--up", value_type = ValidableTypes.Integer, description = "Up part several times (index decrease).")
		position.add_flag("-down", description = "Down part (index increase).")
		position.add_key("--down", value_type = ValidableTypes.Integer, description = "Down part several times (index increase).")
		model.register_handler(self.handlers.move)

		model = group.create_model("newpart", "Create new part.")
		types: str = ", ".join(part_type.value for part_type in PartsTypes)
		position = model.create_position("TYPE", f"Type of part: {types}.", important = True)
		position.set_argument(ValidableTypes.Alpha)
		model.register_handler(self.handlers.newpart)

		model = group.create_model("ptypes", "Prints list of parts types.")
		model.register_handler(self.handlers.ptypes)

		model = group.create_model("tag", "Manage tags.")
		position = model.create_position("TAG", "Tag name.", important = True)
		position.set_argument()
		model.base.add_flag("-r", description = "Remove tag.")
		model.register_handler(self.handlers.tag)

	@override
	def _export_handlers(self) -> type[NoteHandlers]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[NoteHandlers]
		"""

		return NoteHandlers
