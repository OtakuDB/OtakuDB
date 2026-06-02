from enum import Enum

class CallbacksTypes(Enum):
	"""Типы Callback-вызовов."""

	AttachmentsChanged = "attachments_hanged"
	SlaveNoteSaved = "slave_note_saved"