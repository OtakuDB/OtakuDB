from .Attachments import Attachments
from .Enums import CallbacksTypes
from .Metainfo import Metainfo

from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.Methods.Data import Copy

from typing import Any, Literal, TYPE_CHECKING
from pathlib import Path
import os

if TYPE_CHECKING:
	from Source.Core.Session.Driver import Driver
	from Source.Core.Base.Table import BaseTable

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

		return self._GetSearchableStrings()

	@property
	def table(self) -> "BaseTable":
		"""Таблица, к которой относится запись."""

		return self._Table

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _LoadData(self):
		"""Считывает данные записи или создаёт локальный файл при отсутствии такового."""

		NoteFullPath = self.full_path

		self._Data = {
			"name": None,
			"metainfo": dict(),
			"attachments": dict().fromkeys(self._Table.manifest.attachments.slots.keys(), None)
		} | self._GetEmptyNote()

		if NoteFullPath.exists():
			self._Data = self._Data | ReadJSON(NoteFullPath)
			self._ParseContainers()

		else:
			self._ParseContainers()
			self.save(use_presaver = False)

	def _ParseContainers(self):
		"""Парсит контейнерные типы данных."""

		self._Metainfo = Metainfo(self, self._Data.get("metainfo") or dict())
		self._Attachments = Attachments(self, self._Data.get("attachments") or dict())

	def _RunPostSaveCallbacksForBinds(self):
		"""Запускает обработку изменений в записях, привязавших текущую запись."""

		Masters = tuple(CurrentNote for CurrentNote in self._Table.notes if self._ID in CurrentNote.binds.local.notes_id)
		for MasterNote in Masters: MasterNote.run_local_bind_callback(self)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ ОБРАБОТЧИКИ CALLBACK-ВЫЗОВОВ <<<<< #
	#==========================================================================================#	

	def _Callback_SlaveNoteSaved(self, slave_note: "BaseNote"):
		"""
		Обработчик вызова: привязанные запись выполнила сохранение.

		:param slave_note: Привязанная запись, выполнившая операцию сохранения.
		:type slave_note: BaseNote
		"""

		pass

	def _Callback_AttachmentsChanged(self):
		"""Обработчик вызова: вложения изменены."""

		pass

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ ТРИГГЕРНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _PostLocalBindMethod(self, note: "BaseNote"):
		"""
		Метод, выполняющийся после привязки локальной записи.

		:param note: Привязанная запись.
		:type note: BaseNote
		"""

		pass

	def _PreSaveMethod(self):
		"""Метод, выполняющийся перед сохранением записи."""

		pass

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GetEmptyNote(self) -> dict[str, Any]:
		"""
		Возвращает пустую структуру записи.

		Поля _name_, _metainfo_, _attachments_ будут добавлены автоматически, но их можно указать для определения порядка.

		:return: Пустая структура записи.
		:rtype: dict[str, Any]
		"""

		return dict()

	def _GetSearchableStrings(self) -> list[str]:
		"""
		Список индексируемых для поисковых запросов строк.

		:return: Список строк, которые индексируются для поисковых запросов.
		:rtype: list[str]
		"""

		Strings = list()

		if self.name: Strings.append(self.name)

		for Key in ("localized_name", "another_name", "another_names"):
			NameObject = self._Data.get(Key)
			if type(NameObject) == list: Strings += NameObject
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

		self._Driver = driver
		self._Table = table
		self._ID = note_id
		
		self._LoadData()
		self.sort()
		self._ParseContainers()
		self._PostInitMethod()

	def delete(self):
		"""Удаляет запись."""

		self._Table.delete_note(self._ID)

	def rename(self, name: str | None):
		"""
		Задаёт имя записи.

		:param name: Новое имя записи.
		:type name: str | None
		"""

		if type(name) == str: name = name.strip()
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
			case CallbacksTypes.AttachmentsChanged: self._Callback_AttachmentsChanged(*args, **kwargs)
			case CallbacksTypes.SlaveNoteSaved: self._Callback_SlaveNoteSaved(*args, **kwargs)

	def save(self, use_presaver: bool = True):
		"""
		Сохраняет данные записи в локальный файл JSON.

		:param use_presaver: Указывает, нужно ли вызывать переопределяемый метод, выполняющийся перед сохранением.
		:type use_presaver: bool
		"""

		WriteJSON(self.full_path, self.to_dict(use_presaver, copy = False), atomic = True)
		for Master in self._Table.binder.local.get_masters(self._ID): Master.run_callback(CallbacksTypes.SlaveNoteSaved, self)

	def set_id(self, id: int):
		"""
		Задаёт новый ID и переименовывает файл записи.

		:param id: Новый ID записи.
		:type id: int
		"""

		OldPath = self.full_path
		NewPath = OldPath.parent / f"{id}.json"
		os.rename(OldPath, NewPath)
		self._Attachments.move(id)
		self._Table.binder.local.update(self._ID, id)
		self._ID = id

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

	def to_dict(self, use_presaver: bool = True, copy: bool = True, sort: bool = False) -> dict:
		"""
		Возвращает словарное представление записи.

		:param use_presaver: Указывает, нужно ли вызывать переопределяемый метод, выполняющийся перед сохранением.
		:type use_presaver: bool
		:param copy: Указывает, нужно ли вернуть копию внутреннего словаря или оригинал.
		:type copy: bool
		:param sort: Указывает, нужно ли произвести сортировку ключей.
		:type sort: bool
		:return: Словарное представление записи.
		:rtype: dict
		"""

		if use_presaver: self._PreSaveMethod()
		self._Data["metainfo"] = self._Metainfo.to_dict(copy)
		self._Data["attachments"] = self._Attachments.to_dict()
		if sort: self.sort()

		return Copy(self._Data) if copy else self._Data