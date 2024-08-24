from dublib.Engine.Bus import ExecutionError

DRIVER_ERROR_NO_TABLE = ExecutionError(1, "no_table")
DRIVER_ERROR_NO_MODULE = ExecutionError(2, "no_module")
DRIVER_ERROR_NO_MODULES_IN_TABLE = ExecutionError(3, "no_modules_in_table")
DRIVER_ERROR_NO_TYPE = ExecutionError(4, "no_type")
DRIVER_ERROR_BAD_MANIFEST = ExecutionError(5, "bad_manifest")
DRIVER_ERROR_MODULE_ALREADY_INITIALIZED = ExecutionError(6, "module_already_initialized")