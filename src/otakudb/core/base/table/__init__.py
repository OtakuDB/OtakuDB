import importlib
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from ... import exceptions
from .connector import Connector

if TYPE_CHECKING:
	from ...session.driver import Driver
	from ...session.table_descriptor import TableDescriptor
	from ..manifest import Manifest
	from ..note import BaseNote

class BaseTable[N: "BaseNote"]:
	"""Базовая таблица."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def connector(self) -> Connector:
		"""Оператор связей."""

		return self._connector

	@property
	def full_path(self) -> Path:
		"""Полный путь к директории таблицы."""

		return self._descriptor.full_path

	@property
	def manifest(self) -> "Manifest":
		"""Манифест таблицы."""

		return self._descriptor.manifest

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self._descriptor.name

	@property
	def notes(self) -> tuple[N, ...]:
		"""Список записей."""

		return tuple(self._notes.values())
	
	@property
	def notes_id(self) -> tuple[int, ...]:
		"""Последовательность ID записей."""

		return self._get_notes_id()

	@property
	def virtual_path(self) -> Path:
		"""Виртуальный путь к таблице."""

		return self._descriptor.virtual_path

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ ИЗМЕНЕНИЯ ID ЗАПИСЕЙ <<<<< #
	#==========================================================================================#

	def _change_note_id(self, note_id: int, new_id: int, is_target_note_exists: bool):
		"""
		Обрабатывает режим изменения ID записи: базовое изменение.

		:param note_id: Текущий ID.
		:type note_id: int
		:param new_id: Новый ID.
		:type new_id: int
		:param is_target_note_exists: Состояние: существует ли запись с новым ID.
		:type is_target_note_exists: bool
		"""

		if is_target_note_exists:
			raise exceptions.table.OperationError("Unable insert. Target ID already exists.")

		self._notes[new_id] = self._notes[note_id]
		self._notes[new_id].set_id(new_id)
		del self._notes[note_id]

	def _insert_note(self, note_id: int, new_id: int, is_target_note_exists: bool):
		"""
		Обрабатывает режим изменения ID записи: вставка.

		:param note_id: Текущий ID.
		:type note_id: int
		:param new_id: Новый ID.
		:type new_id: int
		:param is_target_note_exists: Состояние: существует ли запись с новым ID.
		:type is_target_note_exists: bool
		"""

		if not is_target_note_exists:
			self.change_note_id(note_id, new_id)
			return

		self.change_note_id(note_id, 0)

		affected_notes_id: list[int] = sorted(note.id for note in self._notes.values() if note.id >= new_id)
		buffer: list[int] = []

		for current_note_id in affected_notes_id:

			if not buffer:
				buffer.append(current_note_id)
				continue

			if current_note_id - buffer[-1] != 1: break 
			buffer.append(current_note_id)

		affected_notes_id = list(reversed(buffer))

		for current_note_id in affected_notes_id:
			self.change_note_id(current_note_id, current_note_id + 1)

		self.change_note_id(0, new_id)
		
	def _overwrite_note(self, note_id: int, new_id: int, is_target_note_exists: bool):
		"""
		Обрабатывает режим изменения ID записи: перезапись.

		:param note_id: Текущий ID.
		:type note_id: int
		:param new_id: Новый ID.
		:type new_id: int
		:param is_target_note_exists: Состояние: существует ли запись с новым ID.
		:type is_target_note_exists: bool
		"""

		if is_target_note_exists: self.delete_note(new_id)
		self._notes[note_id].set_id(new_id)

	def _swap_note(self, note_id: int, new_id: int, is_target_note_exists: bool):
		"""
		Обрабатывает режим изменения ID записи: обмен.

		:param note_id: Текущий ID.
		:type note_id: int
		:param new_id: Новый ID.
		:type new_id: int
		:param is_target_note_exists: Состояние: существует ли запись с новым ID.
		:type is_target_note_exists: bool
		"""

		if not is_target_note_exists:
			raise exceptions.table.OperationError("Unable swap. Target ID is free.")

		FirstNote = self._notes[note_id]
		SecondNote = self._notes[new_id]

		FirstNote.set_id(0)
		SecondNote.set_id(note_id)
		FirstNote.set_id(new_id)

		self._notes[note_id] = SecondNote
		self._notes[new_id] = FirstNote

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _generate_new_note_id(self) -> int:
		"""
		Генерирует новый ID с повторным использованием освободившихся.

		:return: Новый уникальный ID.
		:rtype: int
		"""

		notes_id: tuple[int, ...] = self._get_notes_id()

		if self.manifest.common.recycle_id:
			for note_id in range(1, len(notes_id) + 1):
				if note_id not in notes_id:
					return note_id

		return max(notes_id) + 1 if notes_id else 1

	def _get_note_class(self) -> type[N]:
		"""
		Возвращает класс записи.

		:return: Класс записи.
		:rtype: type[BaseNote]
		"""

		module_path: str = f"otakudb.tables.{self.manifest.table_type}.note"
		note_module = importlib.import_module(module_path)

		return note_module.Note

	def _get_notes_id(self) -> tuple[int, ...]:
		"""
		Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON.

		:return: Последовательность ID записей.
		:rtype: tuple[int]
		"""

		return tuple(
			int(entry.name[:-5])
			for entry in os.scandir(self.full_path)
			if entry.is_file() and entry.name.endswith(".json") and entry.name[:-5].isdigit()
		)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта таблицы."""

		pass

	def _post_load(self):
		"""Метод, выполняющийся после чтения данных таблицы."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, driver: "Driver", descriptor: "TableDescriptor"):
		"""
		Базовая таблица.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param descriptor: Дескриптор таблицы.
		:type descriptor: TableDescriptor
		"""

		self._driver: "Driver" = driver
		self._descriptor: "TableDescriptor" = descriptor

		self._notes: dict[int, N] = {}
		self._note_class: type[N] = self._get_note_class()

		self._connector = Connector(self)
		
		self._post_init()

	def delete(self):
		"""Удаляет директорию таблицы."""

		shutil.rmtree(self.full_path)

	def load_data(self):
		"""Загружает данные таблицы."""
		
		self._notes = {note_id: self._note_class(self._driver, self, note_id) for note_id in self.notes_id}
		self._post_load()

	def rename(self, name: str):
		"""
		Переименовывает таблицу.

		:param name: Новое название таблицы.
		:type name: str
		:raises ValueError: Невозможное имя.
		"""

		if "/" in name or "\\" in name:
			raise ValueError("Name can't contains slashes.")

		old_full_path: Path = self.full_path
		new_full_path = old_full_path.parent / name
		os.rename(old_full_path, new_full_path)

		self._descriptor.rename(name)

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
		:raises NoteNotFoundError: Запись не найдена в таблице.
		:raises ValueError: Неверный режим изменения.
		"""

		if note_id not in self._notes:
			raise exceptions.table.NoteNotFoundError(note_id)

		if mode not in (None, "i", "o", "s"):
			raise ValueError("Incorrect changing mode.")

		is_target_note_exists: bool = self.is_note_exists(new_id)

		match mode:
			case None: self._change_note_id(note_id, new_id, is_target_note_exists)
			case "i": self._insert_note(note_id, new_id, is_target_note_exists)
			case "o": self._overwrite_note(note_id, new_id, is_target_note_exists)
			case "s": self._swap_note(note_id, new_id, is_target_note_exists)

	def create_note(self) -> N:
		"""
		Создаёт запись.

		:return: Запись.
		:rtype: BaseNote
		"""

		new_note_id: int = self._generate_new_note_id()
		new_note: N = self._note_class(self._driver, self, new_note_id)
		self._notes[new_note_id] = new_note

		return new_note

	def delete_note(self, note_id: int):
		"""
		Удаляет запись.

		:param note_id: ID записи.
		:type note_id: int
		:raises NoteNotFoundError: Запись не найдена в таблице.
		"""

		if not self.is_note_exists(note_id):
			raise exceptions.table.NoteNotFoundError(note_id)

		del self._notes[note_id]

		note_path: Path = self.full_path / f"{note_id}.json"
		note_path.unlink()

	def get_note(self, note_id: int) -> N:
		"""
		Возвращает запись.

		:param note_id: ID записи.
		:type note_id: int
		:return: Запись.
		:rtype: BaseNote
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		if not self.is_note_exists(note_id):
			raise exceptions.table.NoteNotFoundError(note_id)

		return self._notes[note_id]
	
	def is_note_exists(self, note_id: int, not_found_error: bool = False) -> bool:
		"""
		Проверяет, существует ли запись с указанным ID.

		:param note_id: ID записи.
		:type note_id: int
		:param not_found_error: Указывает, выбрасывать ли исключение при отсутствии записи.
		:type not_found_error: bool
		:return: Возвращает `True`, если запись существует.
		:rtype: bool
		:raises NoteNotFoundError: Запись не найдена.
		"""

		is_note_found: bool = note_id in self._notes

		if not is_note_found and not_found_error:
			raise exceptions.table.NoteNotFoundError(note_id)

		return is_note_found
