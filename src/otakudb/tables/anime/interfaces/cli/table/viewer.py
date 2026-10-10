from typing import TYPE_CHECKING

from dublib.cli.text_styler import FastStyler

from otakudb.interfaces.cli.base.viewers.table import ALLOWED_TYPES, BaseTableViewer

from ....note.enums import Statuses

if TYPE_CHECKING:
	from ....note import Note as Note
	from ....table import Table as Table

class TableViewer(BaseTableViewer["Table", "Note"]):
	"""Table viewer."""

	#==========================================================================================#
	# >>>>> OVERRIDABLE METHODS <<<<< #
	#==========================================================================================#

	def _fill_row(self, row_data: dict[str, ALLOWED_TYPES], note: "Note"):
		"""
		Fill table row by data dictionary editing.

		:param row_data: Table row data dictionary in which key is column name and value is cell value.
		:type row_data: dict[str, ALLOWED_TYPES]
		:param note: Note.
		:type note: Note
		"""

		row_data["ID"] = note.id

		status = note.status
		match status:
			case Statuses.Announced: row_data["Status"] = FastStyler(status.value).colorize.magenta
			case Statuses.Planned: row_data["Status"] = FastStyler(status.value).colorize.cyan
			case Statuses.Watching: row_data["Status"] = FastStyler(status.value).colorize.yellow
			case Statuses.Completed: row_data["Status"] = FastStyler(status.value).colorize.green
			case Statuses.Dropped: row_data["Status"] = FastStyler(status.value).colorize.red

		row_data["Name"] = note.name
		row_data["Base"] = self._get_metainfo(note, "base")
		row_data["Estimation"] = note.estimation
