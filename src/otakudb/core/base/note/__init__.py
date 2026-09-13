import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from dublib.functions.data import deep_copy
from dublib.functions.filesystem import json

from .attachments import Attachments
from .enums import CallbacksTypes
from .metainfo import Metainfo

if TYPE_CHECKING:
	from otakudb.core.base.table import BaseTable
	from otakudb.core.base.table.connector.bonds import NoteBonds
	from otakudb.core.session.driver import Driver

class BaseNote:
	"""Базовая запись."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def attachments(self) -> Attachments:
		"""Оператор вложений."""

		return self._Attachments
	
	@property
	def bonds(self) -> "NoteBonds":
		"""Связи записи."""

		return self._Table.connector.bonds.get_note_bonds(self._ID)

	@property
	def full_path(self) -> Path:
		"""Полный путь к файлу записи."""

		return self._Table.full_path / f"{self._ID}.json"

	@property
	def id(self) -> int:
		"""ID записи."""

		return self._ID

	@property
	def metainfo(self) -> Metainfo:
		"""Оператор метаданных."""

		return self._Metainfo

	@property
	def name(self) -> str | None:
		"""Название записи."""

		return self._Data.get("name")
	
	@property
	def searchable_strings(self) -> list[str]:
		"""Список строк, которые индексируются для поисковых запросов."""

		return self._export_searchable_strings()

	@property
	def table(self) -> "BaseTable":
		"""Таблица, к которой относится запись."""

		return self._Table

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _load_data(self):
		"""Считывает данные записи или создаёт локальный файл при отсутствии такового."""

		NoteFullPath = self.full_path

		self._Data: dict = {
			"name": None,
			"metainfo": {},
			"attachments": dict.fromkeys(self._Table.manifest.attachments.slots_names, None)
		} | self._export_empty_note()

		if NoteFullPath.exists():
			self._Data = self._Data | json.read(NoteFullPath)
			self._parse_containers()

		else:
			self._parse_containers()
			self.save()

	def _parse_containers(self):
		"""Парсит контейнерные типы данных."""

		self._Metainfo = Metainfo(self, self._Data.get("metainfo", {}))
		self._Attachments = Attachments(self, self._Data.get("attachments", {}))

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ ОБРАБОТЧИКИ CALLBACK-ВЫЗОВОВ <<<<< #
	#==========================================================================================#	

	def _callback_slave_note_saved(self, slave_note: "BaseNote"):
		"""
		Обработчик вызова: привязанные запись выполнила сохранение.

		:param slave_note: Привязанная запись, выполнившая операцию сохранения.
		:type slave_note: BaseNote
		"""

		pass

	def _callback_attachments_changed(self):
		"""Обработчик вызова: вложения изменены."""

		pass

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ ТРИГГЕРНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _pre_dict_formatter(self):
		"""Метод, выполняющийся перед конвертированием записи в словарь (фактически, перед её сохранением)."""

		pass

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _post_local_bind(self, note: "BaseNote"):
		"""
		Метод, выполняющийся после привязки локальной записи.

		:param note: Привязанная запись.
		:type note: BaseNote
		"""

		pass

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _export_empty_note(self) -> dict[str, Any]:
		"""
		Возвращает пустую структуру записи.

		Поля _name_, _metainfo_, _attachments_ будут добавлены автоматически, но их можно указать для определения порядка.

		:return: Пустая структура записи.
		:rtype: dict[str, Any]
		"""

		return {}

	def _export_searchable_strings(self) -> list[str]:
		"""
		Список индексируемых для поисковых запросов строк.

		:return: Список строк, которые индексируются для поисковых запросов.
		:rtype: list[str]
		"""

		Strings: list[str] = []

		if self.name: Strings.append(self.name)

		for Key in ("localized_name", "another_name", "another_names"):
			NameObject: list[str] | str | None = self._Data.get(Key)
			if isinstance(NameObject, list): Strings += NameObject
			elif NameObject: Strings.append(NameObject)

		return Strings

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: "BaseTable", note_id: int):
		"""
		Базовая запись.

		:param table: Таблица.
		:type table: BaseTable
		:param note_id: ID записи.
		:type note_id: int
		:raises ValueError: Обязательный ключ отсутствует в файле записи.
		"""

		self._Driver: "Driver" = driver
		self._Table = table
		self._ID: int = note_id
		
		self._load_data()
		self.sort()
		self._parse_containers()
		self._post_init()

	def delete(self):
		"""Удаляет запись."""

		self._Table.delete_note(self._ID)

	def rename(self, name: str | None):
		"""
		Задаёт имя записи.

		:param name: Новое имя записи.
		:type name: str | None
		"""

		if type(name) is str: name = name.strip()
		self._Data["name"] = name
		self.save()

	def run_callback(self, callback_type: CallbacksTypes, *args, **kwargs):
		"""
		Запускает обработчик обновления связанной записи.

		:param note: Связанная запись, выполнившая операцию сохранения.
		:type note: BaseNote
		:param *args: Позиционные аргументы.
		:param **kwargs: Именованные аргументы.
		"""

		match callback_type:
			case CallbacksTypes.AttachmentsChanged: self._callback_attachments_changed(*args, **kwargs)
			case CallbacksTypes.SlaveNoteSaved: self._callback_slave_note_saved(*args, **kwargs)

	def save(self):
		"""Сохраняет данные записи в локальный файл JSON."""

		IsNoteFileExists = self.full_path.exists()

		json.write(self.full_path, self.to_dict(copy = False), atomic = True)

		if IsNoteFileExists:
			for Master in self.bonds.masters: Master.run_callback(CallbacksTypes.SlaveNoteSaved, self)

	def set_id(self, note_id: int):
		"""
		Задаёт новый ID и переименовывает файл записи.

		:param note_id: Новый ID записи.
		:type note_id: int
		"""

		OldPath = self.full_path
		NewPath = OldPath.parent / f"{note_id}.json"
		os.rename(OldPath, NewPath)
		self._Attachments.move(note_id)
		self._Table.connector.bonds.update_note_id(self._ID, note_id)
		self._ID = note_id

	def sort(self):
		"""
		Сортирует ключи записи в алфавитном порядке.
		
		Важные ключи _name_, _matainfo_, _attachments_ помещаются в начало.
		"""

		ImportantKeys = ("name", "matainfo", "attachments")
			
		def NoteKeysSorter(item: tuple[str, Any]) -> tuple[Literal[0, 1], int, str]:
			"""
			Генератор кортежей сортировки словарного ключей записи.

			:param item: Элемент словаря.
			:type item: tuple[str, Any]
			:return: Кортеж из трёх значений: `1` или `0` для важных и неважных ключей; индекс важного ключа или `0`; ключ.
			:rtype: tuple[Literal[0, 1], int, str]
			"""

			Key = item[0]
			if Key in ImportantKeys: return (0, ImportantKeys.index(Key), "")

			return (1, 0, Key.lower())

		self._Data = dict(sorted(self._Data.items(), key = NoteKeysSorter))

	def to_dict(self, copy: bool = True, sort: bool = False) -> dict:
		"""
		Возвращает словарное представление записи.

		:param copy: Указывает, нужно ли вернуть копию внутреннего словаря или оригинал.
		:type copy: bool
		:param sort: Указывает, нужно ли произвести сортировку ключей.
		:type sort: bool
		:return: Словарное представление записи.
		:rtype: dict
		"""

		self._pre_dict_formatter()
		self._Data["metainfo"] = self._Metainfo.to_dict(copy)
		self._Data["attachments"] = self._Attachments.to_dict()
		if sort: self.sort()

		return deep_copy(self._Data) if copy else self._Data