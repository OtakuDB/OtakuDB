from Source.CLI.Templates import Columns

from dublib.CLI.StyledPrinter import Styles, StylesGroup, StyledPrinter, TextStyler
from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.Engine.Bus import ExecutionError, ExecutionWarning, ExecutionStatus
from dublib.Methods.JSON import ReadJSON, WriteJSON
from dublib.CLI.Templates import Confirmation

import os

#==========================================================================================#
# >>>>> ОБРАБОТЧИКИ ВЗАИМОДЕЙСТВИЙ С ТАБЛИЦЕЙ <<<<< #
#==========================================================================================#

class AnimeNoteCLI:
	"""Обработчик взаимодействий с записью через CLI."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
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
		Com = Command("delpart", "Remove part.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		CommandsList.append(Com)

		# Создание команды: downpart.
		Com = Command("downpart", "Omit part in list.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		CommandsList.append(Com)

		# Создание команды: editpart.
		Com = Command("editpart", "Edit part.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		Com.add_flag("a", description = "Mark part as announced.")
		Com.add_flag("s", description = "Mark part as skipped.")
		Com.add_flag("u", description = "Mark part as unwatched.")
		Com.add_flag("w", description = "Mark part as watched.")
		Com.add_key("comment", description = "Add comment to part.")
		Com.add_key("link", ParametersTypes.URL, description = "Attach link to part.")
		Com.add_key("name", description = "Set name of part.")
		Com.add_key("number", description = "Set number of part (not index).")
		Com.add_key("series", ParametersTypes.Number, description = "Set series count.")
		CommandsList.append(Com)

		# Создание команды: mark.
		Com = Command("mark", "Set bookmark to series.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		Com.add_argument(ParametersTypes.Number, description = "Bookmark.", important = True)
		CommandsList.append(Com)

		# Создание команды: meta.
		Com = Command("meta", "Manage note metainfo fields.")
		Com.add_argument(ParametersTypes.All, description = "Field name.", important = True)
		Com.add_argument(ParametersTypes.All, description = "Field value.")
		Com.add_flag("set", description = "Create new or update exists field.", important = True)
		Com.add_flag("unset", description = "Remove field.", important = True)
		CommandsList.append(Com)

		# Создание команды: newpart.
		Com = Command("newpart", "Create new part.")
		Com.add_argument(description = "Part type.", important = True)
		Com.add_flag("a", description = "Mark part as announced.")
		Com.add_flag("s", description = "Mark part as skipped.")
		Com.add_flag("u", description = "Mark part as unwatched.")
		Com.add_flag("w", description = "Mark part as watched.")
		Com.add_key("comment", description = "Add comment to part.")
		Com.add_key("link", ParametersTypes.URL, description = "Attach link to part.")
		Com.add_key("name", description = "Set name of part.")
		Com.add_key("number", description = "Set number of part (not index).")
		Com.add_key("series", ParametersTypes.Number, description = "Set series count.")
		CommandsList.append(Com)

		# Создание команды: set.
		Com = Command("set", "Set note values.")
		Com.add_key("altname", description = "Alternative name.")
		Com.add_key("estimation", ParametersTypes.Number, "Note estimation.")
		Com.add_key("group", ParametersTypes.Number, description = "Group ID.")
		Com.add_key("name", description = "Note name.")
		Com.add_key("status", description = "View status.")
		Com.add_key("tag", description = "Tag.")
		CommandsList.append(Com)

		# Создание команды: unset.
		Com = Command("unset", "Remove alternative names or tags.")
		ComPos = Com.create_position("TARGET", "Target to remove.", important = True)
		ComPos.add_key("altname", ParametersTypes.Number, "Index of alternative name.")
		ComPos.add_key("tag", description = "Tag.")
		CommandsList.append(Com)

		# Создание команды: uppart.
		Com = Command("uppart", "Raise part.")
		Com.add_argument(ParametersTypes.Number, "Part index.", important = True)
		CommandsList.append(Com)

		# Создание команды: view.
		Com = Command("view", "View note in console.")
		CommandsList.append(Com)

		return CommandsList

	def __View(self):
		"""Выводит форматированные данные записи."""

		#---> Получение данных.
		#==========================================================================================#
		# Описание группы.
		Group = self.__Table.get_group(self.__Note.group_id) if self.__Note.group_id else None
		# Название группы.
		GroupName = Group["name"] if Group and Group["name"] else None
		# Части записи.
		Parts = self.__Note.parts
		# Настройки просмоторщика.
		Options = self.__Table.options["viewer"]

		#---> Объявление литералов.
		#==========================================================================================#
		# Общий прогресс просмотра.
		MSG_TotalProgress = f" ({self.__Note.progress}% viewed)" if self.__Note.progress else ""
		# Название группы. 
		MSG_GroupName = f"@{self.__Note.group_id}" if not GroupName else f"@{GroupName}"

		#---> Вывод описания записи.
		#==========================================================================================#
		# Если у записи есть название, вывести его.
		if self.__Note.name: StyledPrinter(self.__Note.name, decorations = [Styles.Decorations.Bold], end = False)
		# Вывод в консоль: общий прогресс просмотра.
		print(f"{MSG_TotalProgress} {self.__Note.emoji_status}")
		# Вывести в консоль каждое альтернативное название.
		for AnotherName in self.__Note.another_names: StyledPrinter(f"    {AnotherName}", decorations = [Styles.Decorations.Italic])
		# Если задана оценка, вывести её.
		if self.__Note.estimation: print(f"⭐ {self.__Note.estimation} / {self.__Table.max_estimation}")

		#---> Вывод классификаторов записи.
		#==========================================================================================#

		# Если задана группа.
		if self.__Note.group_id:
			# Вывод в консоль: заголовок группы.
			StyledPrinter(f"GROUP: ", decorations = [Styles.Decorations.Bold], end = False)
			# Вывод в консоль: название группы.
			StyledPrinter(MSG_GroupName, decorations = [Styles.Decorations.Italic])

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

		#---> Вывод частей записи.
		#==========================================================================================#

		# Если имеются части.
		if Parts:
			# Вывод в консоль: заголовок частей.
			StyledPrinter(f"PARTS:", decorations = [Styles.Decorations.Bold])

			# Для каждой части.
			for PartIndex in range(0, len(Parts)):

				#---> Объявление литералов.
				#==========================================================================================#
				# Эмодзи-статус части.
				MSG_PartStatus = ""
				if "watched" in Parts[PartIndex].keys(): MSG_PartStatus = " ✅"
				if "announced" in Parts[PartIndex].keys(): MSG_PartStatus = " ℹ️"
				if "skipped" in Parts[PartIndex].keys(): MSG_PartStatus = " 🚫"
				# Название части.
				MSG_Name = " " + Parts[PartIndex]["name"] if "name" in Parts[PartIndex].keys() and Parts[PartIndex]["name"] else ""
				# Номер.
				MSG_Number = " " + str(Parts[PartIndex]["number"]) if "number" in Parts[PartIndex].keys() and Parts[PartIndex]["number"] else ""
				# Отступ (рассчитывается от длины индекса).
				MSG_Indent = " " * len(str(PartIndex))
				# Тип записи.
				MSG_Type = Parts[PartIndex]["type"]

				#---> Определение цвета части.
				#==========================================================================================#
				# Цвет текста.
				TextColor = None
				# Установка цветов.
				if Options["colorize"] and "✅" in MSG_PartStatus: TextColor = StylesGroup(text_color = Styles.Colors.Green)
				if Options["colorize"] and "ℹ️" in MSG_PartStatus: TextColor = StylesGroup(text_color = Styles.Colors.Cyan)
				if Options["colorize"] and "🚫" in MSG_PartStatus: TextColor = StylesGroup(text_color = Styles.Colors.Blue)

				# Если часть многосерийная.
				if "series" in Parts[PartIndex].keys():

					#---> Объявление литералов.
					#==========================================================================================#
					# Закладка.
					MSG_Mark = str(Parts[PartIndex]["mark"]) + " / " if "mark" in Parts[PartIndex] else ""
					# Индикатор закладки.
					MSG_MarkIndicator = " ⏳" if MSG_Mark else ""
					# Прогресс просмотра части.
					MSG_Progress = " (" + str(int(Parts[PartIndex]["mark"] / Parts[PartIndex]["series"] * 100)) + "% viewed)" if MSG_Mark else ""
					# Количество серий. 
					MSG_Series = Parts[PartIndex]["series"]

					#---> Определение цвета части.
					#==========================================================================================#
					# Если часть в процессе просмотра, назначить ей жёлтый цвет.
					if Options["colorize"] and "⏳" in MSG_MarkIndicator: TextColor = StylesGroup(text_color = Styles.Colors.Yellow)

					#---> Вывод части.
					#==========================================================================================#
					# Вывод в консоль: данные части.
					StyledPrinter(f"    {PartIndex} ▸ {MSG_Type}{MSG_Number}:{MSG_Name}{MSG_PartStatus}{MSG_MarkIndicator}", styles = TextColor)
					# Если в части больше одной серии, вывести в консоль прогресс просмотра.
					if not Options["hide_single_series"] or Options["hide_single_series"] and MSG_Series and MSG_Series > 1: StyledPrinter(f"    {MSG_Indent}       {MSG_Mark}{MSG_Series} series{MSG_Progress}", styles = TextColor)

				else:
					# Вывод в консоль: данные части.
					StyledPrinter(f"    {PartIndex} ▸ {MSG_Type}{MSG_Number}:{MSG_Name}{MSG_PartStatus}", styles = TextColor)

				# Вывод в консоль: ссылки и комментарии.
				if Options["links"] and "link" in Parts[PartIndex].keys(): print(f"    {MSG_Indent}       🔗 " + Parts[PartIndex]["link"])
				if Options["comments"] and "comment" in Parts[PartIndex].keys(): print(f"    {MSG_Indent}       💭 " + Parts[PartIndex]["comment"])

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "AnimeTable", note: "AnimeNote"):
		"""
		Обработчик взаимодействий с таблицей через CLI.
			table – объектное представление таблицы;
			note – объектное представление записи.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		# Объектное представление таблицы.
		self.__Table = table
		# Объектное представление записи.
		self.__Note = note
		# Список дескрипторов команд.
		self.__Commands = self.__GenerateCommands()

	def execute(self, command_data: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

		# Статус обработки команды.
		Status = None

		# Обработка команды: delpart.
		if command_data.name == "delpart":
			# Запрос подтверждения.
			Response = Confirmation("Are you sure to remove part?")
			
			# Если подтверждено.
			if Response:
				# Удаление части.
				Status = self.__Note.delete_part(int(command_data.arguments[0]))

		# Обработка команды: downpart.
		if command_data.name == "downpart":
			# Поднятие части.
			Status = self.__Note.down_part(int(command_data.arguments[0]))

		# Обработка команды: editpart.
		if command_data.name == "editpart":
			# Дополнительные данные.
			Data = dict()
			# Парсинг дополнительных значений.
			if "a" in command_data.flags: Data["announced"] = True
			if "w" in command_data.flags:
				Data["watched"] = True
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if "s" in command_data.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = True
			if "u" in command_data.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if command_data.check_key("link"): Data["link"] = command_data.get_key_value("link")
			if command_data.check_key("comment"): Data["comment"] = command_data.get_key_value("comment")
			if command_data.check_key("name"): Data["name"] = command_data.get_key_value("name")
			if command_data.check_key("number"): Data["number"] = command_data.get_key_value("number")
			if command_data.check_key("series"): Data["series"] = command_data.get_key_value("series")
			# Редактирование части.
			Status = self.__Note.edit_part(int(command_data.arguments[0]), Data)

		# Обработка команды: mark.
		if command_data.name == "mark":
			# Добавление закладки.
			Status = self.__Note.set_mark(int(command_data.arguments[0]), int(command_data.arguments[1]))

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

		# Обработка команды: newpart.
		if command_data.name == "newpart":
			# Дополнительные данные.
			Data = dict()
			# Парсинг дополнительных значений.
			if "a" in command_data.flags: Data["announced"] = True
			if "w" in command_data.flags:
				Data["watched"] = True
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if "s" in command_data.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = True
			if "u" in command_data.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if "comment" in command_data.keys.keys(): Data["comment"] = command_data.keys["comment"]
			if "link" in command_data.keys.keys(): Data["link"] = command_data.keys["link"]
			if "name" in command_data.keys.keys(): Data["name"] = command_data.keys["name"]
			if "number" in command_data.keys.keys(): Data["number"] = command_data.keys["number"]
			if "series" in command_data.keys.keys(): Data["series"] = command_data.keys["series"]
			# Добавление части.
			Status = self.__Note.add_part(command_data.arguments[0], Data)

		# Обработка команды: set.
		if command_data.name == "set":

			# Если задаётся альтернативное название.
			if "altname" in command_data.keys.keys():
				# Обновление названия.
				Status = self.__Note.add_another_name(command_data.keys["altname"])

			# Если задаётся группа.
			if "group" in command_data.keys.keys():
				# Установка принадлежности к группе.
				Status = self.__Note.set_group(int(command_data.keys["group"]))

			# Если задаётся оценка.
			if "estimation" in command_data.keys.keys():
				# Обновление оценки.
				Status = self.__Note.estimate(int(command_data.keys["estimation"]))

			# Если задаётся название.
			if "name" in command_data.keys.keys():
				# Обновление названия.
				Status = self.__Note.rename(command_data.keys["name"])

			# Если задаётся статус.
			if "status" in command_data.keys.keys():
				# Установка статуса.
				Status = self.__Note.set_status(command_data.keys["status"])

			# Если задаётся тег.
			if "tag" in command_data.keys.keys():
				# Обновление названия.
				Status = self.__Note.add_tag(command_data.keys["tag"])

		# Обработка команды: unset.
		if command_data.name == "unset":

			# Если удаляется альтернативное название.
			if "altname" in command_data.keys.keys():
				# Удаление альтернативного названия.
				Status = self.__Note.delete_another_name(command_data.keys["altname"])

			# Если удаляется тег.
			if "tag" in command_data.keys.keys():
				# Удаление тега.
				Status = self.__Note.delete_tag(command_data.keys["tag"])

		# Обработка команды: uppart.
		if command_data.name == "uppart":
			# Поднятие части.
			Status = self.__Note.up_part(int(command_data.arguments[0]))

		# Обработка команды: view.
		if command_data.name == "view":
			# Просмотр записи.
			self.__View()

		return Status

class AnimeTableCLI:
	"""Обработчик взаимодействий с таблицей через CLI."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
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
		Com = Command("delgroup", "Remove group.")
		Com.add_argument(ParametersTypes.Number, "Group ID.", important = True)
		CommandsList.append(Com)

		# Создание команды: list.
		Com = Command("list", "Show list of notes.")
		Com.add_flag("r", "Reverse list.")
		Com.add_key("group", ParametersTypes.Number, "Group ID.")
		Com.add_key("sort", ParametersTypes.Text, "Column name.")
		Com.add_key("search", description = "Part of note name.")
		CommandsList.append(Com)

		# Создание команды: new.
		Com = Command("new", "Create new note.")
		CommandsList.append(Com)

		# Создание команды: newgroup.
		Com = Command("newgroup", "Create new group.")
		Com.add_argument(ParametersTypes.All, "Group name.", important = True)
		CommandsList.append(Com)

		# Создание команды: search.
		Com = Command("search", "Search notes by part of name.")
		Com.add_argument(description = "Search query.", important = True)
		CommandsList.append(Com)

		return CommandsList

	def __List(self, command_data: ParsedCommandData, search: str | None = None):
		# Список отображаемых записей.
			Notes = list()
			# Табличное содержимое.
			Content = {
				"ID": [],
				"Status": [],
				"Name": [],
				"Estimation": [],
				"Group": []
			}
			# Режим сортировки.
			SortBy = command_data.keys["sort"].title() if "sort" in command_data.keys.keys() else "ID"
			# Приведение в верхний регистр ID.
			if SortBy == "Id": SortBy = SortBy.upper()
			# Если неизвестный ключ сортировки, вернуть ошибку.
			if SortBy not in Content.keys(): return ExecutionError(-1, "bad_sorting_parameter")
			# Проверка присутствия флага инверсии вывода.
			Reverse = command_data.check_flag("r")
			
			# Если записи существуют.
			if self.__Table.notes:

				# Если включена фильтрация по группе.
				if "group" in command_data.keys.keys():

					# Для каждой записи.
					for Note in self.__Table.notes:
						# Если запись принадлежит к искомой группе, добавить её в список вывода.
						if Note.group_id == int(command_data.keys["group"]): Notes.append(Note)

				else: Notes = self.__Table.notes

				# Если включён поиск.
				if search:
					# Вывод в консоль: поисковый запрос.
					print("Search:", TextStyler(search, text_color = Styles.Colors.Yellow))
					# Копия записей.
					NotesCopy = list(Notes)
					# Буфер поиска.
					SearchBuffer = list()

					# Для каждой записи.
					for Note in NotesCopy:
						# Список названий.
						Names = list()
						# Запись названий.
						if Note.name: Names.append(Note.name)
						if Note.another_names: Names += Note.another_names

						# Для каждого названия.
						for Name in Names:
							# Если название содержит поисковый запрос, записать его.
							if search.lower() in Name.lower(): SearchBuffer.append(Note)

					# Сохранение буфера поиска.
					Notes = SearchBuffer
				
				# Для каждой записи.
				for Note in Notes:
					# Получение данных.
					Name = Note.name if Note.name else ""
					GroupName = f"@{Note.group_id}" if not self.__Table.get_group(Note.group_id) else self.__Table.get_group(Note.group_id)["name"]
					if GroupName == "@None": GroupName = ""
					Status = Note.status
					# Выделение статусов цветом.
					if Status == "announced": Status = TextStyler(Status, text_color = Styles.Colors.Purple)
					if Status == "planned": Status = TextStyler(Status, text_color = Styles.Colors.Cyan)
					if Status == "watching": Status = TextStyler(Status, text_color = Styles.Colors.Yellow)
					if Status == "completed": Status = TextStyler(Status, text_color = Styles.Colors.Green)
					if Status == "dropped": Status = TextStyler(Status, text_color = Styles.Colors.Red)
					# Заполнение колонок.
					Content["ID"].append(Note.id)
					Content["Status"].append(Status)
					Content["Name"].append(Name if len(Name) < 60 else Name[:60] + "…")
					Content["Estimation"].append(Note.estimation if Note.estimation else "")
					Content["Group"].append(GroupName)

				# Буфер проверки значения.
				ContentBuffer = list(Content["Group"])
				while "" in ContentBuffer: ContentBuffer.remove("")
				# Если в таблице нет групп, удалить их колонку.
				if len(ContentBuffer) == 0: del Content["Group"]
				# Вывод описания.
				Columns(Content, sort_by = SortBy, reverse = Reverse)

			else:
				# Вывод в консоль: таблица пуста.
				print("Table is empty.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "AnimeTable"):
		"""
		Обработчик взаимодействий с таблицей через CLI.
			table – объектное представление таблицы.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		# Объектное представление таблицы.
		self.__Table = table
		# Список дескрипторов команд.
		self.__Commands = self.__GenerateCommands()

	def execute(self, command_data: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

		# Статус обработки команды.
		Status = None

		# Обработка команды: delgroup.
		if command_data.name == "delgroup":
			# Создание новой группы.
			Status = self.__Table.remove_group(command_data.arguments[0])

		# Обработка команды: list.
		if command_data.name == "list":
			# Вывод списка записей.
			self.__List(command_data)

		# Обработка команды: new.
		if command_data.name == "new":
			# Создание новой записи.
			Status = self.__Table.create_note()

		# Обработка команды: newgroup.
		if command_data.name == "newgroup":
			# Создание новой группы.
			Status = self.__Table.create_group(command_data.arguments[0])

		# Обработка команды: search.
		if command_data.name == "search":
			# Поиск записи.
			self.__List(command_data, command_data.arguments[0])

		return Status
	
#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class AnimeNote:
	"""Запись просмотра медиаконтента."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	# Пустая структура записи.
	BASE_NOTE = {
		"name": None,
		"another_names": [],
		"estimation": None,
		"status": None,
		"group": None,
		"tags": [],
		"metainfo": {},
		"parts": []
	}

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> AnimeNoteCLI:
		"""Обработчик CLI записи."""

		return self.__NoteCLI

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self.__Data["another_names"]

	@property
	def emoji_status(self) -> str:
		"""Статус просмотра в видзе эмодзи."""

		# Определения статусов.
		Statuses = {
			"announced": "ℹ️",
			"watching": "▶️",
			"completed": "✅",
			"dropped": "⛔",
			"planned": "🗓️",
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

				# Если часть не анонсирована и не пропущена.
				if "announced" not in Part.keys() and "skipped" not in Part.keys():

					# Если есть серии.
					if "series" in Part.keys() and Part["series"] != None:
						# Подсчёт серий.
						MaxProgress += Part["series"]

					else:
						# Инкремент.
						MaxProgress += 1

			# Для каждой части.
			for Part in self.parts:

				# Если часть не анонсирована и не пропущена.
				if "announced" not in Part.keys() and "skipped" not in Part.keys():

					# Если часть просмотрена и есть серии.
					if "watched" in Part.keys() and "series" in Part.keys() and Part["series"] != None:
						# Подсчёт серий.
						CurrentProgress += Part["series"] if "mark" not in Part.keys() else Part["mark"]

					elif "watched" in Part.keys():
						# Инкремент.
						CurrentProgress += 1

			# Подсчёт прогресса.
			Progress = round(float(CurrentProgress / MaxProgress * 100), 1)
			# Если можно округлить до целого числа, выполнить округление.
			if str(Progress).endswith(".0"): Progress = int(Progress)

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
			"series": None
		}

		# Типы: фильм.
		if part_type in ["film", "special"]: return {
			"type": part_type,
			"name": None
		}

		# Типы: ONA, OVA, специальные выпуски.
		if part_type in ["ONA", "OVA", "specials"]: return {
			"type": part_type,
			"series": None
		}

	def __ModifyPart(self, part: dict, data: dict) -> dict:
		"""
		Подставляет типовые значения в часть.
			part – словарное представление части;
			data – словарь данных для подстановки в часть.
		"""
		
		# Для каждого свойства части из переданных данных.
		for Key in data.keys():

			# Если свойство части нужно удалить и такое свойство есть.
			if data[Key] == "*" and Key in part.keys():
				# Удаление свойства.
				del part[Key]

			# Если передано новое значение свойства.
			elif data[Key] != "*":
				# Обновление свойства.
				part[Key] = data[Key]

			#---> Обработка частных случаев.
			#==========================================================================================#

			# Если часть просмотрена и имеет закладку, удалить закладку.
			if "watched" in part.keys() and "mark" in part.keys(): del part["mark"]
			# Если пропущена и имеет закладку, удалить закладку.
			if "skipped" in part.keys() and "mark" in part.keys(): del part["mark"]

		return part

	def __UpdateStatus(self):
		"""Обновляет статус просмотра."""

		# Если не заброшено.
		if self.__Data["status"] != "dropped":
			# Получение прогресса.
			Progress = self.progress
			# Обработка статусов.
			if Progress == None: self.__Data["status"] = None
			elif Progress == 100: self.__Data["status"] = "completed"
			else: self.__Data["status"] = "watching"

		# Если просмотр завершён.
		if self.__Data["status"] == "completed":

			# Для каждой части.
			for Part in self.__Data["parts"]:

				# Если часть является анонсированной.
				if "announced" in Part.keys():
					# Изменение статуса записи.
					self.__Data["status"] = "announced"
					# Остановка цикла.
					break

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "AnimeTable", note_id: int):
		"""
		Запись просмотра медиаконтента.
			table – объектное представление таблицы;
			note_id – идентификатор записи.
		"""
		
		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		# ID записи.
		self.__ID = note_id
		# Объектное представление таблицы.
		self.__Table = table
		# Данные записи.
		self.__Data = ReadJSON(f"{table.directory}/{table.name}/{self.__ID}.json")
		# Обработчик CLI записи.
		self.__NoteCLI = AnimeNoteCLI(table, self)
	
	def add_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Добавляет альтернативное название.
			another_name – альтернативное название.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если такое альтренативное название ещё не задано.
			if another_name not in self.__Data["another_names"]:
				# Добавление алтернативного названия.
				self.__Data["another_names"].append(another_name)
				# Сохранение изменений.
				self.save()
				# Установка сообщения.
				Status.message = "Another name added."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = "Part created."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
				# Установка сообщения.
				Status.message = "Tag added."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
				self.__Data["another_names"].pop(int(another_name))

			else:
				# Удаление альтернативного названия по значению.
				self.__Data["another_names"].remove(another_name)

			# Сохранение изменений.
			self.save()
			# Установка сообщения.
			Status.message = "Another name removed."

		except IndexError:
			# Изменение статуса.
			Status = ExecutionError(1, "incorrect_another_name_index")

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = "Metainfo updated."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = "Part deleted."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщение.
			Status.message = "Tag removed."

		except IndexError:
			# Изменение статуса.
			Status = ExecutionStatus(1, "incorrect_tag_index")

		except IndexError:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
				# Перемещение части вниз.
				self.__Data["parts"].insert(part_index + 1, self.__Data["parts"].pop(part_index))
				# Сохранение изменений.
				self.save()
				# Установка сообщения.
				Status.message = "Part downed."

			# Если последняя часть.
			elif part_index == len(self.__Data["parts"]) - 1:
				# Изменение статуса.
				Status = ExecutionWarning(1, "unable_down_last_part")

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = "Part edited."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			if estimation <= self.__Table.options["max_estimation"]:
				# Выставление оценки.
				self.__Data["estimation"] = estimation
				# Сохранение изменений.
				self.save()
				# Установка сообщение.
				Status.message = "Estimation updated."

			else:
				# Изменение статуса.
				Status = ExecutionError(1, "max_estimation_exceeded")

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = "Name updated."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = f"Note has been added to @{group_id} group."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
				if "watched" in self.__Data["parts"][part_index].keys():
					# Снятие статуса полностью просмотренного и установка закладки.
					del self.__Data["parts"][part_index]["watched"]
					self.__Data["parts"][part_index]["mark"] = mark
					# Обновление статуса просмотра.
					self.__UpdateStatus()
					# Сохранение изменений.
					self.save()
					# Установка сообщения.
					Status.message = "Part marked as unseen."

				# Если закладка установлена на пропущенную часть.
				elif "skipped" in self.__Data["parts"][part_index].keys():
					# Снятие статуса пропуска и установка закладки.
					del self.__Data["parts"][part_index]["skipped"]
					self.__Data["parts"][part_index]["mark"] = mark
					# Обновление статуса просмотра.
					self.__UpdateStatus()
					# Сохранение изменений.
					self.save()
					# Установка сообщения.
					Status.message = "Part marked as unskipped."

				else:

					# Если закладка лежит в диапазоне серий.
					if mark < self.__Data["parts"][part_index]["series"] and mark != 0:
						# Обновление закладки.
						self.__Data["parts"][part_index]["mark"] = mark
						# Установка сообщения.
						Status.message = "Mark updated."

					# Если закладка на последней серии.
					elif mark == self.__Data["parts"][part_index]["series"]:
						# Добавление статуса полностью просмотренного и удаление закладки.
						self.__Data["parts"][part_index]["watched"] = True
						if "mark" in self.__Data["parts"][part_index].keys(): del self.__Data["parts"][part_index]["mark"]
						# Установка сообщения.
						Status.message = "Part marked as fully viewed."

					# Если закладка на нулевой серии.
					elif mark == 0:
						# Удаление закладки.
						del self.__Data["parts"][part_index]["mark"]
						# Изменение статуса.
						Status.message = "Mark removed."

					# Сохранение изменений.
					self.save()
					# Обновление статуса просмотра.
					self.__UpdateStatus()

			else:
				# Изменение статуса.
				Status = ExecutionError(-2, "only_series_supports_marks")

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = "Metainfo updated."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			"a": "announced",
			"w": "watching",
			"c": "completed",
			"d": "dropped",
			"p": "planned",
			"*": None
		}

		try:
			# Если указан сокращённый статус, преобразовать его в полный.
			if status in Statuses.keys(): status = Statuses[status]
			# Установка статуса.
			self.__Data["status"] = status
			# Сохранение изменений.
			self.save()
			# Установка сообщения.
			Status.message = "Status updated."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
				# Установка сообщения.
				Status.message = "Part upped."

			# Если первая часть.
			elif part_index == 0:
				# Изменение статуса.
				Status = ExecutionWarning(1, "unable_up_first_part")

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

		return Status

class AnimeTable:
	"""Таблица просмотров медиакнотента."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	# Тип таблицы.
	type = "anime"

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> AnimeTableCLI:
		"""Обработчик CLI таблицы."""

		return self.__TableCLI

	@property
	def directory(self) -> str:
		"""Путь к каталогу таблицы."""

		return self.__StorageDirectory

	@property
	def id(self) -> list[AnimeNote]:
		"""Идентификатор таблицы."""

		return self.__Notes.values()

	@property
	def max_estimation(self) -> int:
		"""Максимальная допустимая оценка."""

		return self.__Options["max_estimation"]

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self.__Name

	@property
	def notes(self) -> list[AnimeNote]:
		"""Список записей."""

		return self.__Notes.values()

	@property
	def options(self) -> dict:
		"""Словарь опций таблицы."""

		return self.__Options.copy()	

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
		if self.__Options["recycle_id"]:
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
		self.__Notes[note_id] = AnimeNote(self, note_id)

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
		
		#---> Генерация динамичкских атрибутов.
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
		self.__Type = "anime"
		# Опции таблицы.
		self.__Options = {
			"version": 1,
			"type": self.__Type,
			"recycle_id": False,
			"max_estimation": 10,
			"viewer": {
				"links": True,
				"comments": True,
				"colorize": True,
				"hide_single_series": True
			}
		}
		# Обработчик CLI таблицы.
		self.__TableCLI = AnimeTableCLI(self)

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
			# Установка сообщения.
			Status.message = f"Group @{ID} created."


		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

		return Status

	def create_note(self) -> ExecutionStatus:
		"""Создаёт запись."""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# ID новой записи.
			ID = self.__GetNewID(self.__Notes)
			# Сохранение локального файла JSON.
			WriteJSON(f"{self.__StorageDirectory}/{self.__Name}/{ID}.json", AnimeNote.BASE_NOTE)
			# Чтение и объектная интерпретация записи.
			self.__ReadNote(ID)
			# Установка сообщения.
			Status = f"Note #{ID} created."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = "Table renamed."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = f"Group @{group_id} removed."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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
			# Установка сообщения.
			Status.message = "Note removed."

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unknown_error")

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

	def get_group_notes(self, group_id: int) -> list[AnimeNote]:
		"""
		Возвращает словарное представление группы.
			group_id – идентификатор группы.
		"""

		# Список записей.
		NotesList = list()
		
		# Для каждой записи.
		for Note in self.notes:
			# Если запись включена в указанную группу, добавить её в список.
			if Note.group == group_id: NotesList.append(Note)

		return NotesList

	def get_note(self, note_id: int) -> ExecutionStatus:
		"""
		Возвращает объектное представление записи.
			note_id – идентификатор записи.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Приведение ID к целочисленному типу.
			note_id = int(note_id)
			# Осуществление доступа к записи.
			Status.value = self.__Notes[note_id]

		except:
			# Изменение статуса.
			Status = ExecutionError(-1, "unkonwn_error")

		return Status