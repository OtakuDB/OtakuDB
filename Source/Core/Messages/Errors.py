import enum

UNKNOWN = "Unknown error."

class Driver(enum.Enum):
	NO_TABLE_TYPE = "No table type."
	BAD_MANIFEST = "Bad manifest."
	PATH_NOT_FOUND = "Path not found."
	TABLE_ALREADY_EXISTS = "Table already exists."

class Table(enum.Enum):
	NO_NOTE = "No note."
	INCORRECT_NOTE_ID = "Incorrect note ID."