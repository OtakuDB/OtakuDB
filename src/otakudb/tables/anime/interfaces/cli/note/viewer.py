from typing import TYPE_CHECKING

from dublib.cli.text_styler import TextStyler, codes
from dublib.functions.data import stringify_float

from otakudb.interfaces.cli.base.viewers.note import BaseNoteViewer

from ....note.enums import PartStatuses, Statuses

if TYPE_CHECKING:
	from ....note import Note as Note
	from ....table import Table as Table

class NoteViewer(BaseNoteViewer["Note"]):
	"""Note viewer."""

	def _view_note(self):  # noqa: C901
		"""View note."""

		#---> Объявление стилей.
		#==========================================================================================#
		BOLD = TextStyler(decorations = codes.Decorations.Bold)
		ITALIC = TextStyler(decorations = codes.Decorations.Italic)
		GRAY = TextStyler(text_color = codes.Colors.Gray)

		#---> Генерация литералов.
		#==========================================================================================#
		TotalProgress = stringify_float(self.note.progress * 100.0)
		TotalProgress = f" ({TotalProgress}% viewed)"
		StatusEmoji: str = {
			Statuses.Announced: "ℹ️",
			Statuses.Watching: "▶️",
			Statuses.Completed: "✅",
			Statuses.Dropped: "⛔",
			Statuses.Planned: "🗓️",
			None: "",
		}[self.note.status]


		#---> Вывод данных записи.
		#==========================================================================================#
		if self.note.name:
			self.printer.emit(BOLD.get_styled_text(self.note.name), end_line = False)

		self.printer.emit(f"{TotalProgress} {StatusEmoji}")

		if self.note.estimation:
			self.printer.emit(f"⭐ {self.note.estimation} / {self.note.table.manifest.custom.max_estimation}")

		if self.note.another_names:
			self.printer.emit(BOLD.get_styled_text("ANOTHER NAMES:"))

			for AnotherName in self.note.another_names:
				self.printer.emit(ITALIC.get_styled_text(" " * 4 + AnotherName))

		if self.note.tags:
			self.printer.emit(BOLD.get_styled_text("TAGS: "), end_line = False)
			self.printer.emit(", ".join(self.note.tags))

		#---> Вывод данных частей.
		#==========================================================================================#
		Parts = self.note.parts
		if not Parts: return
		self.printer.emit(BOLD.get_styled_text("PARTS:"))

		PartsCount = len(Parts)
		PartsDigits = len(str(PartsCount))

		for Index in range(PartsCount):
			Part = Parts[Index]

			#---> Генерация литералов.
			#==========================================================================================#
			PartNumber = f" {Part.number}" if Part.number else ""
			PartName = f" {Part.name}" if Part.name else ""

			PartStatusEmoji = {
				PartStatuses.Announced: " ℹ️",
				PartStatuses.Skipped: " 🚫",
				PartStatuses.Unwatched: "",
				PartStatuses.Watching: " ▶️",
				PartStatuses.Watched: " ✅",
			}[Part.status]
			PartColor = {
				PartStatuses.Announced: codes.Colors.Cyan,
				PartStatuses.Skipped: codes.Colors.Blue,
				PartStatuses.Unwatched: None,
				PartStatuses.Watching: codes.Colors.Yellow,
				PartStatuses.Watched: codes.Colors.Green,
			}[Part.status]

			Series = ""
			if Part.series:
				if Part.status == PartStatuses.Watching:
					PartProgress = stringify_float(Part.progress * 100.0)
					PartProgress = f" ({PartProgress}% viewed)"
					Series = f"{Part.viewed} / {Part.series} series {PartProgress}"

				elif Part.series > 1: Series = f"{Part.series} series"

			#---> Вывод данных части.
			#==========================================================================================#
			IndexString = str(Index).rjust(PartsDigits)
			self.printer.emit(TextStyler(text_color = PartColor).get_styled_text(" " * 4 + f"{IndexString} ▸ {Part.type.value}{PartNumber}:{PartName}{PartStatusEmoji}"))

			if Series:
				self.printer.emit(TextStyler(text_color = PartColor).get_styled_text(" " * 12 + Series))

			if Part.comment:
				self.printer.emit(" " * 12 + GRAY.get_styled_text(f"💭 {Part.comment}"))
