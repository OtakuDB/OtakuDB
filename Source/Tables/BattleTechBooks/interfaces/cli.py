from ..Structs import CollectionStatusses, Statusses, Types

from Source.Interfaces.CLI.Base import BaseTableCLI, BaseNoteCLI
from Source.Interfaces.CLI.Functions import Unstar

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.TextStyler import FastStyler

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..table import Table
	from ..note import Note

class TableCLI(BaseTableCLI):
	"""Интерпретатор CLI таблицы."""

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def _statistics(self):
		"""Выводит статистику чтения произведений."""

		Notes: "tuple[Note]" = self._Table.notes
		Total = len(Notes)
		Novels = 0
		Stories = 0
		Compilations = 0
		Undefined = 0

		Completed = 0

		CollectedBooks = 0
		CollectedEbooks = 0

		for CurrentNote in Notes:
			if CurrentNote.type == Types.Novel: Novels += 1
			elif CurrentNote.type == Types.Story: Stories += 1
			elif CurrentNote.type == Types.Compilation: Compilations += 1
			else: Undefined += 1

			if CurrentNote.status == Statusses.Completed: Completed += 1

			if CurrentNote.collection_status == CollectionStatusses.Ebook: CollectedEbooks += 1
			elif CurrentNote.collection_status == CollectionStatusses.Collected: CollectedBooks += 1

		if Undefined: Undefined = f", {Undefined} undefined"
		else: Undefined = ""
		print(FastStyler("Total books:").decorate.bold, end = "")
		print(f" {Total} ({Novels} novels, {Stories} stories, {Compilations} compilations){Undefined}")

		CompletedPercentage = round(Completed / Total * 100, 2)
		print(FastStyler("Fully readed:").decorate.bold, end = "")
		print(f" {Completed} books ({CompletedPercentage}%)")

		CollectedTotal = CollectedBooks + CollectedEbooks
		CollectedPercentage = round(CollectedTotal / Total * 100, 2)
		print(FastStyler("Collected:").decorate.bold, end = "")
		print(f" {CollectedBooks} books, {CollectedEbooks} ebooks ({CollectedPercentage}%)")

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
			case "statistics": self._statistics()

	def _GenerateCustomCommands(self) -> list[Command]:
		"""
		Возвращает список кастомных команд интерпретатора.

		:return: Возвращает список кастомных команд интерпретатора.
		:rtype: list[Command]
		"""

		CommandsList = list()

		Com = Command("statistics", "Show statistics of BattleTech books reading.")
		CommandsList.append(Com)

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

		#---> ID
		#==========================================================================================#
		container["ID"] = note.id

		#---> Status
		#==========================================================================================#
		match note.status:
			case Statusses.Announced: container["Status"] = FastStyler(Statusses.Announced.value).colorize.magenta
			case Statusses.Planned: container["Status"] = FastStyler(Statusses.Planned.value).colorize.blue
			case Statusses.Reading: container["Status"] = FastStyler(Statusses.Reading.value).colorize.yellow
			case Statusses.Completed: container["Status"] = FastStyler(Statusses.Completed.value).colorize.green
			case Statusses.Dropped: container["Status"] = FastStyler(Statusses.Dropped.value).colorize.red
			case Statusses.Skipped: container["Status"] = FastStyler(Statusses.Skipped.value).colorize.cyan
			case None: container["Status"] = ""

		container["Status"] = {
			CollectionStatusses.Collected: "📦 ",
			CollectionStatusses.Ebook: "🌍 ",
			CollectionStatusses.Wishlist: "🎁 ",
			CollectionStatusses.Ordered: "🚚 ",
			None: "   "
		}[note.collection_status] + container["Status"]

		#---> Name
		#==========================================================================================#
		container["Name"] = note.localized_name or note.name

		#---> Author
		#==========================================================================================#
		Author = note.metainfo["author"] or ""
		if ";" in Author:
			AuthorsCount = Author.count(";")
			Author = Author.split(";")[0] + f" (and {AuthorsCount} other)"
		container["Author"] = Author
		
		#---> Publication
		#==========================================================================================#
		container["Publication"] = note.metainfo["publication_date"]

		#---> Type
		#==========================================================================================#
		container["Type"] = note.type.value

		#---> Series
		#==========================================================================================#
		container["Series"] = note.metainfo["series"]

		#---> Estimation
		#==========================================================================================#
		container["Estimation"] = str(note.estimation) if note.estimation else ""

		#---> Era
		#==========================================================================================#
		NoteEra = note.era
		if NoteEra: NoteEra = NoteEra.name
		else: NoteEra = ""
		container["Era"] = NoteEra

		return container

class NoteCLI(BaseNoteCLI):
	"""Интерпретатор CLI записи."""

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def _eras(self):
		"""Выводит список эр BattleTech."""

		self._Table: "Table"

		for Era in self._Table.eras:
			StartYear = Era.start_year or "earlier"
			EndYear = Era.end_year or "now"
			print(FastStyler(str(Era.index).ljust(8)).decorate.bold, end = "")
			print(f": {Era.name} [{StartYear} – {EndYear}]")

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
			case "eras": self._eras()

	def _GenerateCustomCommands(self) -> list[Command]:
		"""
		Возвращает список кастомных команд интерпретатора.

		:return: Возвращает список кастомных команд интерпретатора.
		:rtype: list[Command]
		"""

		CommandsList = list()

		Com = Command("eras", "Show list of BattleTech eras.")
		CommandsList.append(Com)

		return CommandsList

	def _ViewNote(self):
		"""Отображает запись."""

		NoteName = self._Note.name or ""
		if NoteName: NoteName = NoteName + " "
		print(f"{NoteName}#{self._Note.id}")
