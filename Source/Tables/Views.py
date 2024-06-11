from Source.CLI.Templates import Columns, Confirmation, Error, ExecutionStatus, Warning
from Source.Functions import ValueToInt

from dublib.Terminalyzer import ArgumentsTypes, Command, CommandData
from dublib.StyledPrinter import Styles, StyledPrinter, TextStyler
from dublib.Methods import ReadJSON, WriteJSON

import os

#==========================================================================================#
# >>>>> ОБРАБОТЧИКИ ВЗАИМОДЕЙСТВИЙ С ТАБЛИЦЕЙ <<<<< #
#==========================================================================================#

class ViewsNoteCLI:
	"""Обработчик взаимодействий с записью через CLI."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		return self.__Commands

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GenerateCommands(self) -> list[Command]:
		"""Генерирует список команд."""

		# Список команд.
		CommandsList = list()

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
		Com.add_flag_position(["a"])
		Com.add_flag_position(["w", "u"])
		Com.add_key_position(["comment"], ArgumentsTypes.All)
		Com.add_key_position(["link"], ArgumentsTypes.URL)
		Com.add_key_position(["mark"], ArgumentsTypes.Number)
		Com.add_key_position(["name"], ArgumentsTypes.All)
		Com.add_key_position(["number"], ArgumentsTypes.All)
		Com.add_key_position(["series"], ArgumentsTypes.Number)
		CommandsList.append(Com)

		# Создание команды: mark.
		Com = Command("mark")
		Com.add_argument(ArgumentsTypes.Number, important = True)
		Com.add_argument(ArgumentsTypes.Number, important = True)
		CommandsList.append(Com)

		# Создание команды: meta.
		Com = Command("meta")
		Com.add_argument(ArgumentsTypes.All, important = True)
		Com.add_argument(ArgumentsTypes.All)
		Com.add_flag_position(["set", "unset"], important = True)
		CommandsList.append(Com)

		# Создание команды: newpart.
		Com = Command("newpart")
		Com.add_argument(ArgumentsTypes.All, important = True)
		Com.add_flag_position(["a"])
		Com.add_flag_position(["w"])
		Com.add_key_position(["comment"], ArgumentsTypes.All)
		Com.add_key_position(["link"], ArgumentsTypes.URL)
		Com.add_key_position(["mark"], ArgumentsTypes.Number)
		Com.add_key_position(["name"], ArgumentsTypes.All)
		Com.add_key_position(["number"], ArgumentsTypes.All)
		Com.add_key_position(["series"], ArgumentsTypes.Number)
		CommandsList.append(Com)

		# Создание команды: reset.
		Com = Command("reset")
		Com.add_argument(ArgumentsTypes.All, important = True)
		CommandsList.append(Com)

		# Создание команды: set.
		Com = Command("set")
		Com.add_key_position(["altname"], ArgumentsTypes.All)
		Com.add_key_position(["comment"], ArgumentsTypes.All)
		Com.add_key_position(["estimation"], ArgumentsTypes.Number)
		Com.add_key_position(["group"], ArgumentsTypes.Number)
		Com.add_key_position(["name"], ArgumentsTypes.All)
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

	def __View(self):
		"""Выводит форматированные данные записи."""

		# Получение основных значений.
		TotalProgress = f" ({self.__Note.progress}% viewed)" if self.__Note.progress else ""
		# Вывод названия и прогресса.
		if self.__Note.name: StyledPrinter(self.__Note.name, decorations = [Styles.Decorations.Bold], end = False)
		print(f"{TotalProgress} {self.__Note.emoji_status}")

		# Если указаны альтернативные названия.
		if self.__Note.another_names:
			# Вывести каждое название.
			for name in self.__Note.another_names: StyledPrinter(f"    {name}", decorations = [Styles.Decorations.Italic])

		# Вывод оценки.
		if self.__Note.estimation: print(f"⭐ {self.__Note.estimation} / {self.__Table.max_estimation}")
		# Получение частей.
		Parts = self.__Note.parts

		# Если задана группа.
		if self.__Note.group_id:
			# Вывод в консоль: заголовок тегов.
			StyledPrinter(f"GROUP: ", decorations = [Styles.Decorations.Bold], end = False)
			# Название группы.
			GroupName = f"@{self.__Note.group_id}" if not self.__Table.get_group(self.__Note.group_id) else self.__Table.get_group(self.__Note.group_id)["name"]
			if GroupName == "@None": GroupName = ""
			# Вывод в консоль: название группы.
			StyledPrinter(GroupName, decorations = [Styles.Decorations.Italic])

		# Если заданы метаданные.
		if self.__Note.metainfo:
			# Вывод в консоль: заголовок метаданных.
			StyledPrinter(f"METAINFO:", decorations = [Styles.Decorations.Bold])
			# Метаданные.
			MetaInfo = self.__Note.metainfo
			
			# Для каждого свойства.
			for Key in MetaInfo.keys():
				# Вывод в консоль: метаданные.
				print(f"    {Key}: " + str(MetaInfo[Key]))

		# Если заданы теги.
		if self.__Note.tags:
			# Вывод в консоль: заголовок тегов.
			StyledPrinter(f"TAGS: ", decorations = [Styles.Decorations.Bold], end = False)
			# Вывод в консоль: теги.
			print(", ".join(self.__Note.tags))

		# Если имеются части.
		if Parts:
			# Вывод в консоль: заголовок частей.
			StyledPrinter(f"PARTS:", decorations = [Styles.Decorations.Bold])

			# Для каждой части.
			for PartIndex in range(0, len(Parts)):
				# Обработка статуса просмотра.
				Watched = " ✅" if Parts[PartIndex]["watched"] else ""
				if "announce" in Parts[PartIndex].keys(): Watched = " ℹ️"
				# Название части.
				Name = " " + Parts[PartIndex]["name"] if "name" in Parts[PartIndex].keys() and Parts[PartIndex]["name"] else ""

				# Если часть многосерийная.
				if "series" in Parts[PartIndex].keys():
					# Закладка.
					Mark = str(Parts[PartIndex]["mark"]) + " / " if "mark" in Parts[PartIndex] else ""
					# Индикатор закладки.
					MarkIndicator = " ⏳" if Mark else ""
					# Прогресс просмотра части.
					Progress = " (" + str(int(Parts[PartIndex]["mark"] / Parts[PartIndex]["series"] * 100)) + "% viewed)" if Mark else ""
					# Номер сезона.
					Number = " " + str(Parts[PartIndex]["number"]) if "number" in Parts[PartIndex].keys() and Parts[PartIndex]["number"] else ""
					# Если есть и номер, и название, добавить тире.
					if Number and Name: Number += " –"

					# Вывод в консоль: тип части.
					print(f"    {PartIndex} ▸ " + Parts[PartIndex]["type"] + f":{Number}{Name}{Watched}{MarkIndicator}")
					# Вывод в консоль: прогресс просмотра.
					print("    " + " " * len(str(PartIndex)) + f"       {Mark}" + str(Parts[PartIndex]["series"]) + f" series{Progress}")

				else:
					# Номер фильма.
					Number = " " + str(Parts[PartIndex]["number"]) if "number" in Parts[PartIndex].keys() and Parts[PartIndex]["number"] else ""
					# Вывод в консоль: название.
					print(f"    {PartIndex} ▸ " + Parts[PartIndex]["type"] + f"{Number}:{Name}{Watched}")

				# Вывод в консоль: метаданные.
				if "link" in Parts[PartIndex].keys(): print("    " + " " * len(str(PartIndex)) + f"       🔗 " + Parts[PartIndex]["link"])
				if "comment" in Parts[PartIndex].keys(): print("    " + " " * len(str(PartIndex)) + f"       💭 " + Parts[PartIndex]["comment"])

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "ViewsTable", note: "ViewsNote"):
		"""
		Обработчик взаимодействий с таблицей через CLI.
			table – объектное представление таблицы;
			note – объектное представление записи.
		"""

		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# Объектное представление таблицы.
		self.__Table = table
		# Объектное представление записи.
		self.__Note = note
		# Список дескрипторов команд.
		self.__Commands = self.__GenerateCommands()

	def execute(self, command_data: CommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

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
			if "a" in command_data.flags: Data["announce"] = True
			if "w" in command_data.flags:
				Data["watched"] = True
				Data["announce"] = "*"
			if "u" in command_data.flags:
				Data["watched"] = False
				Data["announce"] = "*"
			if "link" in command_data.keys: Data["link"] = command_data.values["link"]
			if "comment" in command_data.keys: Data["comment"] = command_data.values["comment"]
			if "name" in command_data.keys: Data["name"] = command_data.values["name"]
			if "number" in command_data.keys: Data["number"] = ValueToInt(command_data.values["number"])
			if "series" in command_data.keys: Data["series"] = ValueToInt(command_data.values["series"])
			# Редактирование части.
			Status = self.__Note.edit_part(int(command_data.arguments[0]), Data)
			# Обработка статуса.
			if Status.code == 0: print("Part edited.")
			if Status.code != 0: Error(Status.message)

		# Обработка команды: mark.
		if command_data.name == "mark":
			# Добавление закладки.
			Status = self.__Note.set_mark(int(command_data.arguments[0]), int(command_data.arguments[1]))
			# Обработка статуса.
			if Status.code in [1, 2, 3]: print(Status.message)
			if Status.code == 0: print("Mark updated.")
			if Status.code == -1: Error(Status.message)
			if Status.code == -2: Warning(Status.message)

		# Обработка команды: meta.
		if command_data.name == "meta":
			# Статус выполнения.
			Status = ExecutionStatus(0)

			# Если метаданные добавляются.
			if "set" in command_data.flags:
				# Установка метаданных.
				Status = self.__Note.set_metainfo(command_data.arguments[0],  command_data.arguments[1])

			# Если метаданные удаляются.
			if "unset" in command_data.flags:
				# Удаление метаданных.
				Status = self.__Note.delete_metainfo(command_data.arguments[0])

			# Обработка статуса.
			if Status.code == 0: print("Metainfo updated.")
			if Status.code != 0: Error(Status.message)

		# Обработка команды: newpart.
		if command_data.name == "newpart":
			# Дополнительные данные.
			Data = dict()
			# Парсинг дополнительных значений.
			if "a" in command_data.flags: Data["announce"] = True
			if "w" in command_data.flags:
				Data["watched"] = True
				Data["announce"] = "*"
			if "comment" in command_data.keys: Data["comment"] = command_data.values["comment"]
			if "link" in command_data.keys: Data["link"] = command_data.values["link"]
			if "name" in command_data.keys: Data["name"] = command_data.values["name"]
			if "number" in command_data.keys: Data["number"] = ValueToInt(command_data.values["number"])
			if "series" in command_data.keys: Data["series"] = ValueToInt(command_data.values["series"])
			# Добавление части.
			Status = self.__Note.add_part(command_data.arguments[0], Data)
			# Обработка статуса.
			if Status.code == 0: print("Part created.")
			if Status.code != 0: Error(Status.message)

		# Обработка команды: reset.
		if command_data.name == "reset":
			# Сброс значения.
			Status = self.__Note.reset(command_data.arguments[0])
			# Обработка статуса.
			if Status.code == 0: print("Value set to default.")
			if Status.code != 0: Error(Status.message)

		# Обработка команды: set.
		if command_data.name == "set":

			# Если задаётся альтернативное название.
			if "altname" in command_data.keys:
				# Обновление названия.
				Status = self.__Note.add_another_name(command_data.values["altname"])
				# Обработка статуса.
				if Status.code == 0: print("Another name added.")
				if Status.code != 0: Error(Status.message)

			# Если задаётся группа.
			if "group" in command_data.keys:
				# Установка принадлежности к группе.
				Status = self.__Note.set_group(int(command_data.values["group"]))
				# Обработка статуса.
				if Status.code == 0: print("Note has been added to @" + command_data.values["group"] + " group.")
				if Status.code != 0: Error(Status.message)

			# Если задаётся оценка.
			if "estimation" in command_data.keys:
				# Обновление оценки.
				Status = self.__Note.estimate(int(command_data.values["estimation"]))
				# Обработка статуса.
				if Status.code == 0: print("Estimation updated.")
				if Status.code != 0: Error(Status.message)

			# Если задаётся название.
			if "name" in command_data.keys:
				# Обновление названия.
				Status = self.__Note.rename(command_data.values["name"])
				# Обработка статуса.
				if Status.code == 0: print("Name updated.")
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
			self.__View()

class ViewsTableCLI:
	"""Обработчик взаимодействий с таблицей через CLI."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		return self.__Commands

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GenerateCommands(self) -> list[Command]:
		"""Генерирует список команд."""

		# Список команд.
		CommandsList = list()

		# Создание команды: delgroup.
		Com = Command("delgroup")
		Com.add_argument(ArgumentsTypes.Number, important = True)
		CommandsList.append(Com)

		# Создание команды: list.
		Com = Command("list")
		Com.add_key_position(["group"], ArgumentsTypes.Number)
		CommandsList.append(Com)

		# Создание команды: new.
		Com = Command("new")
		CommandsList.append(Com)

		# Создание команды: newgroup.
		Com = Command("newgroup")
		Com.add_argument(ArgumentsTypes.All, important = True)
		CommandsList.append(Com)

		return CommandsList

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "ViewsTable"):
		"""
		Обработчик взаимодействий с таблицей через CLI.
			table – объектное представление таблицы.
		"""

		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# Объектное представление таблицы.
		self.__Table = table
		# Список дескрипторов команд.
		self.__Commands = self.__GenerateCommands()

	def execute(self, command_data: CommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

		# Обработка команды: delgroup.
		if command_data.name == "delgroup":
			# Создание новой группы.
			Status = self.__Table.remove_group(command_data.arguments[0])
			# Обработка статуса.
			if Status.code == 0: print(f"Group @" + str(command_data.arguments[0]) + " removed.")
			if Status.code != 0: Error(Status.message)

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
					"Name": [],
					"Estimation": [],
					"Group": []
				}

				# Если включена фильтрация по группе.
				if "group" in command_data.keys:

					# Для каждой записи.
					for Note in Notes:

						# Если запись принадлежит к искомой группе.
						if Note.group_id == int(command_data.values["group"]):
							# Получение данных.
							Name = Note.name if Note.name else ""
							GroupName = f"@{Note.group_id}" if not self.__Table.get_group(Note.group_id) else self.__Table.get_group(Note.group_id)["name"]
							if GroupName == "@None": GroupName = ""
							Status = Note.status
							# Выделение статусов цветом.
							if Status == "announce": Status = TextStyler(Status, text_color = Styles.Colors.Blue)
							if Status == "watching": Status = TextStyler(Status, text_color = Styles.Colors.Yellow)
							if Status == "complete": Status = TextStyler(Status, text_color = Styles.Colors.Green)
							if Status == "dropped": Status = TextStyler(Status, text_color = Styles.Colors.Red)
							# Заполнение колонок.
							Content["ID"].append(Note.id)
							Content["Status"].append(Status)
							Content["Name"].append(Name)
							Content["Estimation"].append(Note.estimation if Note.estimation else "")
							Content["Group"].append(GroupName)

				else:
				
					# Для каждой записи.
					for Note in Notes:
						# Получение данных.
						Name = Note.name if Note.name else ""
						GroupName = f"@{Note.group_id}" if not self.__Table.get_group(Note.group_id) else self.__Table.get_group(Note.group_id)["name"]
						if GroupName == "@None": GroupName = ""
						Status = Note.status
						# Выделение статусов цветом.
						if Status == "announce": Status = TextStyler(Status, text_color = Styles.Colors.Blue)
						if Status == "watching": Status = TextStyler(Status, text_color = Styles.Colors.Yellow)
						if Status == "complete": Status = TextStyler(Status, text_color = Styles.Colors.Green)
						if Status == "dropped": Status = TextStyler(Status, text_color = Styles.Colors.Red)
						# Заполнение колонок.
						Content["ID"].append(Note.id)
						Content["Status"].append(Status)
						Content["Name"].append(Name)
						Content["Estimation"].append(Note.estimation if Note.estimation else "")
						Content["Group"].append(GroupName)

				# Буфер проверки значения.
				ContentBuffer = list(Content["Group"])
				while "" in ContentBuffer: ContentBuffer.remove("")
				# Если в таблице нет групп, удалить их колонку.
				if len(ContentBuffer) == 0: del Content["Group"]
				# Вывод описания.
				Columns(Content)

			else:
				# Вывод в консоль: таблица пуста.
				print("Table is empty.")

		# Обработка команды: new.
		if command_data.name == "new":
			# Создание новой записи.
			Status = self.__Table.create_note()
			# Обработка статуса.
			if Status.code == 0: print(f"Note #" + str(Status.data["id"]) + " created.")
			if Status.code != 0: Error("unable_to_create_note")

		# Обработка команды: newgroup.
		if command_data.name == "newgroup":
			# Создание новой группы.
			Status = self.__Table.create_group(command_data.arguments[0])
			# Обработка статуса.
			if Status.code == 0: print(f"Group @" + str(Status.data["id"]) + " created.")
			if Status.code != 0: Error(Status.message)

#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class ViewsNote:
	"""Запись просмотра медиаконтента."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	# Пустая структура записи.
	BASE_NOTE = {
		"name": None,
		"another-names": [],
		"estimation": None,
		"status": None,
		"group": None,
		"tags": [],
		"metainfo": {},
		"parts": []
	}

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> ViewsNoteCLI:
		"""Обработчик CLI записи."""

		return self.__NoteCLI

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self.__Data["another-names"]

	@property
	def emoji_status(self) -> str:
		"""Статус просмотра в видзе эмодзи."""

		# Определения статусов.
		Statuses = {
			"announced": "ℹ️",
			"watching": "▶️",
			"complete": "✅",
			"dropped": "⛔",
			None: ""
		}

		return Statuses[self.__Data["status"]]

	@property
	def estimation(self) -> int | None:
		"""Оценка."""

		return self.__Data["estimation"]

	@property
	def group_id(self) -> int | None:
		"""Идентификатор группы."""

		return self.__Data["group"]

	@property
	def id(self) -> int:
		"""Идентификатор."""

		return self.__ID

	@property
	def metainfo(self) -> dict:
		"""Метаданные."""

		return self.__Data["metainfo"]

	@property
	def name(self) -> str | None:
		"""Название."""

		return self.__Data["name"]

	@property
	def parts(self) -> list[dict]:
		"""Список частей."""

		return list(self.__Data["parts"])

	@property
	def progress(self) -> float:
		"""Прогресс просмотра."""

		# Прогресс.
		Progress = 0
		# Максимальное значение прогресса.
		MaxProgress = 0
		# Текущий прогресс.
		CurrentProgress = 0
		# Список частей.
		Parts = self.parts

		# Если есть части.
		if Parts:

			# Для каждой части.
			for Part in self.parts:

				# Если есть серии.
				if "series" in Part.keys() and Part["series"] != None:
					# Подсчёт серий.
					MaxProgress += Part["series"]

				else:
					# Инкремент.
					MaxProgress += 1

			# Для каждой части.
			for Part in self.parts:

				# Если часть просмотрена и есть серии.
				if Part["watched"] and "series" in Part.keys() and Part["series"] != None:
					# Подсчёт серий.
					CurrentProgress += Part["series"] if "mark" not in Part.keys() else Part["mark"]

				elif Part["watched"]:
					# Инкремент.
					CurrentProgress += 1

			# Подсчёт прогресса.
			Progress = int(CurrentProgress / MaxProgress * 100)

		return Progress

	@property
	def status(self) -> str | None:
		"""Статус просмотра."""

		return self.__Data["status"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return list(self.__Data["tags"])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetBasePart(self, part_type: str) -> dict:
		"""
		Возвращает стандартную словарную структуру части.
			part_type – тип части.
		"""

		# Типы: сезон.
		if part_type in ["season"]: return {
			"type": part_type,
			"number": None,
			"series": None,
			"watched": False
		}

		# Типы: фильм.
		if part_type in ["film", "special"]: return {
			"type": part_type,
			"name": None,
			"watched": False
		}

		# Типы: ONA, OVA, специальные выпуски.
		if part_type in ["ONA", "OVA", "specials"]: return {
			"type": part_type,
			"series": None,
			"watched": False
		}

	def __ModifyPart(self, part: dict, data: dict) -> dict:
		"""
		Подставляет типовые значения в часть.
			part – словарное представление части;
			data – словарь данных для подстановки в часть.
		"""
		
		# Для каждого значения из переданных данных.
		for Key in data.keys():

			# Если ключ в списке опциональных.
			if Key in ["announce", "comment", "link", "name", "number"]:

				# Если значение не удаляется.
				if data[Key] != "*":
					# Добавление нового значения.
					part[Key] = data[Key]

				# Если опциональное значение определено.
				elif Key in part.keys():
					# Удаление опционального значения.
					del part[Key]

			# Если ключ удаляет закладку.
			elif Key == "watched":
				# Если просмотрено, удалить закладку.
				if data["watched"] and "mark" in part.keys(): del part["mark"]
				# Обновление статуса просмотра.
				part[Key] = data[Key]

			else:
				# Если ключ определён в части, перезаписать данные.
				if Key in part.keys(): part[Key] = data[Key]

		return part

	def __UpdateStatus(self):
		"""Обновляет статус просмотра."""

		# Если не заброшено.
		if self.__Data["status"] != "dropped":
			# Получение прогресса.
			Progress = self.progress
			# Обработка статусов.
			if Progress == None: self.__Data["status"] = None
			elif Progress == 100: self.__Data["status"] = "complete"
			else: self.__Data["status"] = "watching"

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "ViewsTable", note_id: int):
		"""
		Запись просмотра медиаконтента.
			table – объектное представление таблицы;
			note_id – идентификатор записи.
		"""
		
		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# ID записи.
		self.__ID = note_id
		# Объектное представление таблицы.
		self.__Table = table
		# Данные записи.
		self.__Data = ReadJSON(f"{table.directory}/{table.name}/{self.__ID}.json")
		# Обработчик CLI записи.
		self.__NoteCLI = ViewsNoteCLI(table, self)
	
	def add_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Добавляет альтернативное название.
			another_name – альтернативное название.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если такое альтренативное название ещё не задано.
			if another_name not in self.__Data["another-names"]:
				# Добавление алтернативного названия.
				self.__Data["another-names"].append(another_name)
				# Сохранение изменений.
				self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def add_part(self, part_type: str, data: dict) -> ExecutionStatus:
		"""
		Добавляет новую часть.
			part_type – тип части;
			data – данные для заполнения свойств части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Буфер части.
			Buffer = self.__GetBasePart(part_type)
			# Подстановка данных.
			Buffer = self.__ModifyPart(Buffer, data)
			# Добавление новой части.
			self.__Data["parts"].append(Buffer)
			# Обновление статуса просмотра.
			self.__UpdateStatus()
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def add_tag(self, tag: str) -> ExecutionStatus:
		"""
		Добавляет тег.
			tag – название тега.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если тег ещё не задан.
			if tag not in self.__Data["tags"]:
				# Добавление нового тега.
				self.__Data["tags"].append(tag)
				# Сохранение изменений.
				self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def delete_another_name(self, another_name: int | str) -> ExecutionStatus:
		"""
		Удаляет альтернативное название.
			another_name – альтернативное название или его индекс.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если передан индекс.
			if another_name.isdigit():
				# Удаление альтернативного названия по индексу.
				self.__Data["another-names"].pop(int(another_name))

			else:
				# Удаление альтернативного названия по значению.
				self.__Data["another-names"].remove(another_name)

			# Сохранение изменений.
			self.save()

		except IndexError:
			# Изменение статуса.
			Status = ExecutionStatus(1, "incorrect_another_name_index")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def delete_metainfo(self, key: str) -> ExecutionStatus:
		"""
		Удаляет метаданные.
			key – ключ метаданных.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Удаление метаданных.
			del self.__Data["metainfo"][key]
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def delete_part(self, part_index: int) -> ExecutionStatus:
		"""
		Удаляет часть.
			index – индекс части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Удаление части.
			del self.__Data["parts"][part_index]
			# Обновление статуса просмотра.
			self.__UpdateStatus()
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def delete_tag(self, tag: int | str) -> ExecutionStatus:
		"""
		Удаляет тег.
			tag – тег или его индекс.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если передан индекс.
			if tag.isdigit():
				# Удаление тега по индексу.
				self.__Data["tags"].pop(int(tag))

			else:
				# Удаление тега по значению.
				self.__Data["tags"].remove(tag)

			# Сохранение изменений.
			self.save()

		except IndexError:
			# Изменение статуса.
			Status = ExecutionStatus(1, "incorrect_tag_index")

		except IndexError:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def down_part(self, part_index: int) -> ExecutionStatus:
		"""
		Опускает часть на одну позицию вниз.
			part_index – индекс части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если не последняя часть.
			if part_index != len(self.__Data["parts"]) - 1:
				# Перемещение части вверх.
				self.__Data["parts"].insert(part_index + 1, self.__Data["parts"].pop(part_index))
				# Сохранение изменений.
				self.save()

			# Если последняя часть.
			elif part_index == len(self.__Data["parts"]) - 1:
				# Изменение статуса.
				Status = ExecutionStatus(1, "unable_down_last_part")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def edit_part(self, part_index: int, data: dict) -> ExecutionStatus:
		"""
		Редактирует свойства части.
			part_index – индекс части;
			data – данные для обновления свойств части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Подстановка данных.
			self.__Data["parts"][part_index] = self.__ModifyPart(self.__Data["parts"][part_index], data)
			# Обновление статуса просмотра.
			self.__UpdateStatus()
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def estimate(self, estimation: int) -> ExecutionStatus:
		"""
		Выставляет оценку.
			estimation – оценка.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если оценка в допустимом диапазоне.
			if estimation <= self.__Table.options["max-estimation"]:
				# Выставление оценки.
				self.__Data["estimation"] = estimation
				# Сохранение изменений.
				self.save()

			else:
				# Изменение статуса.
				Status = ExecutionStatus(1, "max_estimation_exceeded")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает запись.
			name – название записи.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Изменение имени.
			self.__Data["name"] = name
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def reset(self, key: str) -> ExecutionStatus:
		"""
		Сбрасывает поле к стандартному значению.
			key – ключ поля.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Сброс значения.
			self.__Data[key] = type(self.BASE_NOTE[key])()
			# Обновление статуса просмотра.
			self.__UpdateStatus()
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def save(self):
		"""Сохраняет запись в локальный файл."""

		# Сохранение записи.
		WriteJSON(f"{self.__Table.directory}/{self.__Table.name}/{self.__ID}.json", self.__Data)

	def set_group(self, group_id: int) -> ExecutionStatus:
		"""
		Устанавливает принадлежность к группе.
			group_id – идентификатор группы.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Сброс значения.
			self.__Data["group"] = group_id
			# Добавление элемента в группу.
			self.__Table.add_group_element(group_id, self.__ID)
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def set_mark(self, part_index: int, mark: int) -> ExecutionStatus:
		"""
		Добавляет закладку на серию.
			part_index – индекс части;
			mark – номер серии для постановки закладки (0 для удаления закладки, номер последней серии для пометки всей части как просмотренной).
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если часть многосерийная.
			if "series" in self.__Data["parts"][part_index].keys():

				# Если закладка установлена на просмотренную часть.
				if self.__Data["parts"][part_index]["watched"]:
					# Снятие статуса полностью просмотренного и установка закладки.
					self.__Data["parts"][part_index]["watched"] = False
					self.__Data["parts"][part_index]["mark"] = mark
					# Обновление статуса просмотра.
					self.__UpdateStatus()
					# Сохранение изменений.
					self.save()
					# Изменение статуса.
					Status = ExecutionStatus(2, "Part marked as unseen.")

				else:

					# Если закладка лежит в диапазоне серий.
					if mark < self.__Data["parts"][part_index]["series"] and mark != 0:
						# Обновление закладки.
						self.__Data["parts"][part_index]["mark"] = mark

					# Если закладка на последней серии.
					elif mark == self.__Data["parts"][part_index]["series"]:
						# Добавление статуса полностью просмотренного и удаление закладки.
						self.__Data["parts"][part_index]["watched"] = True
						if "mark" in self.__Data["parts"][part_index].keys(): del self.__Data["parts"][part_index]["mark"]
						# Изменение статуса.
						Status = ExecutionStatus(1, "Part marked as fully viewed.")

					# Если закладка на нулевой серии.
					elif mark == 0:
						# Удаление закладки.
						del self.__Data["parts"][part_index]["mark"]
						# Изменение статуса.
						Status = ExecutionStatus(3, "Mark removed.")

					# Сохранение изменений.
					self.save()
					# Обновление статуса просмотра.
					self.__UpdateStatus()

			else:
				# Изменение статуса.
				Status = ExecutionStatus(-2, "only_series_supports_marks")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def set_metainfo(self, key: str, metainfo: str) -> ExecutionStatus:
		"""
		Задаёт метаданные.
			key – ключ метаданных;
			metainfo – значение метаданных.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Установка метаданных.
			self.__Data["metainfo"][key] = metainfo
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def set_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус.
			status – статус просмотра.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)
		# Определения статусов.
		Statuses = {
			"w": "watching",
			"c": "complete",
			"d": "dropped",
			"*": None
		}

		try:
			# Установка статуса.
			self.__Data["status"] = Statuses[status]
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def up_part(self, part_index: int) -> ExecutionStatus:
		"""
		Поднимает часть на одну позицию вверх.
			part_index – индекс части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если не первая часть.
			if part_index != 0:
				# Перемещение части вверх.
				self.__Data["parts"].insert(part_index - 1, self.__Data["parts"].pop(part_index))
				# Сохранение изменений.
				self.save()

			# Если первая часть.
			elif part_index == 0:
				# Изменение статуса.
				Status = ExecutionStatus(1, "unable_up_first_part")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

class ViewsTable:
	"""Таблица просмотров медиакнотента."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> ViewsTableCLI:
		"""Обработчик CLI таблицы."""

		return self.__TableCLI

	@property
	def directory(self) -> str:
		"""Путь к каталогу таблицы."""

		return self.__StorageDirectory

	@property
	def id(self) -> list[ViewsNote]:
		"""Идентификатор таблицы."""

		return self.__Notes.values()

	@property
	def max_estimation(self) -> int:
		"""Максимальная допустимая оценка."""

		return self.__Options["max-estimation"]

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self.__Name

	@property
	def notes(self) -> list[ViewsNote]:
		"""Список записей."""

		return self.__Notes.values()

	@property
	def options(self) -> dict:
		"""Словарь опций таблицы."""

		return self.__Options.copy()	

	@property
	def type(self) -> str:
		"""Тип таблицы."""

		return self.__Type

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Create(self):
		"""Создаёт каталог и файл описания таблицы."""

		# Если каталог не существует, создать его.
		if not os.path.exists(f"{self.__StorageDirectory}/{self.__Name}"): os.makedirs(f"{self.__StorageDirectory}/{self.__Name}")
		# Сохранение описания.
		WriteJSON(f"{self.__StorageDirectory}/{self.__Name}/manifest.json", self.__Options)

	def __GetNewID(self, container: dict) -> int:
		"""
		Генерирует ID для новой записи или группы.
			container – контейнер записи или группы.
		"""

		# Новый ID.
		NewID = None

		# Если включено использование освободившихся ID.
		if self.__Options["recycle-id"]:
			# Список ID.
			ListID = container.keys()

			# Для каждого значения ID до максимального.
			for ID in range(1, len(ListID) + 1):

				# Если ID свободен.
				if ID not in ListID:
					# Выбор ID.
					NewID = ID
					# Остановка цикла.
					break

		# Если ID не назначен.
		if not NewID:
			# Назначение нового ID методом инкремента максимального.
			NewID = int(max(container.keys())) + 1 if len(container.keys()) > 0 else 1

		return NewID

	def __GetNotesListID(self) -> list[int]:
		"""Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON."""

		# Список ID.
		ListID = list()
		# Получение списка файлов в таблице.
		Files = os.listdir(f"{self.__StorageDirectory}/{self.__Name}")
		# Фильтрация только файлов формата JSON.
		Files = list(filter(lambda File: File.endswith(".json"), Files))

		# Для каждого файла.
		for File in Files: 
			# Если название файла не является числом, удалить его.
			if not File.replace(".json", "").isdigit(): Files.remove(File)

		# Для каждого файла получить и записать ID.
		for File in Files: ListID.append(int(File.replace(".json", "")))
		
		return ListID

	def __ReadNote(self, note_id: int):
		"""
		Считывает содержимое записи.
			note_id – идентификатор записи.
		"""

		# Чтение записи.
		self.__Notes[note_id] = ViewsNote(self, note_id)

	def __ReadNotes(self):
		"""Считывает содержимое всех записей."""

		# Получение списка ID записей.
		ListID = self.__GetNotesListID()

		# Для каждого ID записи.
		for ID in ListID:
			# Чтение записи.
			self.__ReadNote(ID)

	def __SaveGroups(self):
		"""Сохраняет описание группы в локальный файл."""

		# Если определения групп остались.
		if len(self.__Groups.keys()) > 0:
			# Сохранение локального файла JSON.
			WriteJSON(f"{self.__StorageDirectory}/{self.__Name}/groups.json", self.__Groups)

		else:
			# Удаление локального файла.
			os.remove(f"{self.__StorageDirectory}/{self.__Name}/groups.json")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, storage_dir: str, name: str, autocreation: bool = True):
		"""
		Таблица просмотров медиакнотента.
			storage_dir – директория хранения таблиц;
			name – название таблицы;
			autocreation – указывает, нужно ли создавать таблицу при отсутствии таковой. 
		"""
		
		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# Директория хранения таблиц.
		self.__StorageDirectory = storage_dir.rstrip("/\\")
		# Имя таблицы.
		self.__Name = name
		# Словарь записей.
		self.__Notes = dict()
		# Словарь групп.
		self.__Groups = dict()
		# Тип таблицы.
		self.__Type = "views"
		# Опции таблицы.
		self.__Options = {
			"version": 1,
			"type": self.__Type,
			"recycle-id": False,
			"max-estimation": 10,
			"viewer": {
				"links": True,
				"comments": True
			}
		}
		# Обработчик CLI таблицы.
		self.__TableCLI = ViewsTableCLI(self)

		# Если найден файл описания таблицы.
		if os.path.exists(f"{self.__StorageDirectory}/{self.__Name}/manifest.json"):
			# Чтение файла.
			self.__Options = ReadJSON(f"{self.__StorageDirectory}/{self.__Name}/manifest.json")
			# Если тип таблицы не соответствует, выбросить исключение.
			if self.__Options["type"] != self.__Type: raise TypeError(f"Only \"{self.__Type}\" type tables supported.")
			# Чтение записей.
			self.__ReadNotes()

		# Если включено автосоздание таблицы.
		elif autocreation:
			# Создание таблицы.
			self.__Create()

		# Выброс исключения
		else: raise FileExistsError("manifest.json")

		# Если найден файл описания групп.
		if os.path.exists(f"{self.__StorageDirectory}/{self.__Name}/groups.json"):
			# Чтение групп.
			self.__Groups = ReadJSON(f"{self.__StorageDirectory}/{self.__Name}/groups.json")

	def add_group_element(self, group_id: int, note_id: int):
		"""
		Добавляет идентификатор записи в элементы группы.
			group_id – идентификатор группы;
			note_id – идентификатор записи.
		"""

		# Данные группы.
		Group = self.get_group(group_id)
		# Если элемент ещё не в группе, добавить его.
		if note_id not in Group["elements"]: Group["elements"].append(note_id)
		# Сохранение групп в локальный файл.
		self.__SaveGroups()

	def create_group(self, name: str) -> ExecutionStatus:
		"""
		Создаёт группу для объединения записей.
			name – название группы.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# ID новой группы.
			ID = self.__GetNewID(self.__Groups)
			# Заполнение структуры группы.
			self.__Groups[str(ID)] = {
				"name": name,
				"elements": []
			}
			# Сохранение групп в локальный файл.
			self.__SaveGroups()
			# Изменение статуса.
			Status = ExecutionStatus(0, data = {"id": ID})

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def create_note(self) -> ExecutionStatus:
		"""Создаёт запись."""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# ID новой записи.
			ID = self.__GetNewID(self.__Notes)
			# Сохранение локального файла JSON.
			WriteJSON(f"{self.__StorageDirectory}/{self.__Name}/{ID}.json", ViewsNote.BASE_NOTE)
			# Чтение и объектная интерпретация записи.
			self.__ReadNote(ID)
			# Изменение статуса.
			Status = ExecutionStatus(0, data = {"id": ID})

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Переименование каталога.
			os.rename(f"{self.__StorageDirectory}/{self.__Name}", f"{self.__StorageDirectory}/{name}")
			# Перезапись имени.
			self.__Name = name

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status
		
	def remove_group(self, group_id: int) -> ExecutionStatus:
		"""
		Удаляет группу. 
			group_id – идентификатор группы.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Приведение ID к строковому типу.
			group_id = str(group_id)
			# Удаление группы из словаря.
			del self.__Groups[group_id]
			# Сохранение групп в локальный файл.
			self.__SaveGroups()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def remove_note(self, note_id: int) -> ExecutionStatus:
		"""
		Удаляет запись из таблицы. 
			note_id – идентификатор записи.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Приведение ID к целочисленному типу.
			note_id = int(note_id)
			# Удаление записи из словаря.
			del self.__Notes[note_id]
			# Удаление локального файла.
			os.remove(f"{self.__StorageDirectory}/{self.__Name}/{note_id}.json")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def get_group(self, group_id: int) -> dict | None:
		"""
		Возвращает словарное представление группы.
			group_id – идентификатор группы.
		"""

		# Группа.
		Group = None
		# Приведение ID к строковому типу.
		group_id = str(group_id)
		# Если группа существует, записать её определение.
		if group_id in self.__Groups.keys(): Group = self.__Groups[group_id]

		return Group

	def get_group_notes(self, group_id: int) -> list[ViewsNote]:
		"""
		Возвращает словарное представление группы.
			group_id – идентификатор группы.
		"""

		# Список записей.
		NotesList = list()
		
		# Для каждой записи.
		for Note in self.notes:
			# Если запись включена в указанную группу, добавить её в список.
			if note.group == group_id: NotesList.append(Note)

		return NotesList

	def get_note(self, note_id: int) -> ViewsNote | None:
		"""
		Возвращает объектное представление записи.
			note_id – идентификатор записи.
		"""

		# Запись.
		Note = None

		try:
			# Приведение ID к целочисленному типу.
			note_id = int(note_id)
			# Осуществление доступа к записи.
			Note = self.__Notes[note_id]

		except: pass

		return Note