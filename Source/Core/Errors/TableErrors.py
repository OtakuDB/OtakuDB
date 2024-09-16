from dublib.Engine.Bus import ExecutionError

TABLE_ERROR_MISSING_NOTE = ExecutionError(1, "missing_note")
TABLE_ERROR_NOTE_ALREADY_EXISTS = ExecutionError(2, "note_already_exists")