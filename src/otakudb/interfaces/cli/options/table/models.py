from typing import Any

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

__all__ = ["ColumnOptions", "TableInterfaceOptionsModel"]

@dataclass
class ColumnOptions:
	"""Column options."""

	is_enabled: bool = True
	max_width: int | None = None

class TableInterfaceOptionsModel(BaseModel):
	"""Table interface options model."""

	columns: dict[str, ColumnOptions] = {
		"ID": ColumnOptions(True, None),
		"Name": ColumnOptions(True, None),
	}
	custom: dict[str, Any] = {}
