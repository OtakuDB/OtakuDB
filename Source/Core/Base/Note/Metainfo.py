from Source.Core import Exceptions

from dublib.Methods.Data import Copy, RemoveRecurringSubstrings, ToSequence
from dublib.CLI.Validators import Validator_Number

from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:
	from . import BaseNote

class Metainfo:
	"""Оператор метаданных."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def fields(self) -> tuple[str, ...]:
		"""Последовательность имён доступных полей метаданных."""

		return tuple(self.__Data.keys())
	
	@property
	def has_values(self) -> bool:
		"""Состояние: заполнено ли хотя бы одно поле метаданных."""

		Values = self.__Data.values()

		return any(Values) if Values else False

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ ВАЛИДАЦИИ <<<<< #
	#==========================================================================================#

	def __CheckValueTyping(self, field: str, value: float | int | list | str | None):
		"""
		Проверяет, имеет ли значение корректный тип.

		:param field: Имя поля метаданных.
		:type field: str
		:param value: Значение.
		:type value: value: float | int | list | str | None
		:raises MetainfoFieldEnlistingDenied: Использование списков в поле метаданных запрещено.
		"""
		
		value = ToSequence(value, target_type = list)
		FieldParameters = self.__Note.table.manifest.metainfo_rules.get_field_parameters(field)
		
		if not FieldParameters.allow_list:
			if len(value) > 1: raise Exceptions.Note.MetainfoFieldEnlistingDenied(field)

		if FieldParameters.types:
			for Element in value:
				ElementType = type(Element)
				if ElementType not in FieldParameters.types: raise Exceptions.Note.MetainfoFieldIncorrectTyping(field, ElementType, FieldParameters.types)

	def __NormalizeString(self, value: str, separator: str | None = ";") -> str | list[str]:
		"""
		Удаляет из строки повторяющиеся пробелы и разбивает её по вхождению символа `;`.

		:param value: Обрабатываемое значение.
		:type value: str
		:param separator: Разделитель подстрок, используемый для формирования из строки набора значений по вхождению символа.
		:type separator: str | None
		:return: Результат обработки.
		:rtype: str | list[str, ...]
		"""

		Value = RemoveRecurringSubstrings(value, " ")
		Value = Value.strip()
		if separator and separator in Value: Value = list(Element.strip() for Element in Value.split(separator))

		return Value

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, note: "BaseNote", data: dict[str, float | int | list | str | None]):
		"""
		Оператор метаданных.

		:param note: Запись.
		:type note: BaseNote
		:param data: Словарь метаданных.
		:type data: dict[str, float | int | list | str | None]
		"""

		self.__Note = note
		self.__Data: dict[str, float | int | list | str | None] = data.copy()

		self.__MetainfoRules = self.__Note.table.manifest.metainfo_rules

	def __getitem__(self, field: str) -> float | int | list | str | None:
		"""
		Возвращает значение поля метаданных.

		:param field: Имя поля.
		:type field: str
		:return: Значение поля метаданых.
		:rtype: float | int | list | str | None
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		"""

		return self.get_field_value(field)

	def clear_field(self, field: str):
		"""
		Очищает поле метаданных и удаляет его ключ из записи.

		:param field: Имя поля.
		:type field: str
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		"""

		if field not in self.__MetainfoRules.fields_names:
			raise Exceptions.Note.MetainfoFieldNotDescribed(field)

		try:
			del self.__Data[field]
			self.__Note.save()

		except KeyError: pass

	def get_field_value(self, field: str) -> float | int | list | str | None:
		"""
		Возвращает значение поля метаданных.

		:param field: Имя поля.
		:type field: str
		:return: Значение поля метаданых.
		:rtype: float | int | list | str | None
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		"""
		
		if field not in self.__MetainfoRules.fields_names: raise Exceptions.Note.MetainfoFieldNotDescribed(field)

		return self.__Data.get(field)

	def set_field_value(self, field: str, value: float | int | list | str | None):
		"""
		Задаёт значение поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param value: Значение. При передаче `None` поле удаляется.
		:type value: float | int | list | str | None
		:raises MetainfoBlocked: Поле метаданных не описано и свободный режим отключён.
		:raises ValueError: Кортежи могут содержать только строки.
		"""

		if not self.__MetainfoRules.is_free_allowed and field not in self.__MetainfoRules.fields_names: raise Exceptions.Note.MetainfoBlocked()

		if value is None:
			self.clear_field(field)
			return
		
		if type(value) is str:
			value = value.strip()
			if Validator_Number.validate(value): value = Validator_Number.convert(value)
		
		if type(value) in (int, float):
			self.__CheckValueTyping(field, value)
			self.__Data[field] = value
			self.__Note.save()
			return
		
		if type(value) is str:
			value = self.__NormalizeString(value)
		
		value = list(set(ToSequence(value)))
		for Element in value:
			if type(Element) is not str: raise ValueError("Lists can contains only strings.")
			self.__CheckValueTyping(field, Element)

		if len(value) == 1: value = value[0]
		self.__Data[field] = value
		self.__Note.save()

	def append_to_field(self, field: str, value: str | Sequence[str], separator: str | None = ";"):
		"""
		Добавляет строку или список строк в поле, содержащее строку, список строк или являющееся пустым.

		:param field: Имя поля.
		:type field: str
		:param value: Одна строка или список.
		:type value: str | tuple[str, ...]
		:param separator: Разделитель подстрок, используемый для формирования из строки списка значений по вхождению символа.
		:type separator: str | None
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		:raises ValueError: Неверный тип значения.
		"""

		value = ToSequence(value, target_type = list)
		if len(value) == 1: value = value[0]

		if type(value) is str:
			value = self.__NormalizeString(value, separator)
			value = ToSequence(value, target_type = list)
		else:
			raise ValueError("Value isn't str or tuple type.")

		FieldValue = self.get_field_value(field)

		if FieldValue is None: FieldValue = list()
		elif type(FieldValue) is str: FieldValue = [FieldValue]
		else: raise ValueError(f"Field \"{field}\" has non-string and non-sequence value.")

		self.set_field_value(field, FieldValue + value)

	def remove_from_field(self, field: str, value: str | Sequence[str], separator: str | None = ";"):
		"""
		Удаляет строку или набор строк из поля, содержащего строку или набор строк.

		:param field: Имя поля.
		:type field: str
		:param value: Одна строка или набор.
		:type value: str | Sequence[str]
		:param separator: Разделитель подстрок, используемый для формирования из строки набора значений по вхождению символа.
		:type separator: str | None
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		:raises ValueError: Неверный тип значения.
		"""

		if type(value) is str:
			value = self.__NormalizeString(value, separator)
			value = ToSequence(value)
		elif type(value) is not list:
			raise ValueError("Value isn't str or list type.")

		FieldValue = self.get_field_value(field)

		if type(FieldValue) is str:
			FieldValue = [FieldValue]
		else:
			raise ValueError(f"Field \"{field}\" has non-string and non-sequence value.")

		for Element in set(value): FieldValue.remove(Element)
		self.set_field_value(field, FieldValue)

	def to_dict(self, copy: bool = True) -> dict:
		"""
		Возвращает словарное представление метаданных.

		:param copy: Указывает, нужно ли вернуть копию внутреннего словаря или оригинал.
		:type copy: bool
		:return: Словарное представление метаданных.
		:rtype: dict
		"""

		return Copy(self.__Data) if copy else self.__Data