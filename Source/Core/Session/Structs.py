from dataclasses import dataclass
import enum

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class StorageLevels(enum.Enum):
	"""Уровни объектов хранилища."""

	DRIVER = None
	TABLE = "table"
	MODULE = "module"
	NOTE = "note"

@dataclass
class PathObjects:
	"""Контейнер объектов в пути."""

	table: str = None
	module: str = None
	note: int = None