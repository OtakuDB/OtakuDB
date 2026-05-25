from dublib.CLI.Terminalyzer import Command, Terminalyzer, ParametersTypes

COMMANDS: list[Command] = list()

Com = Command("run", "Launch OtakuDB interface.")
ComPos = Com.create_position("INTERFACE", description = "Interface specification: cli (only one supported now).")
ComPos.set_argument(ParametersTypes.Alpha)

Analyzer = Terminalyzer()
Analyzer.helper.enable()
Analyzer.helper.enable_sorting()

COMMAND_DATA = Analyzer.check_commands(COMMANDS)