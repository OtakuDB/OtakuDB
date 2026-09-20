from enum import Enum

class CallbacksTypes(Enum):
	"""Типы Callback-вызовов."""

	AttachmentsChanged = "attachments_changed"
	SlaveSaved = "slave_saved"