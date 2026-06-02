from Source.Core import Exceptions

from dublib.Methods.Data import Copy

from dataclasses import dataclass
from typing import TYPE_CHECKING
from pathlib import Path
import shutil
import os

if TYPE_CHECKING:
	from . import BaseNote

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class SlotInfo:
	"""Информация о слоте."""

	name: str
	file: str | None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Attachments:
	"""Вложения."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def count(self) -> int:
		"""Количество вложений."""

		return len(self.__Data["free"]) + sum(1 for slot in self.slots if slot.file)

	@property
	def free(self) -> tuple[Path]:
		"""Последовательность свободных вложений."""

		return tuple(Path(Value) for Value in self.__Data["free"])

	@property
	def slots(self) -> tuple[SlotInfo]:
		"""Последовательность данных слотов."""

		return tuple(SlotInfo(Name, File) for Name, File in self.__Data["slots"].items())

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, note: "BaseNote", data: dict):
		"""
		Оператор вложений.

		:param note: Запись.
		:type note: BaseNote
		:param data: Словарь данных вложений.
		:type data: dict
		"""

		self.__Note = note
		self.__Data: dict[str, dict[str | None] | list[str]] = {
			"slots": data.get("slots") or dict(),
			"free": data.get("free") or list()
		}

		if bool(note.table.manifest.attachments.rule): os.makedirs(self.__Note.table.get_path() / ".attachments", exist_ok = True)

	def attach(self, file: Path, slot: str | None = None):
		"""
		Прикрепляет файл к записи.

		:param file: Путь к файлу.
		:type file: Path
		:param slot: Имя слота. 
		:type slot: str | None
		:raises AttachmentSlotAlreadyFilled: Слот уже содержит файл.
		"""

		if slot:
			if self.get_slot_file(slot): raise Exceptions.Note.AttachmentSlotAlreadyFilled(slot)
			self.__Data["slots"][slot] = file.name

		else: self.__Data["free"] = file.name

		os.replace(file, self.__Note.table.get_path() / ".attachments" / file.name)
		self.__Note.save()

	def clear_slot(self, slot: str):
		"""
		Очищает слот.

		:param slot: Имя слота.
		:type slot: str
		:raises KeyError: Слот отсутствует.
		"""

		del self.__Data["slots"][slot]
		self.__Note.save()

	def get_slot_file(self, slot: str) -> str | None:
		"""
		Возвращает имя вложения, находящегося в слоте.

		:param slot: Имя слота.
		:type slot: str
		:return: Имя вложения в слоте.
		:rtype: str | None
		:raises KeyError: Слот отсутствует.
		"""

		if slot not in self.__Data["slots"]: raise KeyError(slot)

		return self.__Data["slots"][slot]

	def is_slot_occupied(self, slot: str) -> bool:
		"""
		Проверяет, занят ли слот вложением.

		:param slot: Имя слота.
		:type slot: str
		:return: Возвращает `True`, если слот содержит вложение.
		:rtype: bool
		"""

		try: return bool(self.get_slot_file(slot))
		except KeyError: return False

	def move(self, new_id: int):
		"""
		Перемещает вложения в каталог соответствующий новому ID записи.

		:param new_id: Новый ID записи.
		:type new_id: int
		"""

		if self.count > 0:
			OldAttachmentsPath = self.__Note.table.get_path() / ".attachments" / str(self.__Note.id)
			NewAttachmentsPath =  self.__Note.table.get_path() / ".attachments" / str(new_id)
			shutil.move(OldAttachmentsPath, NewAttachmentsPath)

	def to_dict(self, copy: bool = True) -> dict[str, dict[str | None] | list[str]]:
		"""
		Возвращает словарное представление данных вложений.

		:param copy: Указывает, нужно ли вернуть копию внутреннего словаря или оригинал.
		:type copy: bool
		:return: Словарное представление данных вложений.
		:rtype: dict[str, dict[str | None] | list[str]]
		"""

		return Copy(self.__Data) if copy else self.__Data

	def unnatach(self, filename: str):
		"""
		Удаляет вложение по имени.

		:param filename: Имя вложения.
		:type filename: str
		:raises FileNotFoundError: Вложение не найдено.
		"""

		os.remove(self.__Note.table.get_path() / ".attachments" / filename)
		if self.get_slot_file(filename): self.clear_slot(filename)
		else: self.__Data["free"].remove(filename)
		self.__Note.save()