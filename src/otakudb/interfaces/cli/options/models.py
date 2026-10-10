from typing import Any

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

__all__ = ["ColumnOptions", "TableViewOptionsModel"]

@dataclass
class ColumnOptions:
	"""Column options."""

	is_enabled: bool = True
	max_width: int | None = None

class TableViewOptionsModel(BaseModel):
	"""Table view options model."""

	autoclear: bool = True
	columns: dict[str, ColumnOptions] = {
		"ID": ColumnOptions(True, None),
		"Name": ColumnOptions(True, None),
	}
	custom: dict[str, Any] = {}
