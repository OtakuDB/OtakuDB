from dublib.Engine.Bus import ExecutionError, ExecutionWarning

ERROR_UNKNOWN = ExecutionError(-1, "unknown_error")

#==========================================================================================#
# >>>>> ОШИБКИ ДРАЙВЕРА <<<<< #
#==========================================================================================#

DRIVER_ERROR_NO_TABLE = ExecutionError(1, "no_table")
DRIVER_ERROR_NO_MODULE = ExecutionError(2, "no_module")
DRIVER_ERROR_NO_MODULEs_IN_TABLE = ExecutionError(3, "no_modules_in_table")
DRIVER_ERROR_NO_TYPE = ExecutionError(4, "no_type")
DRIVER_ERROR_BAD_MANIFEST = ExecutionError(5, "bad_manifest")
DRIVER_ERROR_MODULE_ALREADY_INITIALIZED = ExecutionError(6, "module_already_initialized")

#==========================================================================================#
# >>>>> ОШИБКИ ТАБЛИЦ <<<<< #
#==========================================================================================#

TABLE_ERROR_MISSING_NOTE = ExecutionError(1, "missing_note")

#==========================================================================================#
# >>>>> ОШИБКИ МОДУЛЕЙ <<<<< #
#==========================================================================================#

MODULE_ERROR_MISSING_NOTE = TABLE_ERROR_MISSING_NOTE

#==========================================================================================#
# >>>>> ОШИБКИ ЗАПИСЕЙ <<<<< #
#==========================================================================================#

NOTE_ERROR_METAINFO_BLOCKED = ExecutionError(1, "metainfo_blocked")
