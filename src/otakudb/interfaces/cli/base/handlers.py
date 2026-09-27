from typing import TYPE_CHECKING, NoReturn

from ....core import exceptions

if TYPE_CHECKING:
	from ....core.session import Session
	from ....core.session.driver import Driver
	from ....core.session.navigator import Navigator
	from ..shell import Interface

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
