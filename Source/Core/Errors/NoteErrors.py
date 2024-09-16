from dublib.Engine.Bus import ExecutionError

NOTE_ERROR_METAINFO_BLOCKED = ExecutionError(1, "metainfo_blocked")
NOTE_ERROR_ATTACHMENTS_BLOCKED = ExecutionError(2, "attachments_blocked")
NOTE_ERROR_BAD_ATTACHMENT_PATH = ExecutionError(3, "bad_attachment_path")
NOTE_ERROR_OTHER_ATTACHMENTS_DENIED = ExecutionError(4, "other_attachments_denied")
NOTE_ERROR_SLOT_ATTACHMENTS_DENIED = ExecutionError(5, "slot_attachments_denied")
NOTE_ERROR_NO_ATTACHMENT = ExecutionError(6, "no_attachment")
NOTE_ERROR_NO_ATTACHMENT_SLOT = ExecutionError(7, "no_attachment_slot")