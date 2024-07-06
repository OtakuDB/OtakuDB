from Source.CLI.Templates import Columns, Error
from Source.Driver import Driver

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData, Terminalyzer
from dublib.CLI.StyledPrinter import Styles, TextStyler
from dublib.CLI.Templates import PrintExecutionStatus
from dublib.CLI.Templates import Confirmation
from dublib.Exceptions.CLI import *

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
		Com = Command("create", "Create new table.")
		Com.add_argument(description = "Table name.", important = True)
		Com.add_key("type", description = "Type of table.", important = True)
		CommandsList.append(Com)

		# Создание команды: exit.
		Com = Command("exit", "Exit from OtakuBD.")
		CommandsList.append(Com)

		# Создание команды: list.
		Com = Command("list", "Print list op tables.")
		CommandsList.append(Com)

		# Создание команды: mount.
		Com = Command("mount", "Select storage directory.")
		Com.add_argument(description = "Path to storage directory.")
		CommandsList.append(Com)

		# Создание команды: open.
		Com = Command("open", "Open table.")
		Com.add_argument(description = "Table name.", important = True)
		CommandsList.append(Com)

		return CommandsList

	def __GenerateTableCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: table."""

		# Список команд.
		CommandsList = list()

		# Создание команды: close.
		Com = Command("close", "Close table.")
		CommandsList.append(Com)

		# Создание команды: open.
		Com = Command("open", "Open note.")
		ComPos = Com.create_position("NOTE", "Note identificator.", important = True)
		ComPos.add_argument(ParametersTypes.Number, description = "Note ID.")
		ComPos.add_flag("last", description = "Open last created note.")
		CommandsList.append(Com)

		# Создание команды: remove.
		Com = Command("remove", "Remove table.")
		CommandsList.append(Com)

		# Создание команды: rename.
		Com = Command("rename", "Rename table.")
		Com.add_argument(description = "Table name.", important = True)
		CommandsList.append(Com)

		# Добавление команд из таблицы.
		CommandsList += self.__Table.cli.commands

		return CommandsList

	def __GenerateNoteCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: note."""

		# Список команд.
		CommandsList = list()

		# Создание команды: close.
		Com = Command("close", "Close note.")
		CommandsList.append(Com)

		# Создание команды: remove.
		Com = Command("remove", "Remove note.")
		CommandsList.append(Com)

		# Добавление команд из записи.
		CommandsList += self.__Note.cli.commands

		return CommandsList

	#==========================================================================================#
	# >>>>> ОБРАБОТЧИКИ УРОВНЕЙ КОМАНД <<<<< #
	#==========================================================================================#

	def __ProcessManagerCommands(self, command_data: ParsedCommandData):
		"""
		Обрабатывает команды уровня: manager.
			command_data – данные команды.
		"""

		# Статус обработки команды.
		Status = None
		
		# Обработка команды: create.
		if command_data.name == "create":
			# Создание таблицы.
			Status = self.__Driver.create_table(command_data.arguments[0], command_data.get_key_value("type"))

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
				# Табличное содержимое.
				Content = {
					"Table": [],
					"Type": []
				}
				
				# Для каждой таблицы.
				for Table in self.__Driver.tables:
					# Чтение манифеста.
					Manifest = self.__Driver.get_manifest(Table)
					# Заполнение колонок.
					Content["Table"].append(Table)
					Content["Type"].append(TextStyler(Manifest["type"], decorations = [Styles.Decorations.Italic]))

				# Вывод списка.
				Columns(Content, sort_by = "Table")

			else:
				# Вывод в консоль: список таблиц.
				print("No tables.")

		# Обработка команды: mount.
		if command_data.name == "mount":
			# Директория хранилища.
			StorageDir = command_data.arguments[0] if len(command_data.arguments) else "Data"
			# Монтирование директории хранилища.
			Status = self.__Driver.mount(StorageDir)
			
		# Обработка команды: open.
		if command_data.name == "open":
			# Открытие таблицы.
			Status = self.__Driver.open_table(command_data.arguments[0])

			# Если открытие успешно.
			if Status.code == 0:
				# Переход на новый уровень интерпретации.
				self.__Table = Status.value
				self.__InterpreterLevel = "table"		

		# Вывод статуса.
		PrintExecutionStatus(Status)

	def __ProcessTableCommands(self, command_data: ParsedCommandData):
		"""
		Обрабатывает команды уровня: table.
			command_data – данные команды.
		"""

		# Статус обработки команды.
		Status = None

		# Обработка команды: close.
		if command_data.name == "close":
			# Переход на предыдущий уровень интерпретации.
			self.__Table = None
			self.__InterpreterLevel = "manager"

		# Обработка команды: open.
		elif command_data.name == "open":
			# Открытие записи.
			Status = self.__Table.get_note(command_data.arguments[0])

			# Если не получен декскриптор таблицы.
			if Status.code == 0:
				# Переход на новый уровень интерпретации.
				self.__Note = Status.value
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

		# Обработка команды: rename.
		elif command_data.name == "rename":
			# Переименование таблицы.
			Status = self.__Table.rename(command_data.arguments[0])

		else:
			# Обработка команд таблицы.
			Status = self.__Table.cli.execute(command_data)

		# Вывод статуса.
		PrintExecutionStatus(Status)

	def __ProcessNoteCommands(self, command_data: ParsedCommandData):
		"""
		Обрабатывает команды уровня: note.
			command_data – данные команды.
		"""

		# Статус обработки команды.
		Status = None

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

		else:
			# Обработка команд записи.
			Status = self.__Note.cli.execute(command_data)

		# Вывод статуса.
		PrintExecutionStatus(Status)

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

	def __ParseCommandData(self, input_line: list[str]) -> ParsedCommandData:
		"""
		Парсит команду на составляющие.
		"""

		# Данные команды.
		Command = -1

		try:
			# Инициализация анализатора.
			Analyzer = Terminalyzer(input_line)
			# Включение модуля помощи.
			Analyzer.enable_help(True)
			# Отключение записи о важности параметров.
			Analyzer.help_translation.important_note = ""
			# Проверка команд уровня интерпретации.
			Command = Analyzer.check_commands(self.__CommandsGenerators[self.__InterpreterLevel]())

		except NotEnoughParameters:
			# Вывод в консоль: недостаточно параметров.
			Error("not_enough_parameters")

		except InvalidParameterType as ExceptionData:
			# Получение ожидаемого типа данных.
			Type = str(ExceptionData).split("\"")[-2]
			# Вывод в консоль: неверный тип параметра.
			Error("invalid_parameter_type", Type)

		except TooManyParameters:
			# Вывод в консоль: слишком много параметров.
			Error("too_many_parameters")

		return Command

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Обработчик интерфейса командной строки."""

		#---> Генерация динамичкских атрибутов.
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