from collections.abc import Sequence
from typing import TYPE_CHECKING, NoReturn, cast, overload

from ....core import exceptions
from ....core.base.note.metainfo import SUPPORTED_TYPES
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

class BaseHandlersCollection[T: "BaseTable", N: "BaseNote"]:
	"""Base handlers collection."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def driver(self) -> "Driver":
		"""
		Storage driver.

		:raises StorageUnmountedError: Storage unmounted.
		"""

		return self._session.driver or self._raise_unmounted_error()

	@property
	def interface(self) -> "Interface":
		"""Interface processor."""

		return self._interface

	@property
	def navigator(self) -> "Navigator":
		"""
		Navigation operator.

		:raises StorageUnmountedError: Storage unmounted.
		"""

		return self._session.navigator or self._raise_unmounted_error()

	@property
	def note(self) -> N:
		"""
		Current note.

		:raises ObjectUnavailableError: Note unavailable.
		"""

		if not self.navigator.current_note:
			raise ObjectUnavailableError(InteractionLevels.Note)

		return cast(N, self.navigator.current_note)

	@property
	def printer(self) -> "Printer":
		"""Output operator."""

		return self._interface.printer

	@property
	def table(self) -> T:
		"""
		Current table.

		:raises ObjectUnavailableError: Table unavailable.
		"""

		if not self.navigator.current_table:
			raise ObjectUnavailableError(InteractionLevels.Table)

		return cast(T, self.navigator.current_table.table)

	#==========================================================================================#
	# >>>>> PROTECTED METHODS <<<<< #
	#==========================================================================================#

	def _raise_unmounted_error(self) -> NoReturn:
		"""
		Raise storage unmounted error.

		:raises StorageUnmountedError: Storage unmounted.
		"""

		raise exceptions.session.StorageUnmountedError()

	def _set_metainfo(self, field: str, value: SUPPORTED_TYPES | Sequence[SUPPORTED_TYPES] | None):
		"""
		Set metainfo field value from command entity.

		:param field: Field name.
		:type field: str
		:param value: Field value. String with only one character `*` will be transformed to `None`.
		:type value: SUPPORTED_TYPES | Sequence[SUPPORTED_TYPES] | None
		"""

		value = self._unstar(value)
		self.note.metainfo.set_field_value(field, value)

	@overload
	def _unstar(self, value: str) -> str | None: ...
	@overload
	def _unstar[V](self, value: V) -> V: ...

	def _unstar[V](self, value: V) -> V | None:
		"""
		Transform string with only one character `*` to `None`.

		:param value: Value.
		:type value: V
		:return: Value or `None`.
		:rtype: V | None
		"""

		if value == "*":
			return None

		return value

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, interface: "Interface"):
		"""
		Base handlers collection.

		:param interface: Interface processor.
		:type interface: Session
		"""

		self._interface: Interface = interface

		self._session: Session = self._interface.session
