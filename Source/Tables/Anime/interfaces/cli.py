from ..note.Enums import Bases, PartStatuses, PartsTypes, Statuses

from Source.Interfaces.CLI.Base import BaseTableCLI, BaseNoteCLI
from Source.Interfaces.CLI.Functions import Unstar
from Source.Core import Exceptions

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.TextStyler import Codes, FastStyler, TextStyler
from dublib.CLI.Templates.Bus import PrintError
from dublib.Methods.Data import StringifyFloat
from dublib.CLI.Templates import Confirmation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..note import Note

class TableCLI(BaseTableCLI):
	"""Интерпретатор CLI таблицы."""

	def _ExecuteCustomCommand(self, command: ParsedCommandData):
		"""
		Обрабатывает кастомную команду.
		
		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		pass

	def _GenerateCustomCommands(self) -> list[Command]:
		"""
		Возвращает список кастомных команд интерпретатора.

		:return: Возвращает список кастомных команд интерпретатора.
		:rtype: list[Command]
		"""

		CommandsList = list()

		return CommandsList

	def _GenerateTableRow(self, container: dict[str, None], note: "Note") -> dict[str, str | None]:
		"""
		Генерирует данные для заполнения строки таблицы.

		:param container: Словарь, в котром ключи являются названиями колонок.
		:type container: dict[str, None]
		:param note: Запись.
		:type note: Note
		:return: Словарь с подставленными значениями.
		:rtype: dict[str, str | None]
		"""

		container["ID"] = note.id

		NoteStatus = note.status
		match NoteStatus:
			case Statuses.Announced: NoteStatus = FastStyler(NoteStatus.value).colorize.magenta
			case Statuses.Planned: NoteStatus = FastStyler(NoteStatus.value).colorize.cyan
			case Statuses.Watching: NoteStatus = FastStyler(NoteStatus.value).colorize.yellow
			case Statuses.Completed: NoteStatus = FastStyler(NoteStatus.value).colorize.green
			case Statuses.Dropped: NoteStatus = FastStyler(NoteStatus.value).colorize.red
		container["Status"] = NoteStatus

		container["Name"] = note.name
		container["Base"] = note.metainfo["base"]
		container["Estimation"] = note.estimation

		return container

class NoteCLI(BaseNoteCLI):
	"""Интерпретатор CLI записи."""

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def _altname(self, name: str, remove: bool):
		"""
		Управляет альтернативными названиями.

		:param name: Альтернативное название.
		:type name: str
		:param remove: Переключает режимы добавления/удаления названия.
		:type remove: bool
		"""

		if remove: self._Note.remove_another_name(name)
		else: self._Note.add_another_name(name)

	def _delpart(self, index: int, confirm: bool):
		"""
		Удаляет часть.

		:param index: Индекс части.
		:type index: int
		:param confirm: Отключает подтверждение удаления.
		:type confirm: bool
		"""

		if not confirm and not Confirmation(f"Part with index {index} will be deleted.", "Continue?"): return

		try: self._Note.remove_part(index)
		except IndexError: PrintError(f"Part with index {index} not found.")

	def _editpart(self, command: ParsedCommandData):
		"""
		Редактирует данные части.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		Index = command.get_position_value("INDEX")
		Part = None

		try: Part = self._Note.get_part(Index)
		except IndexError:
			PrintError(f"Part with index {Index} not found.")
			return
		
		if command.check_key("--name"): Part.rename(Unstar(command.get_key_value("--name")))
		if command.check_key("--comment"): Part.set_comment(Unstar(command.get_key_value("--comment")))
		if command.check_key("--number"): Part.set_number(command.get_key_value("--number") or None)

		if command.check_key("--series"):
			Series = command.get_key_value("--series") or None
			try: Part.set_series_count(Series)
			except ValueError as ExceptionData: PrintError(str(ExceptionData))

		StatusFlag = command.get_position_parameter("STATUS")
		if StatusFlag:
			try:
				match StatusFlag.name:
					case "-a": Part.set_viewed(-2)
					case "-s": Part.set_viewed(-1)
					case "-u": Part.set_viewed(0)
					case "-w": Part.set_viewed(Part.series)
			except ValueError as ExceptionData: PrintError(str(ExceptionData))

	def _estimate(self, estimation: int):
		"""
		Задаёт оценку.

		:param estimation: Оценка.
		:type estimation: int
		"""

		try: self._Note.estimate(estimation or None)
		except ValueError as ExceptionData: PrintError(str(ExceptionData))

	def _mark(self, index: int, mark: int):
		"""
		Задаёт прогресс просмотра части.

		:param index: Индекс части.
		:type index: int
		:param mark: Количество просмотренных элементов.
		:type mark: int
		"""

		Part = None

		try: Part = self._Note.get_part(index)
		except IndexError:
			PrintError(f"Part with index {index} not found.")
			return
		
		if Part.type == PartsTypes.Film and mark > 1: mark = 1

		try: Part.set_viewed(mark)
		except ValueError as ExceptionData: PrintError(str(ExceptionData))

	def _move(self, command: ParsedCommandData):
		"""
		Перемещает часть.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		Index = command.get_position_value("INDEX")
		Operation, Count = None, 1

		try: self._Note.get_part(Index)
		except IndexError:
			PrintError(f"Part with index {Index} not found.")
			return
		
		if command.check_flag("-up"): Operation = "up"
		elif command.check_key("--up"): Operation, Count = "up", command.get_key_value("--up")
		elif command.check_flag("-down"): Operation = "down"
		elif command.check_key("--down"): Operation, Count = "down", command.get_key_value("--down")

		try:
			match Operation:
				case "up": self._Note.up_part(Index, Count)
				case "down": self._Note.down_part(Index, Count)

		except ValueError: PrintError("Incorrect operations count.")

	def _newpart(self, type: str):
		"""
		Создаёт новую часть.

		:param type: Тип части.
		:type type: str
		"""

		try: type = PartsTypes(type)
		except:
			PrintError(f"Unsupported type \"{type}\".")
			return
		
		type: PartsTypes
		Index = self._Note.create_part(type)
		print(f"Created {type.value} with index {Index}.")

	def _tag(self, tag: str, remove: bool):
		"""
		Управляет тегами.

		:param tag: Тег.
		:type tag: str
		:param remove: Переключает режимы добавления/удаления тегов.
		:type remove: bool
		"""

		if remove: self._Note.remove_tag(tag)
		else: self._Note.add_tag(tag)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
			
	def _ExecuteCustomCommand(self, command: ParsedCommandData):
		"""
		Обрабатывает кастомную команду.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		match command.name:
			case "altname": self._altname(command.get_position_value("ALT_NAME"), command.check_flag("-r"))
			case "base": self._SetMetainfo("base", command.get_position_value("VALUE"))
			case "delpart": self._delpart(command.get_position_value("INDEX"), command.check_flag("-y"))
			case "drop": self._Note.drop()
			case "editpart": self._editpart(command)
			case "estimate": self._estimate(command.get_position_value("ESTIMATION"))
			case "mark": self._mark(command.get_position_value("INDEX"), command.get_position_value("MARK"))
			case "move": self._move(command)
			case "newpart": self._newpart(command.get_position_value("TYPE"))
			case "ptypes": print(", ".join(Type.value for Type in PartsTypes))
			case "tag": self._tag(command.get_position_value("TAG"), command.check_flag("-r"))

	def _GenerateCustomCommands(self) -> list[Command]:
		"""
		Возвращает список кастомных команд интерпретатора.

		:return: Возвращает список кастомных команд интерпретатора.
		:rtype: list[Command]
		"""

		CommandsList = list()

		Com = Command("altname", "Manage alternative names.")
		ComPos = Com.create_position("ALT_NAME", "Alternative name.", important = True)
		ComPos.set_argument()
		Com.base.add_flag("-r", description = "Remove another name if exists.")
		CommandsList.append(Com)

		Com = Command("base", "Set anime base.", "Metainfo")
		BaesesNames = ", ".join(Element.value for Element in Bases)
		ComPos = Com.create_position("VALUE", description = f"One of values: {BaesesNames}. Put * to clear.", important = True)
		ComPos.set_argument(ParametersTypes.Alpha)
		CommandsList.append(Com)

		Com = Command("delpart", "Delete part.")
		ComPos = Com.create_position("INDEX", "Part index.", important = True)
		ComPos.set_argument(ParametersTypes.Integer)
		Com.base.add_flag("-y", description = "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("drop", "Switch drop status")
		CommandsList.append(Com)

		Com = Command("editpart", "Edit part data.")
		ComPos = Com.create_position("INDEX", "Part index.", important = True)
		ComPos.set_argument(ParametersTypes.Integer)
		ComPos = Com.create_position("STATUS", "Status of viewing.")
		ComPos.add_flag("-a", description = "Mark part as announced.")
		ComPos.add_flag("-s", description = "Mark part as skipped.")
		ComPos.add_flag("-u", description = "Mark part as unwatched.")
		ComPos.add_flag("-w", description = "Mark part as fully watched.")
		Com.base.add_key("--comment", description = "Comment to part. Put * to clear.")
		Com.base.add_key("--name", description = "Name of part. Put * to clear.")
		Com.base.add_key("--number", type = ParametersTypes.Number, description = "Number of part. Not index! Put 0 to clear.")
		Com.base.add_key("--series", type = ParametersTypes.Integer, description = "Series count. Put 0 to clear.")
		CommandsList.append(Com)

		Com = Command("estimate", "Set estimation.")
		MaxEstimation = self._Note.table.manifest.custom["max_estimation"]
		ComPos = Com.create_position("ESTIMATION", f"Estimation from 1 to {MaxEstimation}. Put 0 to clear.", important = True)
		ComPos.set_argument(ParametersTypes.Integer)
		CommandsList.append(Com)

		Com = Command("mark", "Set mark of viewing progress to part.")
		ComPos = Com.create_position("INDEX", "Part index.", important = True)
		ComPos.set_argument(ParametersTypes.Integer)
		ComPos = Com.create_position("MARK", "Last watched episode number.", important = True)
		ComPos.set_argument(ParametersTypes.Integer)
		CommandsList.append(Com)

		Com = Command("move", "Move part.")
		ComPos = Com.create_position("INDEX", "Part index.", important = True)
		ComPos.set_argument(ParametersTypes.Integer)
		ComPos = Com.create_position("OPERATION", "Operation type.", important = True)
		ComPos.add_flag("-up", description = "Up part (index decrease).")
		ComPos.add_key("--up", type = ParametersTypes.Integer, description = "Up part several times (index decrease).")
		ComPos.add_flag("-down", description = "Down part (index increase).")
		ComPos.add_key("--down", type = ParametersTypes.Integer, description = "Down part several times (index increase).")
		CommandsList.append(Com)

		Com = Command("newpart", "Create new part.")
		Types = ", ".join(Type.value for Type in PartsTypes)
		ComPos = Com.create_position("TYPE", f"Type of part: {Types}.", important = True)
		ComPos.set_argument(ParametersTypes.Alpha)
		CommandsList.append(Com)

		Com = Command("ptypes", "Prints list of parts types.")
		CommandsList.append(Com)

		Com = Command("tag", "Manage tags.")
		ComPos = Com.create_position("TAG", "Tag name.", important = True)
		ComPos.set_argument()
		Com.base.add_flag("-r", description = "Remove tag.")
		CommandsList.append(Com)

		return CommandsList

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self._Note: "Note"

	def _ViewNote(self):
		"""Отображает запись."""

		#---> Объявление стилей.
		#==========================================================================================#
		BOLD = TextStyler(decorations = Codes.Decorations.Bold)
		ITALIC = TextStyler(decorations = Codes.Decorations.Italic)
		GRAY = TextStyler(text_color = Codes.Colors.Gray)

		#---> Генерация литералов.
		#==========================================================================================#
		TotalProgress = StringifyFloat(self._Note.progress * 100.0)
		TotalProgress = f" ({TotalProgress}% viewed)"
		StatusEmoji = {
			Statuses.Announced: "ℹ️",
			Statuses.Watching: "▶️",
			Statuses.Completed: "✅",
			Statuses.Dropped: "⛔",
			Statuses.Planned: "🗓️"
		}[self._Note.status]


		#---> Вывод данных записи.
		#==========================================================================================#
		if self._Note.name: print(BOLD.get_styled_text(self._Note.name), end = "")
		print(f"{TotalProgress} {StatusEmoji}")
		if self._Note.estimation: print(f"⭐ {self._Note.estimation} / {self._Note.table.manifest.custom["max_estimation"]}")

		if self._Note.another_names:
			print(BOLD.get_styled_text("ANOTHER NAMES:"))
			for AnotherName in self._Note.another_names: print(ITALIC.get_styled_text(" " * 4 + AnotherName))

		if self._Note.tags:
			print(BOLD.get_styled_text("TAGS: "), end = "")
			print(", ".join(self._Note.tags))

		#---> Вывод данных частей.
		#==========================================================================================#
		Parts = self._Note.parts
		if not Parts: return
		print(BOLD.get_styled_text("PARTS:"))

		for Index in range(len(Parts)):
			Part = Parts[Index]

			#---> Генерация литералов.
			#==========================================================================================#
			PartNumber = f" {Part.number}" if Part.number else ""
			PartName = f" {Part.name}" if Part.name else ""

			PartStatusEmoji = {
				PartStatuses.Announced: " ℹ️",
				PartStatuses.Skipped: " 🚫",
				PartStatuses.Unwatched: "",
				PartStatuses.Watching: " ▶️",
				PartStatuses.Watched: " ✅"
			}[Part.status]
			PartColor = {
				PartStatuses.Announced: Codes.Colors.Cyan,
				PartStatuses.Skipped: Codes.Colors.Blue,
				PartStatuses.Unwatched: None,
				PartStatuses.Watching: Codes.Colors.Yellow,
				PartStatuses.Watched: Codes.Colors.Green
			}[Part.status]

			Series = ""
			if Part.series:
				if Part.status == PartStatuses.Watching:
					PartProgress = StringifyFloat(Part.progress * 100.0)
					PartProgress = f" ({PartProgress}% viewed)"
					Series = f"{Part.viewed} / {Part.series} series {PartProgress}"

				elif Part.series > 1: Series = f"{Part.series} series"

			#---> Вывод данных части.
			#==========================================================================================#
			print(TextStyler(text_color = PartColor).get_styled_text(" " * 4 + f"{Index} ▸ {Part.type.value}{PartNumber}:{PartName}{PartStatusEmoji}"))
			if Series: print(TextStyler(text_color = PartColor).get_styled_text(" " * 12 + Series))
			if Part.comment: print(" " * 12 + GRAY.get_styled_text(f"💭 {Part.comment}"))