from typing import TYPE_CHECKING, NoReturn

from ....core import exceptions
from ..enums import InteractionLevels
from ..exceptions import ObjectUnavailableError

if TYPE_CHECKING:
	from ....core.base.note import BaseNote
	from ....core.base.table import BaseTable
	from ....core.session import Session
	from ....core.session.driver import Driver
	from ....core.session.navigator import Navigator
	from ..shell import Interface
	from ..shell.printer import Printer

class BaseHandlersCollection:
	"""Base handlers collection."""

	@property
	def driver(self) -> "Driver":
		"""
		Storage driver.

		:raises StorageUnmountedError: Storage unmounted.
		"""

		return self._session.driver or self._raise_unmounted_error()

	@property
	def navigator(self) -> "Navigator":
		"""
		Navigation operator.

		:raises StorageUnmountedError: Storage unmounted.
		"""

		return self._session.navigator or self._raise_unmounted_error()

	@property
	def note(self) -> "BaseNote":
		"""
		Current note.
		
		:raises ObjectUnavailableError: Note unavailable.
		"""

		if not self.navigator.current_note:
			raise ObjectUnavailableError(InteractionLevels.Note)

		return self.navigator.current_note

	@property
	def printer(self) -> "Printer":
		"""Output operator."""

		return self._interface.printer

	@property
	def table(self) -> "BaseTable":
		"""
		Current table.
		
		:raises ObjectUnavailableError: Table unavailable.
		"""

		if not self.navigator.current_table:
			raise ObjectUnavailableError(InteractionLevels.Table)

		return self.navigator.current_table.table

	def _raise_unmounted_error(self) -> NoReturn:
		"""
		Raise storage unmounted error.

		:raises StorageUnmountedError: Storage unmounted.
		"""

		raise exceptions.session.StorageUnmountedError()

	def __init__(self, interface: "Interface"):
		"""
		Base handlers collection.

		:param interface: Interface processor.
		:type interface: Session
		"""
		
		self._interface: Interface = interface

		self._session: Session = self._interface.session
