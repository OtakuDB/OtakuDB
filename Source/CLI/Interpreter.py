from Source.CLI.Templates import Columns, Confirmation, Error, ExecutionStatus, Warning
from dublib.Terminalyzer import ArgumentsTypes, Command, CommandData, Terminalyzer
from dublib.Exceptions.Terminalyzer import InvalidArgumentType, NotEnoughArguments
from Source.CLI.Viewer import View
from Source.Driver import Driver

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
		com_create = Command("create")
		com_create.add_argument(ArgumentsTypes.All, important = True)
		CommandsList.append(com_create)

		# Создание команды: exit.
		com_exit = Command("exit")
		CommandsList.append(com_exit)

		# Создание команды: list.
		com_list = Command("list")
		CommandsList.append(com_list)

		# Создание команды: open.
		com_open = Command("open")
		com_open.add_argument(ArgumentsTypes.All, important = True)
		CommandsList.append(com_open)

		return CommandsList

	def __GenerateTableCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: table."""

		# Список команд.
		CommandsList = list()

		# Создание команды: close.
		com_close = Command("close")
		CommandsList.append(com_close)

		# Создание команды: list.
		com_list = Command("list")
		CommandsList.append(com_list)

		# Создание команды: new.
		com_new = Command("new")
		CommandsList.append(com_new)

		# Создание команды: open.
		com_open = Command("open")
		com_open.add_argument(ArgumentsTypes.Number, important = True)
		CommandsList.append(com_open)

		# Создание команды: remove.
		com_remove = Command("remove")
		CommandsList.append(com_remove)

		# Создание команды: rename.
		com_rename = Command("rename")
		com_rename.add_argument(ArgumentsTypes.All, important = True)
		CommandsList.append(com_rename)

		return CommandsList

	def __GenerateNoteCommands(self) -> list[Command]:
		"""Генерирует список команд уровня: note."""

		# Список команд.
		CommandsList = list()

		# Создание команды: close.
		Com = Command("close")
		CommandsList.append(Com)

		# Создание команды: delpart.
		Com = Command("delpart")
		Com.add_argument(ArgumentsTypes.Number, important = True)
		CommandsList.append(Com)

		# Создание команды: downpart.
		Com = Command("downpart")
		Com.add_argument(ArgumentsTypes.Number, important = True)
		CommandsList.append(Com)

		# Создание команды: editpart.
		Com = Command("editpart")
		Com.add_argument(ArgumentsTypes.Number, important = True)
		Com.add_flag_position(["w", "u"])
		Com.add_key_position(["comment"], ArgumentsTypes.All)
		Com.add_key_position(["link"], ArgumentsTypes.URL)
		Com.add_key_position(["mark"], ArgumentsTypes.Number)
		Com.add_key_position(["name"], ArgumentsTypes.All)
		Com.add_key_position(["number"], ArgumentsTypes.Number)
		Com.add_key_position(["series"], ArgumentsTypes.Number)
		CommandsList.append(Com)

		# Создание команды: mark.
		Com = Command("mark")
		Com.add_argument(ArgumentsTypes.Number, important = True)
		Com.add_argument(ArgumentsTypes.Number, important = True)
		CommandsList.append(Com)

		# Создание команды: newpart.
		Com = Command("newpart")
		Com.add_argument(ArgumentsTypes.All, important = True)
		Com.add_flag_position(["w"])
		Com.add_key_position(["comment"], ArgumentsTypes.All)
		Com.add_key_position(["link"], ArgumentsTypes.URL)
		Com.add_key_position(["mark"], ArgumentsTypes.Number)
		Com.add_key_position(["name"], ArgumentsTypes.All)
		Com.add_key_position(["number"], ArgumentsTypes.Number)
		Com.add_key_position(["series"], ArgumentsTypes.Number)
		CommandsList.append(Com)

		# Создание команды: remove.
		Com = Command("remove")
		CommandsList.append(Com)

		# Создание команды: reset.
		Com = Command("reset")
		Com.add_argument(ArgumentsTypes.All, important = True)
		CommandsList.append(Com)

		# Создание команды: set.
		Com = Command("set")
		Com.add_key_position(["name"], ArgumentsTypes.All)
		Com.add_key_position(["altname"], ArgumentsTypes.All)
		Com.add_key_position(["estimation"], ArgumentsTypes.Number)
		Com.add_key_position(["status"], ArgumentsTypes.All)
		Com.add_key_position(["tag"], ArgumentsTypes.All)
		CommandsList.append(Com)

		# Создание команды: undrop.
		Com = Command("undrop")
		CommandsList.append(Com)

		# Создание команды: unset.
		Com = Command("unset")
		Com.add_key_position(["altname", "tag"], ArgumentsTypes.All, important = True)
		CommandsList.append(Com)

		# Создание команды: uppart.
		Com = Command("uppart")
		Com.add_argument(ArgumentsTypes.Number, important = True)
		CommandsList.append(Com)

		# Создание команды: view.
		Com = Command("view")
		CommandsList.append(Com)

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
			Status = self.__Driver.create_table(command_data.arguments[0])
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
			# Вывод в консоль: список таблиц.
			print("\n".join(Tables))

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

		# Обработка команды: list.
		if command_data.name == "list":
			# Получение списка записей.
			Notes = self.__Table.notes
			
			# Если записи существуют.
			if len(Notes) > 0:
				# Табличное содержимое.
				Content = {
					"ID": [],
					"Status": [],
					"Estimation": [],
					"Name": []
				}
				
				# Для каждой записи.
				for Note in Notes:
					# Получение данных.
					Name = Note.name if Note.name else ""
					# Заполнение колонок.
					Content["ID"].append(Note.id)
					Content["Status"].append(Note.emoji_status)
					Content["Estimation"].append(Note.estimation if Note.estimation else "")
					Content["Name"].append(Name)

				# Вывод описания.
				Columns(Content)

			else:
				# Вывод в консоль: таблица пуста.
				print("Table is empty.")

		# Обработка команды: new.
		if command_data.name == "new":
			# Создание новой записи.
			ID = self.__Table.create_note()
			
			# Если запись создана.
			if ID:
				# Вывод в консоль: ID новой записи.
				print(f"Note #{ID} created.")

			else:
				# Вывод в консоль: ошибка.
				Error("unable_to_create_note")

		# Обработка команды: open.
		if command_data.name == "open":
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
		if command_data.name == "remove":
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
		if command_data.name == "rename":
			# Переименование таблицы.
			Status = self.__Table.rename(command_data.arguments[0])
			# Обработка статуса.
			if Status.code == 0: print("Table renamed.")
			if Status.code != 0: Error(Status.message)

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

		# Обработка команды: delpart.
		if command_data.name == "delpart":
			# Запрос подтверждения.
			Response = Confirmation("Are you sure to remove part?")
			
			# Если подтверждено.
			if Response:
				# Удаление части.
				Status = self.__Note.delete_part(int(command_data.arguments[0]))
				# Обработка статуса.
				if Status.code == 0: print("Part deleted.")
				if Status.code != 0: Error(Status.message)

		# Обработка команды: downpart.
		if command_data.name == "downpart":
			# Поднятие части.
			Status = self.__Note.down_part(int(command_data.arguments[0]))
			# Обработка статуса.
			if Status.code == 0: print("Part downed.")
			if Status.code == 1: Warning(Status.message)
			if Status.code < 0: Error(Status.message)

		# Обработка команды: editpart.
		if command_data.name == "editpart":
			# Дополнительные данные.
			Data = dict()
			# Парсинг дополнительных значений.
			if "w" in command_data.flags: Data["watched"] = True
			if "u" in command_data.flags: Data["watched"] = False
			if "link" in command_data.keys: Data["link"] = command_data.values["link"]
			if "comment" in command_data.keys: Data["comment"] = command_data.values["comment"]
			if "number" in command_data.keys: Data["number"] = int(command_data.values["number"])
			if "series" in command_data.keys: Data["series"] = int(command_data.values["series"])
			# Добавление части.
			Status = self.__Note.edit_part(int(command_data.arguments[0]), Data)
			# Обработка статуса.
			if Status.code == 0: print("Part edited.")
			if Status.code != 0: Error(Status.message)

		# Обработка команды: mark.
		if command_data.name == "mark":
			# Добавление закладки.
			Status = self.__Note.set_mark(int(command_data.arguments[0]), int(command_data.arguments[1]))
			# Обработка статуса.
			if Status.code == 0: print("Mark updated.")
			if Status.code == 1: Warning(Status.message)
			if Status.code in [2, 3]: print(Status.message)
			if Status.code < 0: Error(Status.message)

		# Обработка команды: newpart.
		if command_data.name == "newpart":
			# Дополнительные данные.
			Data = dict()
			# Парсинг дополнительных значений.
			if "w" in command_data.flags: Data["watched"] = True
			if "link" in command_data.keys: Data["link"] = command_data.values["link"]
			if "name" in command_data.keys: Data["name"] = command_data.values["name"]
			if "number" in command_data.keys: Data["number"] = int(command_data.values["number"])
			if "series" in command_data.keys: Data["series"] = int(command_data.values["series"])
			# Добавление части.
			Status = self.__Note.add_part(command_data.arguments[0], Data)
			# Обработка статуса.
			if Status.code == 0: print("Part created.")
			if Status.code != 0: Error(Status.message)

		# Обработка команды: remove.
		if command_data.name == "remove":
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

		# Обработка команды: reset.
		if command_data.name == "reset":
			# Сброс значения.
			Status = self.__Note.reset(command_data.arguments[0])
			# Обработка статуса.
			if Status.code == 0: print("Value set to default.")
			if Status.code != 0: Error(Status.message)

		# Обработка команды: set.
		if command_data.name == "set":

			# Если задаётся название.
			if "name" in command_data.keys:
				# Обновление названия.
				Status = self.__Note.rename(command_data.values["name"])
				# Обработка статуса.
				if Status.code == 0: print("Name updated.")
				if Status.code != 0: Error(Status.message)

			# Если задаётся альтернативное название.
			if "altname" in command_data.keys:
				# Обновление названия.
				Status = self.__Note.add_another_name(command_data.values["altname"])
				# Обработка статуса.
				if Status.code == 0: print("Another name added.")
				if Status.code != 0: Error(Status.message)

			# Если задаётся оценка.
			if "estimation" in command_data.keys:
				# Обновление оценки.
				Status = self.__Note.estimate(int(command_data.values["estimation"]))
				# Обработка статуса.
				if Status.code == 0: print("Estimation updated.")
				if Status.code != 0: Error(Status.message)

			# Если задаётся статус.
			if "status" in command_data.keys:
				# Установка статуса.
				Status = self.__Note.set_status(command_data.values["status"])
				# Обработка статуса.
				if Status.code == 0: print("Status updated.")
				if Status.code != 0: Error(Status.message)

			# Если задаётся тег.
			if "tag" in command_data.keys:
				# Обновление названия.
				Status = self.__Note.add_tag(command_data.values["tag"])
				# Обработка статуса.
				if Status.code == 0: print("Tag added.")
				if Status.code != 0: Error(Status.message)

		# Обработка команды: unset.
		if command_data.name == "unset":

			# Если удаляется альтернативное название.
			if "altname" in command_data.keys:
				# Удаление альтернативного названия.
				Status = self.__Note.delete_another_name(command_data.values["altname"])
				# Обработка статуса.
				if Status.code == 0: print("Another name removed.")
				if Status.code != 0: Error(Status.message)

			# Если удаляется тег.
			if "tag" in command_data.keys:
				# Удаление тега.
				Status = self.__Note.delete_tag(command_data.values["tag"])
				# Обработка статуса.
				if Status.code == 0: print("Tag removed.")
				if Status.code != 0: Error(Status.message)

		# Обработка команды: uppart.
		if command_data.name == "uppart":
			# Поднятие части.
			Status = self.__Note.up_part(int(command_data.arguments[0]))
			# Обработка статуса.
			if Status.code == 0: print("Part upped.")
			if Status.code == 1: Warning(Status.message)
			if Status.code < 0: Error(Status.message)

		# Обработка команды: view.
		if command_data.name == "view":
			# Просмотр записи.
			View(self.__Table, self.__Note)

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
			Command = Terminalyzer(input_line).check_commands(self.__Commands[self.__InterpreterLevel])

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
		self.__Driver = Driver()
		# Уровень интерпретации.
		self.__InterpreterLevel = "manager"
		# Определения команд.
		self.__Commands = {
			"manager": self.__GenerateManagerCommands(),
			"table": self.__GenerateTableCommands(),
			"note": self.__GenerateNoteCommands()
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
			# Обработка ввода.
			InputLine = input(self.__Selector())
			InputLine = InputLine.strip()
			InputLine = shlex.split(InputLine) if len(InputLine) > 0 else [""]

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