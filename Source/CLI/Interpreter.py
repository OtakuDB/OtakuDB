from Source.CLI.Templates import Columns, Confirmation, Error, ExecutionStatus, Warning
from Source.Driver import Driver

from dublib.Terminalyzer import ArgumentsTypes, Command, CommandData, Terminalyzer
from dublib.Exceptions.Terminalyzer import InvalidArgumentType, NotEnoughArguments
from dublib.StyledPrinter import Styles, TextStyler

import readline
import shlex

class Interpreter:
	"""Обработчик интерфейса командной строки."""

	#==========================================================================================#
	# >>>>> ГЕНЕРАТОРЫ УРОВНЕЙ КОМАНД <<<<< #
	#==========================================================================================#

	def __GenerateManagerCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: manager."""

		# Список команд.
		CommandsList = list()

		# Создание команды: create.
		Com = Command("create")
		Com.add_argument(ArgumentsTypes.All, important = True)
		Com.add_key_position(["type"], ArgumentsTypes.All, important = True)
		CommandsList.append(Com)

		# Создание команды: exit.
		Com = Command("exit")
		CommandsList.append(Com)

		# Создание команды: list.
		Com = Command("list")
		CommandsList.append(Com)

		# Создание команды: mount.
		Com = Command("mount")
		Com.add_argument(ArgumentsTypes.ValidPath)
		CommandsList.append(Com)

		# Создание команды: open.
		Com = Command("open")
		Com.add_argument(ArgumentsTypes.All, important = True)
		CommandsList.append(Com)

		return CommandsList

	def __GenerateTableCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: table."""

		# Список команд.
		CommandsList = list()

		# Создание команды: close.
		Com = Command("close")
		CommandsList.append(Com)

		# Создание команды: open.
		Com = Command("open")
		Com.add_argument(ArgumentsTypes.Number, important = True, layout_index = 1)
		Com.add_flag_position(["f"], layout_index = 1)
		CommandsList.append(Com)

		# Создание команды: remove.
		Com = Command("remove")
		CommandsList.append(Com)

		# Создание команды: rename.
		Com = Command("rename")
		Com.add_argument(ArgumentsTypes.All, important = True)
		CommandsList.append(Com)

		# Добавление команд из таблицы.
		CommandsList += self.__Table.cli.commands

		return CommandsList

	def __GenerateNoteCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: note."""

		# Список команд.
		CommandsList = list()

		# Создание команды: close.
		Com = Command("close")
		CommandsList.append(Com)

		# Создание команды: remove.
		Com = Command("remove")
		CommandsList.append(Com)

		# Добавление команд из записи.
		CommandsList += self.__Note.cli.commands

		return CommandsList

	#==========================================================================================#
	# >>>>> ОБРАБОТЧИКИ УРОВНЕЙ КОМАНД <<<<< #
	#==========================================================================================#

	def __ProcessManagerCommands(self, command_data: CommandData):
		"""
		Обрабатывает команды уровня: manager.
			command_data – данные команды.
		"""
		
		# Обработка команды: create.
		if command_data.name == "create":
			# Создание таблицы.
			Status = self.__Driver.create_table(command_data.arguments[0], command_data.values["type"])
			# Обработка статуса.
			if Status.code == 0: print("Created.")
			if Status.code != 0: Error(Status.message)

		# Обработка команды: exit.
		if command_data.name == "exit":
			# Завершение процесса.
			exit(0)
		
		# Обработка команды: list.
		if command_data.name == "list":
			# Получение списка таблиц.
			Tables = sorted(self.__Driver.tables)

			# Если существуют таблицы.
			if len(Tables):
				# Вывод в консоль: список таблиц.
				print("\n".join(Tables))

			else:
				# Вывод в консоль: список таблиц.
				print("No tables.")

		# Обработка команды: mount.
		if command_data.name == "mount":
			# Директория хранилища.
			StorageDir = command_data.arguments[0] if len(command_data.arguments) else "Data"
			# Монтирование директории хранилища.
			Status = self.__Driver.mount(StorageDir)
			# Обработка статуса.
			if Status.code == 0: print(f"Mounted: \"{self.__Driver.storage_directory}\"." )
			if Status.code < 0: Error(Status.message)

		# Обработка команды: open.
		if command_data.name == "open":
			# Открытие таблицы.
			Table = self.__Driver.open_table(command_data.arguments[0])

			# Если не получен декскриптор таблицы.
			if type(Table) == ExecutionStatus:
				# Вывод в консоль: ошибка.
				Error(Table.message)

			else:
				# Переход на новый уровень интерпретации.
				self.__Table = Table
				self.__InterpreterLevel = "table"

	def __ProcessTableCommands(self, command_data: CommandData):
		"""
		Обрабатывает команды уровня: table.
			command_data – данные команды.
		"""

		# Обработка команды: close.
		if command_data.name == "close":
			# Переход на предыдущий уровень интерпретации.
			self.__Table = None
			self.__InterpreterLevel = "manager"

		# Обработка команды: open.
		elif command_data.name == "open":
			# Открытие записи.
			Note = self.__Table.get_note(command_data.arguments[0])

			# Если не получен декскриптор таблицы.
			if type(Note) == ExecutionStatus:
				# Вывод в консоль: ошибка.
				Error(Note.message)

			else:
				# Переход на новый уровень интерпретации.
				self.__Note = Note
				self.__InterpreterLevel = "note"

		# Обработка команды: remove.
		elif command_data.name == "remove":
			# Запрос подтверждения.
			Response = Confirmation("Are you sure to remove \"" + self.__Table.name + "\" table?")
			
			# Если подтверждено.
			if Response:
				# Удаление таблицы.
				Status = self.__Driver.remove_table(self.__Table.name)

				# Если удаление успешно.
				if Status.code == 0:
					# Переход на предыдущий уровень интерпретации.
					self.__Table = None
					self.__InterpreterLevel = "manager"
					# Вывод в консоль: таблица удалена.
					print("Table removed.")

				else: Error(Status.message)

		# Обработка команды: rename.
		elif command_data.name == "rename":
			# Переименование таблицы.
			Status = self.__Table.rename(command_data.arguments[0])
			# Обработка статуса.
			if Status.code == 0: print("Table renamed.")
			if Status.code != 0: Error(Status.message)

		# Обработка команд таблицы.
		else: self.__Table.cli.execute(command_data)

	def __ProcessNoteCommands(self, command_data: CommandData):
		"""
		Обрабатывает команды уровня: note.
			command_data – данные команды.
		"""

		# Обработка команды: close.
		if command_data.name == "close":
			# Переход на предыдущий уровень интерпретации.
			self.__Note = None
			self.__InterpreterLevel = "table"

		# Обработка команды: remove.
		elif command_data.name == "remove":
			# Запрос подтверждения.
			Response = Confirmation("Are you sure to remove #" + str(self.__Note.id) + " note?")
			
			# Если подтверждено.
			if Response:
				# Удаление таблицы.
				Status = self.__Table.remove_note(self.__Note.id)

				# Если удаление успешно.
				if Status.code == 0:
					# Переход на предыдущий уровень интерпретации.
					self.__Note = None
					self.__InterpreterLevel = "table"
					# Вывод в консоль: запись удалена.
					print("Note removed.")

				else: Error(Status.message)

		# Обработка команд записи.
		else: self.__Note.cli.execute(command_data)

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Selector(self) -> str:
		"""Создаёт идентификатор ввода в зависимости от уровня интерпретации."""

		# Название таблицы.
		TableName = "-" + self.__Table.name if self.__Table else ""
		# ID Записи.
		NoteID = "-" + str(self.__Note.id) if self.__Note else ""
		# Идентификатор ввода.
		Selector = f"[OtakuBD{TableName}{NoteID}]-> "

		return Selector

	def __ParseCommandData(self, input_line: list[str]) -> CommandData:
		"""
		Парсит команду на составляющие.
		"""

		# Данные команды.
		Command = -1

		try:
			# Проверка команд уровня интерпретации.
			Command = Terminalyzer(input_line).check_commands(self.__CommandsGenerators[self.__InterpreterLevel]())

		except NotEnoughArguments:
			# Вывод в консоль: недостаточно аргументов.
			Error("not_enough_arguments")

		except InvalidArgumentType as ExceptionData:
			# Получение ожидаемого типа данных.
			Type = str(ExceptionData).split("\"")[-2]
			# Вывод в консоль: недостаточно аргументов.
			Error("invalid_argument_type", Type)

		return Command

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Обработчик интерфейса командной строки."""

		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# Менеджер таблиц.
		self.__Driver = Driver(mount = True)
		# Вывод в консоль: выполненное монтирование.
		if self.__Driver.is_mounted: print(f"Mounted: \"{self.__Driver.storage_directory}\"." )
		# Уровень интерпретации.
		self.__InterpreterLevel = "manager"
		# Определения команд.
		self.__CommandsGenerators = {
			"manager": self.__GenerateManagerCommands,
			"table": self.__GenerateTableCommands,
			"note": self.__GenerateNoteCommands
		}
		# Определения обработчиков.
		self.__Processors = {
			"manager": self.__ProcessManagerCommands,
			"table": self.__ProcessTableCommands,
			"note": self.__ProcessNoteCommands
		}
		# Текущая таблица.
		self.__Table = None
		# Текущая запись.
		self.__Note = None

	def run(self):
		"""Запускает оболочку CLI."""

		# Введённая строка.
		InputLine = None

		# Пока не введена команда закрытия.
		while True:

			try:
				# Обработка ввода.
				InputLine = input(self.__Selector())
				InputLine = InputLine.strip()
				InputLine = shlex.split(InputLine) if len(InputLine) > 0 else [""]

			except KeyboardInterrupt:
				# Вывод в консоль: выход.
				print("exit\nExiting...")
				# Завершение работы.
				exit(0)

			# Если ввод не пустой.
			if InputLine != [""]:
				# Парсинг команды.
				Command = self.__ParseCommandData(InputLine)

				# Если команда не распознана.
				if Command == None:
					# Вывод в консоль: ошибка распознания команды.
					Error("unknown_command", InputLine[0])

				elif Command != -1:
					# Запуск обработчика команд текущего уровня интерпретации.
					self.__Processors[self.__InterpreterLevel](Command)					