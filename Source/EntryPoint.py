from dublib.CLI.Terminalyzer import Command, Terminalyzer, ParametersTypes

COMMANDS: list[Command] = list()

Com = Command("run", "Launch OtakuDB interface.")
ComPos = Com.create_position("INTERFACE", description = "Interface specification.")
ComPos.add_argument(ParametersTypes.Alpha, "Interface: cli (only one supported now).")

Analyzer = Terminalyzer()
Analyzer.helper.enable()
Analyzer.helper.enable_sorting()

COMMAND_DATA = Analyzer.check_commands(COMMANDS)