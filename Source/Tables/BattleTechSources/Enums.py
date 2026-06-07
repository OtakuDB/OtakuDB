from enum import Enum

class CollectionStatuses(Enum):
	"""Статусы коллекционирования."""

	Collected = "collected"
	Ebook = "ebook"
	Wishlist = "wishlist"
	Ordered = "ordered"

class Statuses(Enum):
	"""Статусы прочтения."""

	Announced = "announced"
	Completed = "completed"
	Dropped = "dropped"
	Planned = "planned"
	Reading = "reading"
	Skipped = "skipped"

class Types(Enum):
	"""Типы соурсбуков."""

	Dossier = "Dossier"
	CombatManual = "Combat Manual"
	ForceManual = "Force Manual"
	FieldManual = "Field Manual"
	Handbook = "Handbook"
	SpotlightOn = "Spotlight On"
	ScenarioPack = "Scenario Pack"
	Sourcebook = "Sourcebook"
	TouringStars = "Touring the Stars"
	Rulebook = "Rulebook"
	EraDigest = "EraDigest"