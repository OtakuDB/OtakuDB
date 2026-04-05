from Source.Core.Base.Structs import Interfaces, SupportedInterfaces
from Source.Core.Base import Note, Manifest, Module
from Source.Core.Bus import ExecutionStatus
from Source.Core.Messages import Errors
from Source.Core.Exceptions import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.TextStyler import Codes, FastStyler, TextStyler
from dublib.CLI.Templates import Confirmation

from Source.Interfaces.CLI.Base import *

from os import PathLike

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class Otaku_Anime_NoteCLI(NoteCLI):
	"""CLI записи."""

	#==========================================================================================#
	# >>>>> ЗАЩИЩЁННЫЕ ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		Com = Command("altname", "Manage alternative names.")
		ComPos = Com.create_position("ALTNAME", "Alternative name.", important = True)
		ComPos.add_argument()
		Com.base.add_flag("d", "Remove another name.")
		CommandsList.append(Com)

		Com = Command("base", "[METAINFO] Set anime base.")
		ComPos = Com.create_position("BASE", "Anime base.", important = True)
		ComPos.add_argument(ParametersTypes.Alpha, "Type of anime base: game, manga, novel, original, ranobe.")
		CommandsList.append(Com)

		Com = Command("delpart", "Remove part.")
		ComPos = Com.create_position("INDEX", "Part index.", important = True)
		ComPos.add_argument(ParametersTypes.Number)
		CommandsList.append(Com)

		Com = Command("downpart", "Down part in list.")
		ComPos = Com.create_position("INDEX", "Part index.", important = True)
		ComPos.add_argument(ParametersTypes.Number)
		CommandsList.append(Com)

		Com = Command("editpart", "Edit part. Put * to keys for data removing.")
		Com.base.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		Com.base.add_flag("a", description = "Mark part as announced.")
		Com.base.add_flag("s", description = "Mark part as skipped.")
		Com.base.add_flag("u", description = "Mark part as unwatched.")
		Com.base.add_flag("w", description = "Mark part as watched.")
		Com.base.add_key("comment", description = "Add comment to part.")
		Com.base.add_key("link", ParametersTypes.URL, description = "Attach link to part.")
		Com.base.add_key("name", description = "Set name of part.")
		Com.base.add_key("number", description = "Set number of part (not index).")
		Com.base.add_key("series", ParametersTypes.Number, description = "Set series count.")
		CommandsList.append(Com)

		Com = Command("estimate", "Set estimation.")
		ComPos = Com.create_position("ESTIMATION", "Estimation value.", important = True)
		ComPos.add_argument(ParametersTypes.Number)
		CommandsList.append(Com)

		Com = Command("mark", "Set bookmark to series.")
		ComPos = Com.create_position("INDEX", "Part index.", important = True)
		ComPos.add_argument(ParametersTypes.Number)
		ComPos = Com.create_position("MARK", "Last watched episode number.", important = True)
		ComPos.add_argument(ParametersTypes.Number)
		CommandsList.append(Com)

		Com = Command("newpart", "Create new part.")
		Com.base.add_argument(description = "Part type.", important = True)
		Com.base.add_flag("a", description = "Mark part as announced.")
		Com.base.add_flag("s", description = "Mark part as skipped.")
		Com.base.add_flag("u", description = "Mark part as unwatched.")
		Com.base.add_flag("w", description = "Mark part as watched.")
		Com.base.add_key("comment", description = "Add comment to part.")
		Com.base.add_key("link", ParametersTypes.URL, description = "Attach link to part.")
		Com.base.add_key("name", description = "Set name of part.")
		Com.base.add_key("number", description = "Set number of part (not index).")
		Com.base.add_key("series", ParametersTypes.Number, description = "Set series count.")
		CommandsList.append(Com)

		Com = Command("status", "Set viewing status.")
		ComPos = Com.create_position("STATUS", "Status name or code: announced (a), watching (w), completed (c), dropped (d), planned (p) or * to remove.", important = True)
		ComPos.add_argument(ParametersTypes.Alpha)
		CommandsList.append(Com)

		Com = Command("tag", "Manage tags.")
		ComPos = Com.create_position("TAG", "Tag name.", important = True)
		ComPos.add_argument()
		Com.base.add_flag("d", "Remove tag.")
		CommandsList.append(Com)
		
		Com = Command("uppart", "Raise part in list.")
		ComPos = Com.create_position("INDEX", "Part index.", important = True)
		ComPos.add_argument(ParametersTypes.Number)
		CommandsList.append(Com)

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()
		self._Note: "Otaku_Anime_Note"

		if parsed_command.name == "altname":
			AnotherName = parsed_command.arguments[0]
			if parsed_command.check_flag("d"): Status = self._Note.remove_another_name(AnotherName)
			else: Status = self._Note.add_another_name(AnotherName)

		elif parsed_command.name == "base":
			Value = parsed_command.arguments[0]
			if Value == "*": Status = self._Note.remove_metainfo("base")
			else: Status = self._Note.set_metainfo("base", Value)

		elif parsed_command.name == "estimate":
			Status = self._Note.estimate(parsed_command.arguments[0])

		elif parsed_command.name == "delpart":
			Response = Confirmation("Are you sure to remove part?")
			
			if Response:
				Status = self._Note.remove_part(parsed_command.arguments[0])

		elif parsed_command.name == "downpart":
			Status = self._Note.down_part(parsed_command.arguments[0])

		elif parsed_command.name == "editpart":
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
			Status = self._Note.edit_part(parsed_command.arguments[0], Data)

		elif parsed_command.name == "mark":
			Status = self._Note.set_mark(parsed_command.arguments[0], parsed_command.arguments[1])

		elif parsed_command.name == "newpart":
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

		elif parsed_command.name == "status":
			Status = self._Note.set_status(parsed_command.arguments[0])

		elif parsed_command.name == "tag":
			Tag = parsed_command.arguments[0]
			if parsed_command.check_flag("d"): Status = self._Note.remove_tag(Tag)
			else: Status = self._Note.add_tag(Tag)

		elif parsed_command.name == "uppart":
			Status = self._Note.up_part(parsed_command.arguments[0])

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def view(self) -> ExecutionStatus:
		"""Выводит форматированные данные записи."""

		Status = ExecutionStatus()

		try:
			#---> Получение данных.
			#==========================================================================================#
			self._Note: "Otaku_Anime_Note"
			self._Table: "Otaku_Anime"
			Parts = self._Note.parts
			Options = self._Table.manifest.interfaces_options.cli

			#---> Объявление литералов.
			#==========================================================================================#
			MSG_TotalProgress = f" ({self._Note.progress}% viewed)" if self._Note.progress else ""

			#---> Вывод описания записи.
			#==========================================================================================#
			if self._Note.name: print(FastStyler(self._Note.name).decorate.bold, end = "")
			print(f"{MSG_TotalProgress} {self._Note.emoji_status}")
			if self._Note.estimation: print(f"⭐ {self._Note.estimation} / {self._Table.max_estimation}")
			if self._Note.another_names: print(FastStyler(f"ANOTHER NAMES: ").decorate.bold)
			for AnotherName in self._Note.another_names: print(FastStyler(f"    {AnotherName}").decorate.italic)

			#---> Вывод классификаторов записи.
			#==========================================================================================#

			if self._Note.tags:
				print(FastStyler(f"TAGS: ").decorate.bold, end = "")
				print(", ".join(self._Note.tags))

			#---> Вывод частей записи.
			#==========================================================================================#

			if Parts:
				print(FastStyler(f"PARTS:").decorate.bold)

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
					if Options.colorize and "✅" in MSG_PartStatus: TextColor = Codes.Colors.Green
					if Options.colorize and "ℹ️" in MSG_PartStatus: TextColor = Codes.Colors.Cyan
					if Options.colorize and "🚫" in MSG_PartStatus: TextColor = Codes.Colors.Blue

					if "series" in Parts[PartIndex].keys():

						#---> Объявление литералов.
						#==========================================================================================#
						MSG_Mark = str(Parts[PartIndex]["mark"]) + " / " if "mark" in Parts[PartIndex] else ""
						MSG_MarkIndicator = " ⏳" if MSG_Mark else ""
						MSG_Progress = " (" + str(int(Parts[PartIndex]["mark"] / Parts[PartIndex]["series"] * 100)) + "% viewed)" if MSG_Mark else ""
						MSG_Series = Parts[PartIndex]["series"]

						#---> Определение цвета части.
						#==========================================================================================#
						if Options.colorize and "⏳" in MSG_MarkIndicator: TextColor = Codes.Colors.Yellow

						#---> Вывод части.
						#==========================================================================================#
						print(TextStyler(text_color = TextColor).get_styled_text(f"    {PartIndex} ▸ {MSG_Type}{MSG_Number}:{MSG_Name}{MSG_PartStatus}{MSG_MarkIndicator}"))
						if not self._Table.manifest.custom["hide_single_series"] or self._Table.manifest.custom["hide_single_series"] and MSG_Series and MSG_Series > 1: print(TextStyler(text_color = TextColor).get_styled_text(f"    {MSG_Indent}       {MSG_Mark}{MSG_Series} series{MSG_Progress}"))

					else:
						print(TextStyler(text_color = TextColor).get_styled_text(f"    {PartIndex} ▸ {MSG_Type}{MSG_Number}:{MSG_Name}{MSG_PartStatus}"))

					if self._Table.manifest.custom["links"] and "link" in Parts[PartIndex].keys():
						print(f"    {MSG_Indent}       🔗 " + Parts[PartIndex]["link"])

					if self._Table.manifest.custom["comments"] and "comment" in Parts[PartIndex].keys():
						print(f"    {MSG_Indent}       💭 " + FastStyler(Parts[PartIndex]["comment"]).colorize.gray)
		
		except: Status.push_error(Errors.UNKNOWN)

		return Status
	
class Otaku_Anime_ModuleCLI(ModuleCLI):
	"""CLI таблицы."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _BuildNoteRow(self, note: "Otaku_Anime_Note") -> dict[str, str]:
		"""
		Строит строку описания записи для таблицы и возвращает словарь в формате: название колонки – данные.
			note – обрабатываемая запись.
		"""

		Row = dict()
		NoteStatus = note.status
		if NoteStatus == "announced": NoteStatus = FastStyler(NoteStatus).colorize.magenta
		if NoteStatus == "planned": NoteStatus = FastStyler(NoteStatus).colorize.cyan
		if NoteStatus == "watching": NoteStatus = FastStyler(NoteStatus).colorize.yellow
		if NoteStatus == "completed": NoteStatus = FastStyler(NoteStatus).colorize.green
		if NoteStatus == "dropped": NoteStatus = FastStyler(NoteStatus).colorize.red
		Row["ID"] = note.id
		Row["Status"] = NoteStatus
		Row["Name"] = note.name
		Row["Estimation"] = note.estimation
		Row["Base"] = FastStyler(note.metainfo["base"]).decorate.italic if "base" in note.metainfo.keys() else None

		return Row
	
#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class Otaku_Anime_Note(Note):
	"""Запись о просмотре аниме."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	BASE_NOTE = {
		"name": None,
		"another_names": [],
		"estimation": None,
		"status": None,
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

					if "series" in Part.keys() and Part["series"]:
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
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._CLI = Otaku_Anime_NoteCLI

	def _SpecifyInterfaces(self) -> SupportedInterfaces:
		"""
		Определяет объекты с реализацией интерфейсов.

		:return: Контейнер поддерживаемых интерфейсов.
		:rtype: SupportedInterfaces
		"""

		self._Interfaces[Interfaces.CLI] = Otaku_Anime_NoteCLI

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Добавляет альтернативное название.
			another_name – альтернативное название.
		"""

		Status = ExecutionStatus()

		try:
			if another_name not in self._Data["another_names"]:
				self._Data["another_names"].append(another_name)
				self.save()
				Status.push_message("Another name added.")

		except:	Status.push_error(Errors.UNKNOWN)

		return Status

	def add_part(self, part_type: str, data: dict) -> ExecutionStatus:
		"""
		Добавляет новую часть.
			part_type – тип части;\n
			data – данные для заполнения свойств части.
		"""

		Status = ExecutionStatus()

		try:
			Buffer = self.__GetBasePart(part_type)
			Buffer = self.__ModifyPart(Buffer, data)
			self._Data["parts"].append(Buffer)
			self.__UpdateStatus()
			self.save()
			Status.push_message("Part created.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def add_tag(self, tag: str) -> ExecutionStatus:
		"""
		Добавляет тег.
			tag – название тега.
		"""

		Status = ExecutionStatus()

		try:
			if tag not in self._Data["tags"]:
				self._Data["tags"].append(tag)
				self.save()
				Status.push_message("Tag added.")

			else: Status.push_message("Tag already exists.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def remove_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Удаляет альтернативное название.
			another_name – альтернативное название.
		"""

		Status = ExecutionStatus()

		try:
			self._Data["another_names"].remove(another_name)
			self.save()
			Status.push_message("Another name removed.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def remove_part(self, part_index: int) -> ExecutionStatus:
		"""
		Удаляет часть.
			index – индекс части.
		"""

		Status = ExecutionStatus()

		try:
			del self._Data["parts"][part_index]
			self.__UpdateStatus()
			self.save()
			Status.push_message("Part deleted.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def remove_tag(self, tag: str) -> ExecutionStatus:
		"""
		Удаляет тег.
			tag – тег.
		"""

		Status = ExecutionStatus()

		try:
			if tag in self._Data["tags"]:
				self._Data["tags"].remove(tag)
				self.save()
				Status.push_message("Tag removed.")

			else: Status.push_message("Tag not found.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def down_part(self, part_index: int) -> ExecutionStatus:
		"""
		Опускает часть на одну позицию вниз.
			part_index – индекс части.
		"""

		Status = ExecutionStatus()

		try:

			if part_index != len(self._Data["parts"]) - 1:
				self._Data["parts"].insert(part_index + 1, self._Data["parts"].pop(part_index))
				self.save()
				Status.push_message("Part downed.")

			elif part_index == len(self._Data["parts"]) - 1:
				Status.push_warning("Unable down last part.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def edit_part(self, part_index: int, data: dict) -> ExecutionStatus:
		"""
		Редактирует свойства части.
			part_index – индекс части;\n
			data – данные для обновления свойств части.
		"""

		Status = ExecutionStatus()

		try:
			self._Data["parts"][part_index] = self.__ModifyPart(self._Data["parts"][part_index], data)
			self.__UpdateStatus()
			self.save()
			Status.push_message("Part edited.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def estimate(self, estimation: int) -> ExecutionStatus:
		"""
		Выставляет оценку.
			estimation – оценка.
		"""

		Status = ExecutionStatus()

		try:

			if estimation <= self._Table.manifest.custom["max_estimation"]:
				self._Data["estimation"] = estimation
				self.save()
				Status.push_message("Estimation updated.")

			else: Status.push_error("Estimation exceeded.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_mark(self, part_index: int, mark: int) -> ExecutionStatus:
		"""
		Добавляет закладку на серию.
			part_index – индекс части;\n
			mark – номер серии для постановки закладки (0 для удаления закладки, номер последней серии для пометки всей части как просмотренной).
		"""

		Status = ExecutionStatus()

		if not self._Data["parts"][part_index]["series"]:
			Status.push_error("Marking available only after series count specification.")
			return Status

		try:

			if "series" in self._Data["parts"][part_index].keys():

				if "watched" in self._Data["parts"][part_index].keys():
					del self._Data["parts"][part_index]["watched"]
					self._Data["parts"][part_index]["mark"] = mark
					self.__UpdateStatus()
					self.save()
					Status.push_message("Part marked as unseen.")

				elif "skipped" in self._Data["parts"][part_index].keys():
					del self._Data["parts"][part_index]["skipped"]
					self._Data["parts"][part_index]["mark"] = mark
					self.__UpdateStatus()
					self.save()
					Status.push_message("Part marked as unskipped.")

				else:

					if mark < self._Data["parts"][part_index]["series"] and mark != 0:
						self._Data["parts"][part_index]["mark"] = mark
						Status.push_message("Mark updated.")

					elif mark == self._Data["parts"][part_index]["series"]:
						self._Data["parts"][part_index]["watched"] = True
						if "mark" in self._Data["parts"][part_index].keys(): del self._Data["parts"][part_index]["mark"]
						Status.push_message("Part marked as fully viewed.")

					elif mark == 0 and "mark" in self._Data["parts"][part_index].keys():
						del self._Data["parts"][part_index]["mark"]
						Status.push_message("Mark removed.")

					self.save()
					self.__UpdateStatus()

			else: Status.push_error("Only series supports mark.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус.
			status – статус просмотра.
		"""

		Status = ExecutionStatus()
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
			if status: Status.push_message("Status updated.")
			else: Status.push_message("Status removed.")
			
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def up_part(self, part_index: int) -> ExecutionStatus:
		"""
		Поднимает часть на одну позицию вверх.
			part_index – индекс части.
		"""

		Status = ExecutionStatus()

		try:

			if part_index != 0:
				self._Data["parts"].insert(part_index - 1, self._Data["parts"].pop(part_index))
				self.save()
				Status.push_message("Part upped.")

			elif part_index == 0:
				Status.push_error("Unable up first part.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

class Otaku_Anime(Module):
	"""Таблица просмотров аниме."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "otaku:anime"

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def max_estimation(self) -> int:
		"""Максимальная допустимая оценка."""

		return self._Manifest.custom["max_estimation"]

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GetEmptyManifest(self, path: PathLike) -> Manifest:
		"""
		Возвращает пустой манифест. Переопределите для настройки.

		:param path: Путь к каталогу таблицы.
		:type path: PathLike
		:return: Пустой манифест.
		:rtype: Manifest
		"""

		Buffer = super()._GetEmptyManifest(path)
		Buffer.set_type(self.TYPE)
		Buffer.metainfo_rules.set_rule("base", ("game", "manga", "novel", "original", "ranobe"))
		Buffer.viewer.columns.set_columns(
			(
				"ID",
				"Status",
				"Name",
				"Base",
				"Estimation"
			)
		)
		Buffer.custom["max_estimation"] = 10
		Buffer.custom["hide_single_series"] = True

		return Buffer

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = Otaku_Anime_Note

	def _SpecifyInterfaces(self) -> SupportedInterfaces:
		"""
		Определяет объекты с реализацией интерфейсов.

		:return: Контейнер поддерживаемых интерфейсов.
		:rtype: SupportedInterfaces
		"""

		self._Interfaces[Interfaces.CLI] = Otaku_Anime_ModuleCLI