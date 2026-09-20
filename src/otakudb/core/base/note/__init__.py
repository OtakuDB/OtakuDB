from typing import TYPE_CHECKING, Any, Literal, Self

from dublib.functions.data import deep_copy
from dublib.functions.data.dictionary import deep_merge
from dublib.functions.filesystem import json

from .attachments import Attachments
from .enums import CallbacksTypes
from .metainfo import Metainfo

if TYPE_CHECKING:
	from pathlib import Path

	from ...session.driver import Driver
	from ..table import BaseTable
	from ..table.connector.bonds import NoteBonds

class BaseNote[T: "BaseTable"]:
	"""Базовая запись."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def attachments(self) -> Attachments[Self]:
		"""Оператор вложений."""

		return self._attachments
	
	@property
	def bonds(self) -> "NoteBonds[Self]":
		"""Связи записи."""

		return self._table.connector.bonds.get_note_bonds(self._note_id)

	@property
	def full_path(self) -> Path:
		"""Полный путь к файлу записи."""

		return self._table.full_path / f"{self._note_id}.json"

	@property
	def id(self) -> int:
		"""ID записи."""

		return self._note_id

	@property
	def metainfo(self) -> Metainfo[Self]:
		"""Оператор метаданных."""

		return self._metainfo

	@property
	def name(self) -> str | None:
		"""Название записи."""

		return self._data.get("name")
	
	@property
	def searchable_strings(self) -> tuple[str, ...]:
		"""Список строк, которые индексируются для поисковых запросов."""

		return self._export_searchable_strings()

	@property
	def table(self) -> "BaseTable":
		"""Таблица, к которой относится запись."""

		return self._table

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _load_data(self):
		"""Считывает данные записи или создаёт локальный файл при отсутствии такового."""

		self._data |= self._export_empty_note()
		note_full_path: Path = self.full_path

		if note_full_path.exists():
			self._data = deep_merge(self._data, json.read(note_full_path), uniqueness = True)
			self._parse_containers()

		else:
			self._parse_containers()
			self.save()

	def _parse_containers(self):
		"""Парсит контейнерные типы данных."""

		self._metainfo: Metainfo[Self] = Metainfo(self, self._data.get("metainfo", {}))
		self._attachments: Attachments[Self] = Attachments(self, self._data.get("attachments", {}))

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ ОБРАБОТЧИКИ CALLBACK-ВЫЗОВОВ <<<<< #
	#==========================================================================================#	

	def _callback_slave_note_saved(self, slave_note: Self):
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

	def _post_binding(self, note: Self):
		"""
		Метод, выполняющийся после создания связи.

		:param note: Привязанная запись.
		:type note: BaseNote
		"""

		pass

	def _post_hyperlinking(self, note: "BaseNote"):
		"""
		Метод, выполняющийся после создания гиперссылки.

		:param note: Запись, на которую создана гиперссылка.
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

	def _export_searchable_strings(self) -> tuple[str, ...]:
		"""
		Список индексируемых для поисковых запросов строк.

		:return: Последовательность строк, которые индексируются для поисковых запросов.
		:rtype: Sequence[str]
		"""

		strings: list[str] = []

		if self.name:
			strings.append(self.name)

		for key in ("localized_name", "another_name", "another_names"):
			strings_container: list[str] | str | None = self._data.get(key)
			if isinstance(strings_container, list): strings += strings_container
			elif strings_container: strings.append(strings_container)

		return tuple(strings)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: T, note_id: int):
		"""
		Базовая запись.

		:param driver: Драйвер хранилища.
		:type driver: Driver
		:param table: Таблица.
		:type table: BaseTable
		:param note_id: ID записи.
		:type note_id: int
		"""

		self._driver: "Driver" = driver
		self._table: T = table
		self._note_id: int = note_id

		self._data: dict = {
			"name": None,
			"metainfo": {},
			"attachments": dict.fromkeys(self._table.manifest.attachments.slots_names, None)
		}
		
		self._load_data()
		self.sort()
		self._parse_containers()
		
		self._post_init()

	def delete(self):
		"""Удаляет запись."""

		self._table.delete_note(self._note_id)

	def rename(self, name: str | None):
		"""
		Задаёт имя записи.

		:param name: Новое имя записи.
		:type name: str | None
		"""

		if isinstance(name, str): name = name.strip()
		self._data["name"] = name
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
			case CallbacksTypes.SlaveSaved: self._callback_slave_note_saved(*args, **kwargs)

	def save(self):
		"""Сохраняет данные записи в локальный файл JSON."""

		is_file_creation: bool = not self.full_path.exists()
		json.write(self.full_path, self.to_dict(copy = False), atomic = True)

		if is_file_creation:
			for Master in self.bonds.masters:
				Master.run_callback(CallbacksTypes.SlaveSaved, self)

	def set_id(self, note_id: int):
		"""
		Задаёт новый ID и переименовывает файл записи.

		:param note_id: Новый ID записи.
		:type note_id: int
		"""

		old_path: "Path" = self.full_path
		new_path: "Path" = old_path.parent / f"{note_id}.json"
		old_path.rename(new_path)

		self._attachments.move(note_id)
		self._table.connector.bonds.update_note_id(self._note_id, note_id)
		self._note_id = note_id

	def sort(self):
		"""
		Сортирует ключи записи в алфавитном порядке.
		
		Важные ключи _name_, _matainfo_, _attachments_ помещаются в начало.
		"""

		important_keys: tuple[str, ...] = ("name", "matainfo", "attachments")
			
		def note_keys_sorter(item: tuple[str, Any]) -> tuple[Literal[0, 1], int, str]:
			"""
			Генератор кортежей сортировки словарного ключей записи.

			:param item: Элемент словаря.
			:type item: tuple[str, Any]
			:return: Кортеж из трёх значений: `1` или `0` для важных и неважных ключей; индекс важного ключа или `0`; ключ.
			:rtype: tuple[Literal[0, 1], int, str]
			"""

			key: str = item[0]
			if key in important_keys:
				return (0, important_keys.index(key), "")

			return (1, 0, key.lower())

		self._data = dict(sorted(self._data.items(), key = note_keys_sorter))

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
		self._data["metainfo"] = self._metainfo.to_dict(copy)
		self._data["attachments"] = self._attachments.to_dict()
		if sort: self.sort()

		return deep_copy(self._data) if copy else self._data