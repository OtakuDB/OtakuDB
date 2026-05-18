from .Manifest import Manifest

from Source.Core import Exceptions

from dublib.Methods.Filesystem import ListDir

from typing import Literal, TYPE_CHECKING
from pathlib import Path
import importlib
import shutil
import os

if TYPE_CHECKING:
	from .Note import BaseNote

	from Source.Core.Session.TableDescriptor import TableDescriptor
	from Source.Core.Session.Driver import Driver

class BaseTable:
	"""Базовая таблица."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def manifest(self) -> Manifest:
		"""Манифест таблицы."""

		return self._Descriptor.manifest

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self._Descriptor.name

	@property
	def notes(self) -> "tuple[BaseNote]":
		"""Список записей."""

		return tuple(self._Notes.values())
	
	@property
	def notes_id(self) -> tuple[int]:
		"""Список ID записей."""

		return self._GetNotesID()

	@property
	def path(self) -> Path:
		"""Виртуальный путь к таблице."""

		return self._Descriptor.path

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

	def _GetNotesID(self) -> tuple[int]:
		"""
		Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON.

		:return: Последовательность ID записей.
		:rtype: tuple[int]
		"""

		ListID = list()
		Files = ListDir(self._TotalPath)
		Files = list(filter(lambda File: File.endswith(".json"), Files))

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

		self._TotalPath = self._Driver.storage_directory / self._Descriptor.path
		self._Notes: "dict[int, BaseNote]" = dict()
		self._NoteClass = self._GetNoteClass()
		
		self._PostInitMethod()

	def delete(self):
		"""Удаляет таблицу."""

		shutil.rmtree(self._TotalPath)

	def load_data(self):
		"""Загружает данные таблицы."""

		for ID in self._GetNotesID(): self._Notes[ID] = self._NoteClass(self._Driver, self, ID)
		self._PostLoadMethod()

	def rename(self, name: str):
		"""
		Переименовывает таблицу.

		:param name: Новое название таблицы.
		:type name: str
		"""

		# To-Do: проверка валидности имени.
		OldPath = self._TotalPath
		NewPath = self._TotalPath.parent / name
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
		:param mode: Режим изменения: **i** ― вставка, **o** ― перезапись,**s** ― обмен местами. По умолчанию используется вставка.
		:type mode: Literal["i", "o", "s"] | None
		:raises NoteNotFound: Запись не найдена в таблице.
		:raises ValueError: Неверный режим изменения.
		"""

		IsTargetNoteExists = new_id in self._Notes
		mode = mode or "i"

		if note_id not in self._Notes: raise Exceptions.Table.NoteNotFound(note_id)
		if mode not in ("i", "o", "s"): raise ValueError("Incorrect changing mode.")
		if IsTargetNoteExists and mode == "i": raise Exceptions.Table.OperationError("Unable insert. Target ID already exists.")

		if IsTargetNoteExists:

			match mode:

				case "i":
					self.change_note_id(note_id, 0)
					NotesID = list(self._Notes.keys())
					NotesID = sorted(NotesID)
					Buffer = list(NotesID)

					for ID in Buffer:
						if ID < new_id: NotesID.remove(ID)

					Buffer = list(NotesID)
					NewBuffer = list()
					IsFirst = True

					for ID in Buffer:

						if ID + 1 in Buffer:
							NewBuffer.append(ID)

						elif IsFirst: 
							NewBuffer.append(ID)
							break

					NotesID = NewBuffer
					if note_id in NotesID: NotesID.remove(note_id)
					NotesID.reverse()

					for ID in NotesID: self.change_note_id(ID, ID + 1)
					self.change_note_id(0, new_id)

				case "o":
					self.delete_note(new_id)
					self._Notes[note_id].set_id(new_id)

				case "s":
					FirstNote = self._Notes[note_id]
					SecondNote = self._Notes[new_id]

					FirstNote.set_id(0)
					SecondNote.set_id(note_id)
					FirstNote.set_id(new_id)

					self._Notes[note_id] = SecondNote
					self._Notes[new_id] = FirstNote

		else:
			self._Notes[new_id] = self._Notes[note_id]
			self._Notes[new_id].set_id(new_id)
			del self._Notes[note_id]

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
		os.remove(self._TotalPath / f"{note_id}.json")

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
