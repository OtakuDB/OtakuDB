from Source.Core.Base import Note, NoteCLI, Table, TableCLI 
from Source.CLI.Templates import Columns
from Source.Core.Exceptions import *
from Source.Core.Errors import *

from dublib.CLI.StyledPrinter import Styles, StylesGroup, StyledPrinter, TextStyler
from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.Engine.Bus import ExecutionError, ExecutionWarning, ExecutionStatus
from dublib.CLI.Templates import Confirmation

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class Anime_NoteCLI(NoteCLI):
	"""CLI записи."""

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		Com = Command("delpart", "Remove part.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		CommandsList.append(Com)

		Com = Command("downpart", "Omit part in list.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		CommandsList.append(Com)

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

		Com = Command("estimate", "Set estimation.")
		Com.add_argument(ParametersTypes.Number, description = "Estimation.", important = True)
		CommandsList.append(Com)

		Com = Command("mark", "Set bookmark to series.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		Com.add_argument(ParametersTypes.Number, description = "Bookmark.", important = True)
		CommandsList.append(Com)

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

		Com = Command("set", "Set note values.")
		Com.add_key("altname", description = "Alternative name.")
		Com.add_key("status", description = "View status.")
		Com.add_key("tag", description = "Tag.")
		CommandsList.append(Com)

		Com = Command("unset", "Remove alternative names or tags.")
		ComPos = Com.create_position("TARGET", "Target to remove.", important = True)
		ComPos.add_key("altname", ParametersTypes.All, "Index of alternative name or alternative name.")
		ComPos.add_key("tag", description = "Tag.")
		CommandsList.append(Com)

		Com = Command("uppart", "Raise part.")
		Com.add_argument(ParametersTypes.Number, "Part index.", important = True)
		CommandsList.append(Com)

		Com = Command("view", "View note in console.")
		CommandsList.append(Com)

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		if parsed_command.name == "estimate":
			Status = self._Note.estimate(parsed_command.arguments[0])

		if parsed_command.name == "delpart":
			Response = Confirmation("Are you sure to remove part?")
			
			if Response:
				Status = self._Note.delete_part(int(parsed_command.arguments[0]))

		if parsed_command.name == "downpart":
			Status = self._Note.down_part(int(parsed_command.arguments[0]))

		if parsed_command.name == "editpart":
			Data = dict()
			if "a" in parsed_command.flags: Data["announced"] = True
			if "w" in parsed_command.flags:
				Data["watched"] = True
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if "s" in parsed_command.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = True
			if "u" in parsed_command.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if parsed_command.check_key("link"): Data["link"] = parsed_command.get_key_value("link")
			if parsed_command.check_key("comment"): Data["comment"] = parsed_command.get_key_value("comment")
			if parsed_command.check_key("name"): Data["name"] = parsed_command.get_key_value("name")
			if parsed_command.check_key("number"): Data["number"] = parsed_command.get_key_value("number")
			if parsed_command.check_key("series"): Data["series"] = parsed_command.get_key_value("series")
			Status = self._Note.edit_part(int(parsed_command.arguments[0]), Data)

		if parsed_command.name == "mark":
			Status = self._Note.set_mark(int(parsed_command.arguments[0]), int(parsed_command.arguments[1]))

		if parsed_command.name == "newpart":
			Data = dict()
			if "a" in parsed_command.flags: Data["announced"] = True
			if "w" in parsed_command.flags:
				Data["watched"] = True
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if "s" in parsed_command.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = True
			if "u" in parsed_command.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if "comment" in parsed_command.keys.keys(): Data["comment"] = parsed_command.keys["comment"]
			if "link" in parsed_command.keys.keys(): Data["link"] = parsed_command.keys["link"]
			if "name" in parsed_command.keys.keys(): Data["name"] = parsed_command.keys["name"]
			if "number" in parsed_command.keys.keys(): Data["number"] = parsed_command.keys["number"]
			if "series" in parsed_command.keys.keys(): Data["series"] = parsed_command.keys["series"]
			Status = self._Note.add_part(parsed_command.arguments[0], Data)

		if parsed_command.name == "set":

			if "altname" in parsed_command.keys.keys():
				Status = self._Note.add_another_name(parsed_command.keys["altname"])

			if "status" in parsed_command.keys.keys():
				Status = self._Note.set_status(parsed_command.keys["status"])

			if "tag" in parsed_command.keys.keys():
				Status = self._Note.add_tag(parsed_command.keys["tag"])

		if parsed_command.name == "unset":

			if "altname" in parsed_command.keys.keys():
				Status = self._Note.remove_another_name(parsed_command.keys["altname"])

			if "tag" in parsed_command.keys.keys():
				Status = self._Note.remove_tag(parsed_command.keys["tag"])

		if parsed_command.name == "uppart":
			Status = self._Note.up_part(int(parsed_command.arguments[0]))

		if parsed_command.name == "view":
			self.__View()

		return Status

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __View(self):
		"""Выводит форматированные данные записи."""

		#---> Получение данных.
		#==========================================================================================#
		Parts = self._Note.parts
		Options = self._Table.manifest.viewer

		#---> Объявление литералов.
		#==========================================================================================#
		MSG_TotalProgress = f" ({self._Note.progress}% viewed)" if self._Note.progress else ""

		#---> Вывод описания записи.
		#==========================================================================================#
		if self._Note.name: StyledPrinter(self._Note.name, decorations = [Styles.Decorations.Bold], end = False)
		print(f"{MSG_TotalProgress} {self._Note.emoji_status}")
		if self._Note.estimation: print(f"⭐ {self._Note.estimation} / {self._Table.max_estimation}")
		if self._Note.another_names: StyledPrinter(f"ANOTHER NAMES: ", decorations = [Styles.Decorations.Bold])
		for AnotherName in self._Note.another_names: StyledPrinter(f"    {AnotherName}", decorations = [Styles.Decorations.Italic])

		#---> Вывод классификаторов записи.
		#==========================================================================================#

		if self._Note.metainfo:
			StyledPrinter(f"METAINFO:", decorations = [Styles.Decorations.Bold])
			MetaInfo = self._Note.metainfo
			
			for Key in MetaInfo.keys():
				CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
				print(f"    {CustomMetainfoMarker}{Key}: " + str(MetaInfo[Key]))

		if self._Note.tags:
			StyledPrinter(f"TAGS: ", decorations = [Styles.Decorations.Bold], end = False)
			print(", ".join(self._Note.tags))

		#---> Вывод частей записи.
		#==========================================================================================#

		if Parts:
			StyledPrinter(f"PARTS:", decorations = [Styles.Decorations.Bold])

			for PartIndex in range(0, len(Parts)):

				#---> Объявление литералов.
				#==========================================================================================#
				MSG_PartStatus = ""
				if "watched" in Parts[PartIndex].keys(): MSG_PartStatus = " ✅"
				if "announced" in Parts[PartIndex].keys(): MSG_PartStatus = " ℹ️"
				if "skipped" in Parts[PartIndex].keys(): MSG_PartStatus = " 🚫"
				MSG_Name = " " + Parts[PartIndex]["name"] if "name" in Parts[PartIndex].keys() and Parts[PartIndex]["name"] else ""
				MSG_Number = " " + str(Parts[PartIndex]["number"]) if "number" in Parts[PartIndex].keys() and Parts[PartIndex]["number"] else ""
				MSG_Indent = " " * len(str(PartIndex))
				MSG_Type = Parts[PartIndex]["type"]

				#---> Определение цвета части.
				#==========================================================================================#
				TextColor = None
				if Options["colorize"] and "✅" in MSG_PartStatus: TextColor = StylesGroup(text_color = Styles.Colors.Green)
				if Options["colorize"] and "ℹ️" in MSG_PartStatus: TextColor = StylesGroup(text_color = Styles.Colors.Cyan)
				if Options["colorize"] and "🚫" in MSG_PartStatus: TextColor = StylesGroup(text_color = Styles.Colors.Blue)

				if "series" in Parts[PartIndex].keys():

					#---> Объявление литералов.
					#==========================================================================================#
					MSG_Mark = str(Parts[PartIndex]["mark"]) + " / " if "mark" in Parts[PartIndex] else ""
					MSG_MarkIndicator = " ⏳" if MSG_Mark else ""
					MSG_Progress = " (" + str(int(Parts[PartIndex]["mark"] / Parts[PartIndex]["series"] * 100)) + "% viewed)" if MSG_Mark else ""
					MSG_Series = Parts[PartIndex]["series"]

					#---> Определение цвета части.
					#==========================================================================================#
					if Options["colorize"] and "⏳" in MSG_MarkIndicator: TextColor = StylesGroup(text_color = Styles.Colors.Yellow)

					#---> Вывод части.
					#==========================================================================================#
					StyledPrinter(f"    {PartIndex} ▸ {MSG_Type}{MSG_Number}:{MSG_Name}{MSG_PartStatus}{MSG_MarkIndicator}", styles = TextColor)
					if not Options["hide_single_series"] or Options["hide_single_series"] and MSG_Series and MSG_Series > 1: StyledPrinter(f"    {MSG_Indent}       {MSG_Mark}{MSG_Series} series{MSG_Progress}", styles = TextColor)

				else:
					StyledPrinter(f"    {PartIndex} ▸ {MSG_Type}{MSG_Number}:{MSG_Name}{MSG_PartStatus}", styles = TextColor)

				if Options["links"] and "link" in Parts[PartIndex].keys(): print(f"    {MSG_Indent}       🔗 " + Parts[PartIndex]["link"])
				if Options["comments"] and "comment" in Parts[PartIndex].keys(): print(f"    {MSG_Indent}       💭 " + Parts[PartIndex]["comment"])

class Anime_TableCLI(TableCLI):
	"""CLI таблицы."""

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		Com = Command("list", "Show list of notes.")
		Com.add_flag("r", "Reverse list.")
		Com.add_key("group", ParametersTypes.Number, "Group ID.")
		Com.add_key("sort", ParametersTypes.Text, "Column name.")
		Com.add_key("search", description = "Part of note name.")
		CommandsList.append(Com)

		Com = Command("search", "Search notes by part of name.")
		Com.add_argument(description = "Search query.", important = True)
		CommandsList.append(Com)

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		if parsed_command.name == "list":
			self.__List(parsed_command)

		if parsed_command.name == "search":
			self.__List(parsed_command, parsed_command.arguments[0])

		return Status

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __List(self, parsed_command: ParsedCommandData, search: str | None = None):
			Content = {
				"ID": [],
				"Status": [],
				"Name": [],
				"Estimation": []
			}
			SortBy = parsed_command.keys["sort"].title() if "sort" in parsed_command.keys.keys() else "ID"
			if SortBy == "Id": SortBy = SortBy.upper()
			if SortBy not in Content.keys(): return ExecutionError(-1, "bad_sorting_parameter")
			Reverse = parsed_command.check_flag("r")
			
			if self._Table.notes:
				Notes = self._Table.notes

				if search:
					print("Search:", TextStyler(search, text_color = Styles.Colors.Yellow))
					NotesCopy = list(Notes)
					SearchBuffer = list()

					for Note in NotesCopy:
						Names = list()
						if Note.name: Names.append(Note.name)
						if Note.another_names: Names += Note.another_names

						for Name in Names:
							if search.lower() in Name.lower(): SearchBuffer.append(Note)

					Notes = SearchBuffer
				
				for Note in Notes:
					Name = Note.name if Note.name else ""
					Status = Note.status
					if Status == "announced": Status = TextStyler(Status, text_color = Styles.Colors.Purple)
					if Status == "planned": Status = TextStyler(Status, text_color = Styles.Colors.Cyan)
					if Status == "watching": Status = TextStyler(Status, text_color = Styles.Colors.Yellow)
					if Status == "completed": Status = TextStyler(Status, text_color = Styles.Colors.Green)
					if Status == "dropped": Status = TextStyler(Status, text_color = Styles.Colors.Red)
					Content["ID"].append(Note.id)
					Content["Status"].append(Status if Status else "")
					Content["Name"].append(Name if len(Name) < 60 else Name[:60] + "…")
					Content["Estimation"].append(Note.estimation if Note.estimation else "")

				if len(Notes): Columns(Content, sort_by = SortBy, reverse = Reverse)
				else: print("Notes not found.")

			else:
				print("Table is empty.")
	
#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class Anime_Note(Note):
	"""Запись о просмотре аниме."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

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
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self._Data["another_names"]
	
	@property
	def emoji_status(self) -> str:
		"""Статус просмотра в видзе эмодзи."""

		Statuses = {
			"announced": "ℹ️",
			"watching": "▶️",
			"completed": "✅",
			"dropped": "⛔",
			"planned": "🗓️",
			None: ""
		}

		return Statuses[self._Data["status"]]

	@property
	def estimation(self) -> int | None:
		"""Оценка."""

		return self._Data["estimation"]

	@property
	def metainfo(self) -> dict:
		"""Метаданные."""

		return self._Data["metainfo"]

	@property
	def parts(self) -> list[dict]:
		"""Список частей."""

		return list(self._Data["parts"])

	@property
	def progress(self) -> float:
		"""Прогресс просмотра."""

		Progress = 0
		MaxProgress = 0
		CurrentProgress = 0
		Parts = self.parts

		if Parts:

			for Part in self.parts:

				if "announced" not in Part.keys() and "skipped" not in Part.keys():

					if "series" in Part.keys() and Part["series"] != None:
						MaxProgress += Part["series"]

					else:
						MaxProgress += 1

			for Part in self.parts:

				if "announced" not in Part.keys() and "skipped" not in Part.keys():

					if "watched" in Part.keys() and "series" in Part.keys() and Part["series"] != None:
						CurrentProgress += Part["series"] if "mark" not in Part.keys() else Part["mark"]

					elif "watched" in Part.keys():
						CurrentProgress += 1

			Progress = round(float(CurrentProgress / MaxProgress * 100), 1)
			if str(Progress).endswith(".0"): Progress = int(Progress)

		return Progress

	@property
	def status(self) -> str | None:
		"""Статус просмотра."""

		return self._Data["status"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return list(self._Data["tags"])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetBasePart(self, part_type: str) -> dict:
		"""
		Возвращает стандартную словарную структуру части.
			part_type – тип части.
		"""

		if part_type in ["season"]: return {
			"type": part_type,
			"number": None,
			"series": None
		}

		if part_type in ["film", "special"]: return {
			"type": part_type,
			"name": None
		}

		if part_type in ["ONA", "OVA", "specials"]: return {
			"type": part_type,
			"series": None
		}

	def __ModifyPart(self, part: dict, data: dict) -> dict:
		"""
		Подставляет типовые значения в часть.
			part – словарное представление части;\n
			data – словарь данных для подстановки в часть.
		"""
		
		for Key in data.keys():

			if data[Key] == "*" and Key in part.keys():
				del part[Key]

			elif data[Key] != "*":
				part[Key] = data[Key]

			#---> Обработка частных случаев.
			#==========================================================================================#

			if "watched" in part.keys() and "mark" in part.keys(): del part["mark"]
			if "skipped" in part.keys() and "mark" in part.keys(): del part["mark"]

		return part

	def __UpdateStatus(self):
		"""Обновляет статус просмотра."""

		if self._Data["status"] != "dropped":
			Progress = self.progress
			if Progress == None: self._Data["status"] = None
			elif Progress == 100: self._Data["status"] = "completed"
			else: self._Data["status"] = "watching"

		if self._Data["status"] == "completed":

			for Part in self._Data["parts"]:

				if "announced" in Part.keys():
					self._Data["status"] = "announced"
					break

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._CLI = Anime_NoteCLI

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Добавляет альтернативное название.
			another_name – альтернативное название.
		"""

		Status = ExecutionStatus(0)

		try:

			if another_name not in self._Data["another_names"]:
				self._Data["another_names"].append(another_name)
				self.save()
				Status.message = "Another name added."

		except:	Status = ERROR_UNKNOWN

		return Status

	def add_part(self, part_type: str, data: dict) -> ExecutionStatus:
		"""
		Добавляет новую часть.
			part_type – тип части;\n
			data – данные для заполнения свойств части.
		"""

		Status = ExecutionStatus(0)

		try:
			Buffer = self.__GetBasePart(part_type)
			Buffer = self.__ModifyPart(Buffer, data)
			self._Data["parts"].append(Buffer)
			self.__UpdateStatus()
			self.save()
			Status.message = "Part created."

		except: Status = ERROR_UNKNOWN

		return Status

	def add_tag(self, tag: str) -> ExecutionStatus:
		"""
		Добавляет тег.
			tag – название тега.
		"""

		Status = ExecutionStatus(0)

		try:

			if tag not in self._Data["tags"]:
				self._Data["tags"].append(tag)
				self.save()
				Status.message = "Tag added."

		except: Status = ERROR_UNKNOWN

		return Status

	def remove_another_name(self, another_name: int | str) -> ExecutionStatus:
		"""
		Удаляет альтернативное название.
			another_name – альтернативное название или его индекс.
		"""

		Status = ExecutionStatus(0)

		try:

			if another_name.isdigit() and another_name not in self._Data["another_names"]:
				self._Data["another_names"].pop(int(another_name))

			else:
				self._Data["another_names"].remove(another_name)

			self.save()
			Status.message = "Another name removed."

		except IndexError: Status = ExecutionError(-1, "incorrect_another_name_index")
		except: Status = ERROR_UNKNOWN

		return Status

	def remove_part(self, part_index: int) -> ExecutionStatus:
		"""
		Удаляет часть.
			index – индекс части.
		"""

		Status = ExecutionStatus(0)

		try:
			del self._Data["parts"][part_index]
			self.__UpdateStatus()
			self.save()
			Status.message = "Part deleted."

		except: Status = ERROR_UNKNOWN

		return Status

	def remove_tag(self, tag: int | str) -> ExecutionStatus:
		"""
		Удаляет тег.
			tag – тег или его индекс.
		"""

		Status = ExecutionStatus(0)

		try:
			if tag.isdigit(): self._Data["tags"].pop(int(tag))
			else: self._Data["tags"].remove(tag)
			self.save()
			Status.message = "Tag removed."

		except IndexError: Status = ExecutionStatus(-1, "incorrect_tag_index")

		return Status

	def down_part(self, part_index: int) -> ExecutionStatus:
		"""
		Опускает часть на одну позицию вниз.
			part_index – индекс части.
		"""

		Status = ExecutionStatus(0)

		try:

			if part_index != len(self._Data["parts"]) - 1:
				self._Data["parts"].insert(part_index + 1, self._Data["parts"].pop(part_index))
				self.save()
				Status.message = "Part downed."

			elif part_index == len(self._Data["parts"]) - 1:
				Status = ExecutionWarning(1, "unable_down_last_part")

		except: Status = ERROR_UNKNOWN

		return Status

	def edit_part(self, part_index: int, data: dict) -> ExecutionStatus:
		"""
		Редактирует свойства части.
			part_index – индекс части;\n
			data – данные для обновления свойств части.
		"""

		Status = ExecutionStatus(0)

		try:
			self._Data["parts"][part_index] = self.__ModifyPart(self._Data["parts"][part_index], data)
			self.__UpdateStatus()
			self.save()
			Status.message = "Part edited."

		except: Status = ERROR_UNKNOWN

		return Status

	def estimate(self, estimation: int) -> ExecutionStatus:
		"""
		Выставляет оценку.
			estimation – оценка.
		"""

		Status = ExecutionStatus(0)

		try:

			if estimation <= self._Table.manifest.custom["max_estimation"]:
				self._Data["estimation"] = estimation
				self.save()
				Status.message = "Estimation updated."

			else: Status = ExecutionError(-1, "max_estimation_exceeded")

		except: Status = ERROR_UNKNOWN

		return Status

	def set_mark(self, part_index: int, mark: int) -> ExecutionStatus:
		"""
		Добавляет закладку на серию.
			part_index – индекс части;\n
			mark – номер серии для постановки закладки (0 для удаления закладки, номер последней серии для пометки всей части как просмотренной).
		"""

		Status = ExecutionStatus(0)

		try:

			if "series" in self._Data["parts"][part_index].keys():

				if "watched" in self._Data["parts"][part_index].keys():
					del self._Data["parts"][part_index]["watched"]
					self._Data["parts"][part_index]["mark"] = mark
					self.__UpdateStatus()
					self.save()
					Status.message = "Part marked as unseen."

				elif "skipped" in self._Data["parts"][part_index].keys():
					del self._Data["parts"][part_index]["skipped"]
					self._Data["parts"][part_index]["mark"] = mark
					self.__UpdateStatus()
					self.save()
					Status.message = "Part marked as unskipped."

				else:

					if mark < self._Data["parts"][part_index]["series"] and mark != 0:
						self._Data["parts"][part_index]["mark"] = mark
						Status.message = "Mark updated."

					elif mark == self._Data["parts"][part_index]["series"]:
						self._Data["parts"][part_index]["watched"] = True
						if "mark" in self._Data["parts"][part_index].keys(): del self._Data["parts"][part_index]["mark"]
						Status.message = "Part marked as fully viewed."

					elif mark == 0:
						del self._Data["parts"][part_index]["mark"]
						Status.message = "Mark removed."

					self.save()
					self.__UpdateStatus()

			else: Status = ExecutionError(-1, "only_series_supports_marks")

		except: Status = ERROR_UNKNOWN

		return Status

	def set_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус.
			status – статус просмотра.
		"""

		Status = ExecutionStatus(0)
		Statuses = {
			"a": "announced",
			"w": "watching",
			"c": "completed",
			"d": "dropped",
			"p": "planned",
			"*": None
		}

		try:
			if status in Statuses.keys(): status = Statuses[status]
			self._Data["status"] = status
			self.save()
			Status.message = "Status updated."

		except: Status = ERROR_UNKNOWN

		return Status

	def up_part(self, part_index: int) -> ExecutionStatus:
		"""
		Поднимает часть на одну позицию вверх.
			part_index – индекс части.
		"""

		Status = ExecutionStatus(0)

		try:

			if part_index != 0:
				self._Data["parts"].insert(part_index - 1, self._Data["parts"].pop(part_index))
				self.save()
				Status.message = "Part upped."

			elif part_index == 0:
				Status = ExecutionWarning(1, "unable_up_first_part")

		except: Status = ERROR_UNKNOWN

		return Status

class Anime(Table):
	"""Таблица просмотров аниме."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "anime"
	MANIFEST: dict = {
		"object": "table",
		"type": TYPE,
		"modules": [],
		"common": {
			"recycle_id": True
		},
		"metainfo_rules": {
			"base": ["game", "manga", "novel", "original", "ranobe"]
		},
		"viewer": {
			"links": True,
			"comments": True,
			"colorize": True,
			"hide_single_series": True
		},
		"custom": {
			"max_estimation": 10
		}
	}

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def max_estimation(self) -> int:
		"""Максимальная допустимая оценка."""

		return self._Manifest.custom["max_estimation"]

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = Anime_Note
		self._CLI = Anime_TableCLI