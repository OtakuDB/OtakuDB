import enum

UNKNOWN = "Unknown error."
PATH_NOT_FOUND = "Path not found."

class Driver(enum.Enum):
	NO_TABLE_TYPE = "No table type."
	NO_MODULE_TYPE = "No module type."
	MODULES_NOT_SUPPORTED = "Modules not supported."
	BAD_MANIFEST = "Bad manifest."
	TABLE_ALREADY_EXISTS = "Table already exists."
	MISSING_OBJECT = "Missing object."
	OBJECT_OVERWRITING_DENIED = "Object overwtiting denied."
	STORAGE_NOT_MOUNTED = "Storage not mounted."

class Table(enum.Enum):
	NO_NOTE = "No note."
	INCORRECT_NOTE_ID = "Incorrect note ID."

class Module(enum.Enum):
	NO_NOTE = Table.NO_NOTE
	INCORRECT_NOTE_ID = Table.INCORRECT_NOTE_ID

class Note(enum.Enum):
	ATTACHMENTS_DISABLED = "Attachments disabled."
	ATTACHMENT_DENIED = "Attachment denied."
	METAINFO_BLOCKED = "Metainfo blocked."