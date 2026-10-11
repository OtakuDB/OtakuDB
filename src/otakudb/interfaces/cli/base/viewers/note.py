from typing import TYPE_CHECKING

from dublib.cli.text_styler import FastStyler

if TYPE_CHECKING:
	from .....core.base.note import BaseNote
	from ...shell import Interface
	from ...shell.printer import Printer

ALLOWED_TYPES = float | int | str | None

class BaseNoteViewer[N: "BaseNote"]:
	"""Base note viewer."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def printer(self) -> "Printer":
		"""Output printer."""

		return self._interface.printer

	@property
	def note(self) -> N:
		"""Note."""

		return self._note

	#==========================================================================================#
	# >>>>> PROTECTED METHODS <<<<< #
	#==========================================================================================#

	def _validate_attachments(self):
		"""Validate note attachments."""

		for error in self.note.attachments.validate():
			slot: str = f" on slot \"{error.slot}\"" if error.slot else ""
			self.printer.warning(f"Attachment file \"{error.file}\"{slot} missing.")

	#==========================================================================================#
	# >>>>> OVERRIDABLE METHODS <<<<< #
	#==========================================================================================#

	def _view_attachments(self):
		"""View attachments."""

		self.printer.emit(FastStyler("ATTACHMENTS:").decorate.bold)

		for slot in self.note.attachments.slots:
			if not slot.file: continue
			file: str = FastStyler(slot.file).decorate.italic
			self.printer.emit(" " * 4 + f"{slot.name}: {file}")

	def _view_metainfo(self):
		"""View metainfo."""

		self.printer.emit(FastStyler("METAINFO:").decorate.bold)

		for field in self.note.metainfo.fields:
			value = self.note.metainfo.get_field_value(field)

			if value is None: continue
			if field not in self.note.table.manifest.metainfo_rules.fields_names:
				field = FastStyler(field).colorize.blue

			if isinstance(value, tuple):
				self.printer.emit(" " * 4 + f"{field}:")
				for element in value: self.printer.emit(" " * 9 + f" > {element}")

			else: self.printer.emit(" " * 4 + f"{field}: {value}")

	def _view_note(self):
		"""View note."""

		name: str | None = self.note.name

		if name:
			self.printer.emit(name)

		self.printer.emit(f"ID: {self.note.id}")

	def _post_init(self):
		"""Execute after instance initialization."""

		pass

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, interface: "Interface", note: N):
		"""
		Base note viewer.

		:param interface: Interface processor.
		:type interface: Interface
		:param note: Base note.
		:type note: BaseNote
		"""

		self._interface: Interface = interface
		self._note: N = note

		self._post_init()

	def view(self, validate: bool = True):
		"""View note."""

		if self._interface.options.common.autoclear: self.printer.clear()
		if validate: self._validate_attachments()

		self._view_note()
		if self.note.metainfo.has_values: self._view_metainfo()
		if self.note.attachments.count: self._validate_attachments()

