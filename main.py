from Source.Interfaces.Enums import Interfaces
from Source.Core.Session import Session
from Source import EntryPoint

from dublib.CLI.Terminalyzer import Command, Terminalyzer

#==========================================================================================#
# >>>>> ГЕНЕРАЦИЯ КОМАНД <<<<< #
#==========================================================================================#

COMMANDS: list[Command] = list()

Com = Command("run", "Launch OtakuDB interface.")
ComPos = Com.create_position("INTERFACE", description = "Interface specification.")
ComPos.add_flag("-api")
ComPos.add_flag("-cli")
ComPos.add_flag("-web")
COMMANDS.append(Com)

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ ОБЪЕКТОВ <<<<< #
#==========================================================================================#

Analyzer = Terminalyzer()
Analyzer.helper.enable()
Analyzer.helper.enable_sorting()

SessionObject = Session()

#==========================================================================================#
# >>>>> ПАРСИНГ И ОБРАБОТКА КОМАНД <<<<< #
#==========================================================================================#

COMMAND_DATA = Analyzer.check_commands(COMMANDS)

if not COMMAND_DATA:
	EntryPoint.RunInterface(Interfaces.CLI, SessionObject)
	exit()

match COMMAND_DATA.name:

	case "help": pass

	case "run":
		InterfaceFlag = None

		try: InterfaceFlag = COMMAND_DATA.get_position_parameter("INTERFACE")
		except KeyError: pass

		if InterfaceFlag: InterfaceFlag = InterfaceFlag.name
		Interface = {
			"-cli": Interfaces.CLI,
			None: Interfaces.CLI
		}[InterfaceFlag]

		EntryPoint.RunInterface(Interface, SessionObject)
		