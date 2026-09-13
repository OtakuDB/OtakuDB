from dataclasses import dataclass
from typing import Literal

from .... import exceptions
from ._base import BaseSection

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

class AttachmentsSection(BaseSection):
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

		return self.__rule

	@property
	def slots(self) -> tuple[SlotParameters, ...]:
		"""Последовательность определений слотов."""

		return tuple(self.__slots.values())
	
	@property
	def slots_names(self) -> tuple[str, ...]:
		"""Последовательность имён слотов."""

		return tuple(self.__slots.keys())

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__rule: Literal[0, 1, 2] = 0
		self.__slots: dict[str, SlotParameters] = {}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def create_slot_parameters(self, slot: str, description: str | None):
		"""
		Резервирует слот вложений для особого взаимодействия.

		:param slot: Название слота.
		:type slot: str
		:param description: Описание слота.
		:type description: str | None
		:raises AttachmentSlotAlreadyDescribedError: Слот уже описан.
		"""

		if slot in self.__slots: raise exceptions.note.AttachmentSlotAlreadyDescribedError(slot)
		self.__slots[slot] = SlotParameters(slot, description)

	def get_slot_parameters(self, slot: str) -> SlotParameters:
		"""
		Возвращает описание слота.

		:param slot: Имя слота.
		:type slot: str
		:return: Параметры слота.
		:rtype: SlotParameters
		:raises AttachmentSlotNotDescribed: Слот не описан.
		"""

		if slot not in self.__slots:
			raise exceptions.note.AttachmentSlotNotDescribedError(slot)

		return self.__slots[slot]

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.set_attachments_rule(data["rule"])
		self.__slots.clear()
		slots_data: dict = data.get("slots", {})

		for slot, description in slots_data.items():
			self.create_slot_parameters(slot, description)

	def remove_slot_parameters(self, slot: str):
		"""
		Удаляет слот вложений.

		:param slot: Имя слота.
		:type slot: str
		:raises AttachmentSlotNotDescribed: Слот не описан.
		"""

		if slot not in self.__slots: raise exceptions.note.AttachmentSlotAlreadyDescribedError(slot)
		del self.__slots[slot]

	def set_attachments_rule(self, rule: Literal[0, 1, 2]):
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

		if rule not in (0, 1, 2): raise ValueError("Rule must be between 0 and 2.")
		self.__rule = rule

	def to_dict(self) -> dict[str, int | dict]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, int | dict]
		"""

		return {
			"rule": self.__rule,
			"slots": {slot.name: slot.description for slot in self.__slots.values()}
		}
