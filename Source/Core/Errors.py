from dublib.Engine.Bus import ExecutionError

ERROR_UNKNOWN = ExecutionError(-1, "unknown_error")

DRIVER_ERROR_BAD_PATH = ExecutionError(1, "bad_path")
DRIVER_ERROR_NO_TABLE_TYPE = ExecutionError(2, "no_table_type")
DRIVER_ERROR_BAD_MANIFEST = ExecutionError(3, "bad_manifest")
DRIVER_ERROR_NO_MODULES = ExecutionError(4, "no_modules")

# TABLE_ERROR = ExecutionError(1, "")

NOTE_ERROR_METAINFO_BLOCKED = ExecutionError(1, "metainfo_blocked")
