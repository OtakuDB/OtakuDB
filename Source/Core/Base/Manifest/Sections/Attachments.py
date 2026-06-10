from ._BaseSection import BaseSection

from Source.Core import Exceptions

from dataclasses import dataclass
from typing import Literal

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class SlotParameters:
	"""Параметры слота."""

	name: str
	description: str | None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class AttachmentsParameters(BaseSection):
	"""Параметры вложений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def rule(self) -> int:
		"""
		Правило использования вложений.
		
		* 0 – запрещены все всложения;
		* 1 – разрешены только слоты;
		* 2 – разрешены все вложения.
		"""

		return self.__Rule

	@property
	def slots(self) -> tuple[SlotParameters, ...]:
		"""Последовательность определений слотов."""

		return tuple(self.__Slots.values())
	
	@property
	def slots_names(self) -> tuple[str, ...]:
		"""Последовательность имён слотов."""

		return tuple(self.__Slots.keys())

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Rule = 0
		self.__Slots: dict[str, SlotParameters] = dict()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def create_slot_parameters(self, slot: str, description: str | None, save: bool = True):
		"""
		Резервирует слот вложений для особого взаимодействия.

		:param slot: Название слота.
		:type slot: str
		:param description: Описание слота.
		:type description: str | None
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises AttachmentSlotAlreadyDescribed: Слот уже описан.
		"""

		if slot in self.__Slots: raise Exceptions.Note.AttachmentSlotAlreadyDescribed(slot)
		self.__Slots[slot] = SlotParameters(slot, description)
		if save: self.save()

	def get_slot_parameters(self, slot: str) -> SlotParameters:
		"""
		Возвращает описание слота.

		:param slot: Имя слота.
		:type slot: str
		:return: Параметры слота.
		:rtype: SlotParameters
		:raises AttachmentSlotNotDescribed: Слот не описан.
		"""

		if slot not in self.__Slots: raise Exceptions.Note.AttachmentSlotNotDescribed(slot)

		return self.__Slots[slot]

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.set_attachments_rule(data["rule"], save = False)
		self.__Slots = dict()
		SlotsData = data.get("slots") or dict()
		for Slot, Description in SlotsData.items(): self.create_slot_parameters(Slot, Description, save = False)

	def remove_slot_parameters(self, slot: str, save: bool = True):
		"""
		Удаляет слот вложений.

		:param slot: Имя слота.
		:type slot: str
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises AttachmentSlotNotDescribed: Слот не описан.
		"""

		if slot not in self.__Slots: raise Exceptions.Note.AttachmentSlotNotDescribed(slot)
		del self.__Slots[slot]
		if save: self.save()

	def set_attachments_rule(self, rule: Literal[0, 1, 2], save: bool = True):
		"""
		Задаёт правило использования вложений.
		
		* 0 – запрещены все всложения;
		* 1 – разрешены только слоты;
		* 2 – разрешены все вложения.

		:param rule: Индекс правила использования вложений.
		:type rule: Literal[0, 1, 2]
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises ValueError: Индекс правила выходит за пределы диапазона.
		"""

		if rule not in (0, 1, 2): raise ValueError(f"Rule must be between 0 and 2.")
		self.__Rule = rule
		if save: self.save()

	def to_dict(self) -> dict[str, int | dict]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, int | dict]
		"""

		return {
			"rule": self.__Rule,
			"slots": {Slot.name: Slot.description for Slot in self.__Slots.values()}
		}
