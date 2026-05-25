from enum import Enum

class Bases(Enum):
	"""Основы аниме."""

	Game = "game"
	Manga = "manga"
	Novel = "novel"
	Original = "original"
	Ranobe = "ranobe"

class PartsTypes(Enum):
	"""Типы частей."""

	Film = "film"
	ONA = "ONA"
	OVA = "OVA"
	Season = "season"
	Specials = "specials"

class Statusses(Enum):
	"""Статусы просмотра."""

	Announced = "announced"
	Completed = "completed"
	Dropped = "dropped"
	Planned = "planned"
	Watching = "watching"