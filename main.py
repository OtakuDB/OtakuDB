from Source.EntryPoint import COMMAND_DATA
from Source.Core.Enums import Interfaces
from Source.Core.Session import Session

import importlib

SessionObject = Session("Data")

if not COMMAND_DATA or COMMAND_DATA.name == "run":
	Interface = Interfaces.CLI
	if COMMAND_DATA and len(COMMAND_DATA.arguments) > 0: Interface = Interfaces(COMMAND_DATA.arguments[0])
	InterfaceModule = importlib.import_module(f"Source.Interfaces.{Interface.name}")
	InterfaceModule.Interface(SessionObject).run()

match COMMAND_DATA.name:
	case "help": exit()