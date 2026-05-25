from dataclasses import dataclass

from enum import Enum

#==========================================================================================#
# >>>>> СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass
class Era:
	index: int | float
	name: str
	start_year: int | None
	end_year: int | None

#==========================================================================================#
# >>>>> ПЕРЕЧИСЛЕНИЯ <<<<< #
#==========================================================================================#

class CollectionStatusses(Enum):
	"""Статусы коллекционирования."""

	Collected = "collected"
	Ebook = "ebook"
	Wishlist = "wishlist"
	Ordered = "ordered"

class Statusses(Enum):
	"""Статусы прочтения."""

	Announced = "announced"
	Completed = "completed"
	Dropped = "dropped"
	Planned = "planned"
	Reading = "reading"
	Skipped = "skipped"

class Types(Enum):
	"""Типы произведений."""

	Compilation = "compilation"
	Novel = "novel"
	Story = "story"