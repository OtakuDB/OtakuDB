from Source.Core import Exceptions

from dataclasses import dataclass
from typing import TYPE_CHECKING
from pathlib import Path
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
	file: str

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

		return len(self.__Data["slots"]) + len(self.__Data["free"])

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

	def __init__(self, directory: Path, note: "BaseNote", data: dict):
		"""
		Оператор вложений.

		:param directory: Полный путь к директории таблицы.
		:type directory: Path
		:param note: Запись.
		:type note: BaseNote
		:param data: Словарь данных вложений.
		:type data: dict
		"""

		self.__Directory = directory
		self.__Note = note
		self.__Data: dict[str, dict | list] = {
			"slots": data.get("slots") or dict(),
			"free": data.get("free") or list()
		}

		self.__AttachmentsDirectory = self.__Directory / ".attachments"
		if bool(note.table.manifest.attachments.rule): os.makedirs(self.__AttachmentsDirectory, exist_ok = True)

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

		os.replace(file, self.__AttachmentsDirectory / file.name)
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

	def unnatach(self, filename: str):
		"""
		Удаляет вложение по имени.

		:param filename: Имя вложения.
		:type filename: str
		:raises FileNotFoundError: Вложение не найдено.
		"""

		os.remove(self.__AttachmentsDirectory / filename)
		if self.get_slot_file(filename): self.clear_slot(filename)
		else: self.__Data["free"].remove(filename)
		self.__Note.save()