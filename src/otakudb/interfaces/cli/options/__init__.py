from dataclasses import dataclass

from .common import CommonInterfaceOptions
from .table import TableInterfaceOptions

@dataclass(frozen = True)
class InterfaceOptions:
	"""Interface options."""

	common: CommonInterfaceOptions
	table: TableInterfaceOptions
