from ..Manifest import Manifest

from .Connector import Connector

from Source.Core import Exceptions

from dublib.Methods.Filesystem import ListDir

from typing import Literal, TYPE_CHECKING
from pathlib import Path
import importlib
import shutil
import os

if TYPE_CHECKING:
	from ..Note import BaseNote

	from Source.Core.Session.TableDescriptor import TableDescriptor
	from Source.Core.Session.Driver import Driver

class BaseTable:
	"""Базовая таблица."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def connector(self) -> Connector:
		"""Оператор связей."""

		return self._Connector

	@property
	def full_path(self) -> Path:
		"""Полный путь к директории таблицы."""

		return self._Descriptor.full_path

	@property
	def manifest(self) -> Manifest:
		"""Манифест таблицы."""

		return self._Descriptor.manifest

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self._Descriptor.name

	@property
	def notes(self) -> "tuple[BaseNote, ...]":
		"""Список записей."""

		return tuple(self._Notes.values())
	
	@property
	def notes_id(self) -> tuple[int, ...]:
		"""Список ID записей."""

		return self._GetNotesID()

	@property
	def virtual_path(self) -> Path:
		"""Виртуальный путь к таблице."""

		return self._Descriptor.virtual_path

	#==========================================================================================#
	# >>>>> ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GenerateNewNoteID(self) -> int:
		"""
		Генерирует новый ID с повторным использованием освободившихся.

		:return: Новый уникальный ID.
		:rtype: int
		"""

		SequenceID = self._GetNotesID()

		if self.manifest.common.recycle_id:
			for ID in range(1, len(SequenceID) + 1):
				if ID not in SequenceID: return ID

		return int(max(SequenceID)) + 1 if len(SequenceID) > 0 else 1

	def _GetNoteClass(self) -> type:
		"""
		Возвращает класс записи.

		:return: Класс записи.
		:rtype: type
		"""

		ImportPath = f"Source.Tables.{self.manifest.type}.note"
		NoteModule = importlib.import_module(ImportPath)

		return NoteModule.Note

	def _GetNotesID(self) -> tuple[int, ...]:
		"""
		Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON.

		:return: Последовательность ID записей.
		:rtype: tuple[int]
		"""

		ListID = list()
		Files = ListDir(self.full_path)
		Files = list(filter(lambda File: File.endswith(".json") and File[:-5].isdigit(), Files))

		for File in Files: 
			if not File.replace(".json", "").isdigit(): Files.remove(File)

		for File in Files: ListID.append(int(File.replace(".json", "")))
		
		return tuple(ListID)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта таблицы."""

		pass

	def _PostLoadMethod(self):
		"""Метод, выполняющийся после чтения данных таблицы."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, driver: "Driver", descriptor: "TableDescriptor"):
		"""
		Базовая таблица.

		:param session: Сессия.
		:type session: Session
		:param storage: Путь к каталогу таблицы.
		:type storage: PathLike
		:param name: Название таблицы.
		:type name: str
		"""
		
		self._Driver = driver
		self._Descriptor = descriptor

		self._Notes: "dict[int, BaseNote]" = dict()
		self._NoteClass = self._GetNoteClass()
		self._Connector = Connector(self)
		
		self._PostInitMethod()

	def delete(self):
		"""Удаляет таблицу."""

		shutil.rmtree(self.full_path)

	def load_data(self):
		"""Загружает данные таблицы."""

		for ID in self._GetNotesID(): self._Notes[ID] = self._NoteClass(self._Driver, self, ID)
		self._PostLoadMethod()

	def rename(self, name: str):
		"""
		Переименовывает таблицу.

		:param name: Новое название таблицы.
		:type name: str
		:raises ValueError: Невозможное имя.
		"""

		if "/" in name or "\"" in name: raise ValueError("Name can't contains slashes.")
		TableFullPath = self.full_path
		OldPath = TableFullPath
		NewPath = TableFullPath.parent / name
		os.rename(OldPath, NewPath)
		self._Descriptor.rename(name)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ УПРАВЛЕНИЯ ЗАПИСЯМИ <<<<< #
	#==========================================================================================#

	def change_note_id(self, note_id: int, new_id: int, mode: Literal["i", "o", "s"] | None = None):
		"""
		Изменяет ID записи.

		:param note_id: Текущий ID.
		:type note_id: int
		:param new_id: Новый ID.
		:type new_id: int
		:param mode: Режим изменения: **i** ― вставка со сдвигом, **o** ― перезапись, **s** ― обмен местами. По умолчанию возможна вставка только на позицию со свободным индексом.
		:type mode: Literal["i", "o", "s"] | None
		:raises NoteNotFound: Запись не найдена в таблице.
		:raises ValueError: Неверный режим изменения.
		"""

		IsTargetNoteExists = new_id in self._Notes

		if note_id not in self._Notes: raise Exceptions.Table.NoteNotFound(note_id)
		if mode not in (None, "i", "o", "s"): raise ValueError("Incorrect changing mode.")

		match mode:

			case None:
				if IsTargetNoteExists: raise Exceptions.Table.OperationError("Unable insert. Target ID already exists.")
				self._Notes[new_id] = self._Notes[note_id]
				self._Notes[new_id].set_id(new_id)
				del self._Notes[note_id]

			case "i":

				if not IsTargetNoteExists:
					self.change_note_id(note_id, new_id)
					return

				self.change_note_id(note_id, 0)

				AffectedNotesID = sorted(CurrentNote.id for CurrentNote in self._Notes.values() if CurrentNote.id >= new_id)
				Buffer = list()

				for CurrentID in AffectedNotesID:

					if not Buffer:
						Buffer.append(CurrentID)
						continue

					if CurrentID - Buffer[-1] != 1: break 
					Buffer.append(CurrentID)

				AffectedNotesID = list(reversed(Buffer))
				for CurrentID in AffectedNotesID: self.change_note_id(CurrentID, CurrentID + 1)
				self.change_note_id(0, new_id)

			case "o":
				self.delete_note(new_id)
				self._Notes[note_id].set_id(new_id)

			case "s":
				if not IsTargetNoteExists: raise Exceptions.Table.OperationError("Unable swap. Target ID is free.")
				FirstNote = self._Notes[note_id]
				SecondNote = self._Notes[new_id]

				FirstNote.set_id(0)
				SecondNote.set_id(note_id)
				FirstNote.set_id(new_id)

				self._Notes[note_id] = SecondNote
				self._Notes[new_id] = FirstNote

	def create_note(self) -> "BaseNote":
		"""
		Создаёт запись.

		:return: Запись.
		:rtype: Note
		"""

		NewNoteID = self._GenerateNewNoteID()
		self._Notes[NewNoteID] = self._NoteClass(self._Driver, self, NewNoteID)

		return self._Notes[NewNoteID]

	def delete_note(self, note_id: int):
		"""
		Удаляет запись.

		:param note_id: ID записи.
		:type note_id: int
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		if note_id not in self._Notes: raise Exceptions.Table.NoteNotFound(note_id)
		del self._Notes[note_id]
		os.remove(self.full_path / f"{note_id}.json")

	def get_note(self, note_id: int) -> "BaseNote":
		"""
		Возвращает запись.

		:param note_id: ID записи.
		:type note_id: int
		:return: Запись.
		:rtype: Note
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		if note_id not in self._Notes: raise Exceptions.Table.NoteNotFound(note_id)

		return self._Notes[note_id]
	
	def is_note_exists(self, note_id: int) -> bool:
		"""
		Проверяет, существует ли запись с указанным ID.

		:param note_id: ID записи.
		:type note_id: int
		:return: Возвращает `True`, если запись существует.
		:rtype: bool
		"""

		return note_id in self._Notes
