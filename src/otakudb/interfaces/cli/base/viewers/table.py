from typing import TYPE_CHECKING

from prettytable import PLAIN_COLUMNS, PrettyTable

from dublib.cli.text_styler import FastStyler

if TYPE_CHECKING:
	from .....core.base.note import BaseNote
	from .....core.base.note.metainfo import SUPPORTED_TYPES
	from .....core.base.table import BaseTable
	from ...options import ColumnOptions
	from ...shell import Interface
	from ...shell.printer import Printer

ALLOWED_TYPES = float | int | str | None

class BaseTableViewer[T: "BaseTable", N: "BaseNote"]:
	"""Base table viewer."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def printer(self) -> "Printer":
		"""Output printer."""

		return self._interface.printer

	@property
	def table(self) -> T:
		"""Table."""

		return self._table

	#==========================================================================================#
	# >>>>> PROTECTED METHODS <<<<< #
	#==========================================================================================#

	# To-Do: run on _print_table() side?
	def _get_metainfo(self, note: N, field: str) -> str | None:
		"""
		Generate metainfo value representation as string.

		:param note: Note
		:type note: BaseNote
		:param field: Metainfo field name.
		:type field: str
		:return: Metainfo value as string.
		:rtype: str | None
		"""

		value: SUPPORTED_TYPES | tuple[SUPPORTED_TYPES, ...] | None = note.metainfo.get_field_value(field)

		if value is None:
			value = ""

		elif isinstance(value, tuple):
			values_count: int = len(value)
			value = str(value[0])

			other_count: int = values_count - 1
			other_label: str = f" (and {other_count} other)"

			if other_count:
				value += other_label

		else: 
			value = str(value)

		return value

	def _print_table(self, data: dict[str, list[ALLOWED_TYPES]], options: dict[str, "ColumnOptions"], sort_by = "ID"):
		"""
		Build and print notes table.

		:param data: Columns data dictionary in which key is column name and value is cell value.
		:type data: dict[str, list[ALLOWED_TYPES]]
		:param options: Columns options.
		:type options: dict[str, ColumnOptions]
		:param sort_by: Column name to sorting.
		:type sort_by: str
		"""

		table: PrettyTable = PrettyTable()
		table.set_style(PLAIN_COLUMNS)

		for column in data.keys():
			current_options: "ColumnOptions" = options[column]

			if not current_options.is_enabled:
				continue

			values: list[ALLOWED_TYPES] = data[column]

			if current_options.max_width:
				for index in range(len(values)):
					value: ALLOWED_TYPES = values[index]

					if value is None: value = ""
					else: value = str(value)

					if len(value) > current_options.max_width:
						value = value[:current_options.max_width].rstrip() + "…"

			header: str = FastStyler(column).decorate.bold
			table.add_column(header, values)

		table.align = "l"

		if sort_by:
			table.sortby = FastStyler(sort_by).decorate.bold

		self.printer.emit(table.get_string())

	def _search_notes(self, notes: tuple[N, ...], search_query: str) -> tuple[N, ...]:
		"""
		Seqrch notes by check is query in searchable strings.

		:param notes: Notes sequence.
		:type notes: tuple[N, ...]
		:param search_query: Seqrch quesry. Case insensitive.
		:type search_query: str
		:return: Search results.
		:rtype: tuple[N, ...]
		"""

		search_query = search_query.lower()
	
		return tuple(
			note for note in notes 
			if any(search_query in string.lower() for string in note.searchable_strings)
		)

	#==========================================================================================#
	# >>>>> OVERRIDABLE METHODS <<<<< #
	#==========================================================================================#

	def _fill_row(self, row_data: dict[str, ALLOWED_TYPES], note: N):
		"""
		Fill table row by data dictionary editing.

		:param row_data: Table row data dictionary in which key is column name and value is cell value.
		:type row_data: dict[str, ALLOWED_TYPES]
		:param note: Note.
		:type note: BaseNote
		"""

		row_data["ID"] = note.id
		row_data["Name"] = note.name

	def _no_search_results(self):
		"""Execute if notes not found by search query."""

		self.printer.emit("No results.")

	def _post_init(self):
		"""Execute after instance initialization."""

		pass

	def _table_is_empty(self):
		"""Execute if table is empty."""

		self.printer.emit("Table is empty.")

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, interface: "Interface", table: T):
		"""
		Base table viewer.

		:param interface: Interface processor.
		:type interface: Interface
		:param table: Base table.
		:type table: BaseTable
		"""

		self._interface: Interface = interface
		self._table: T = table

		self._post_init()

	def view(self, search_query: str | None = None, reverse: bool = False, sort_by: str = "ID"):
		"""
		Print notes list.

		:param search_query: Search query (will be scanned by notes searchable strings).
		:type search_query: str | None, optional
		:param reverse: Reverse notes order.
		:type reverse: bool
		:param sort_by: Column name to sorting.
		:type sort_by: str
		"""

		notes: tuple[N, ...] = self._table.notes

		if not notes:
			self._table_is_empty()
			return

		if search_query:
			notes = self._search_notes(notes, search_query)

		if not notes:
			self._no_search_results()
			return

		if reverse:
			notes = tuple(reversed(notes))

		columns_options: dict[str, ColumnOptions] = self._interface.table_interface_options.columns
		columns_data: dict[str, list[ALLOWED_TYPES]] = {column: [] for column in columns_options.keys()}

		for note in notes:
			row_data: dict[str, ALLOWED_TYPES] = dict.fromkeys(columns_options.keys())
			self._fill_row(row_data, note)
			
			for column in columns_data.keys():
				value: ALLOWED_TYPES = row_data.get(column)
				if value is None: value = ""
				columns_data[column].append(value)

		self._print_table(columns_data, columns_options, sort_by = sort_by)