from pathlib import Path
from typing import TYPE_CHECKING

from .. import exceptions
from .box import Box, RootBox
from .table_descriptor import TableDescriptor

if TYPE_CHECKING:
	from ..base.note import BaseNote
	from .driver import Driver

class Navigator:
	"""Navigation operator."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def current_box(self) -> Box | RootBox:
		"""Current box."""

		return self.__current_box

	@property
	def current_item(self) -> Box | RootBox | TableDescriptor:
		"""Current item."""

		return self.__current_table or self.__current_box

	@property
	def current_note(self) -> "BaseNote | None":
		"""Current table note."""

		return self.__current_note

	@property
	def current_table(self) -> TableDescriptor | None:
		"""Descriptor of current table."""

		return self.__current_table
	
	@property
	def root_box(self) -> RootBox:
		"""Root box."""

		return self.__driver.root_box

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver"):
		"""
		Navigation operator.

		:param driver: Storage driver.
		:type driver: Driver
		"""

		self.__driver = driver

		self.__current_box: Box | RootBox = self.__driver.root_box
		self.__current_table: TableDescriptor["BaseNote"] | None = None
		self.__current_note: "BaseNote | None" = None

	def close(self):
		"""Close current item."""
		
		if self.__current_note:
			self.__current_note = None
			return

		if self.__current_table:
			self.__current_table = None
			return

		self.unbox()

	def inbox(self, box_name: str) -> Box:
		"""
		Открывает вложенное хранилище.

		:param box_name: Название хранилища.
		:type box_name: str
		:return: Представление текущего навигации.
		:rtype: Box
		:raises NotBoxError: Target item isn't box.
		"""
		
		item = self.__current_box.get_item(box_name)

		if not isinstance(item, Box):
			raise exceptions.session.navigator.NotBoxError(item.virtual_path)
		
		item.reload()
		self.__current_box = item

		return item

	def navigate(self, virtual_path: Path) -> Box | RootBox | TableDescriptor:
		"""
		Navigate by virtual path.

		:param virtual_path: Virtual path with POSIX standart support.
		:type virtual_path: Path
		:return: Target item.
		:rtype: Box | RootBox | TableDescriptor
		"""

		if virtual_path.is_absolute():
			for part in virtual_path.parts: self.inbox(part)
			return self.__current_box

		navigable_parts: tuple[str, ...] = virtual_path.parts

		for part in navigable_parts:
			if part == "..":
				self.unbox()
				continue

			if self.__driver.is_box(self.__current_box.virtual_path / part):
				self.inbox(part)

			elif part != navigable_parts[-1]:
				raise exceptions.session.navigator.TableNotAtPathEndError(virtual_path)
				
			else:
				self.__current_table = self.open_table(part)
				return self.__current_table

		return self.__current_box

	def open_note(self, note_id: int) -> "BaseNote":
		"""
		Open current table note.

		:param note_id: Note ID.
		:type note_id: int
		:return: Note.
		:rtype: BaseNote
		:raises NotTableError: Target item isn't table.
		"""

		if self.__current_table is None:
			raise exceptions.session.navigator.NotTableError(self.current_item.virtual_path)

		self.__current_note = self.__current_table.table.get_note(note_id)

		return self.__current_note

	def open_table(self, table_name: str) -> TableDescriptor:
		"""
		Open table in current box.

		:param table_name: Table name.
		:type table_name: str
		:return: Table descriptor.
		:rtype: TableDescriptor
		:raises NotTableError: Target item isn't table.
		"""

		item = self.current_box.get_item(table_name)

		if isinstance(item, TableDescriptor):
			item.table.load_data()
			return item

		raise exceptions.session.navigator.NotTableError(item.virtual_path)

	def to_root(self):
		"""Переходит в корневое представление древа навигации."""

		self.root_box.reload()
		self.__current_box = self.root_box

	def unbox(self):
		"""
		Navigate to parent box from current box.

		:raises NotBoxError: Current item isn't box.
		:raises RootUnboxingError: Unable out from storage root box.
		"""

		if self.__current_table:
			raise exceptions.session.navigator.NotBoxError(self.__current_table.virtual_path)

		if type(self.__current_box) is Box:
			self.__current_box = self.__current_box.parent
			self.__current_box.reload()
			return

		raise exceptions.session.navigator.RootUnboxingError()
