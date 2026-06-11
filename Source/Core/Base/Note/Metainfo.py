from Source.Core import Exceptions

from dublib.Methods.Data import Copy, RemoveRecurringSubstrings, ToIterable

from typing import TYPE_CHECKING

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
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckMetainfoValue(self, field: str, value: int | float | str | None):
		"""
		Проверяет, подходят ли метаданные под правила фильтрации.

		:param field: Имя поля метаданных.
		:type field: str
		:param value: Значение.
		:type value: int | float | str | None
		:raise MetainfoBlocked: Невозможно задать метаданные.
		"""

		if not self.__Note.table.manifest.metainfo_rules.is_free_allowed and field not in self.__Note.table.manifest.metainfo_rules.fields_names:
			raise Exceptions.Note.MetainfoBlocked()
		
		FieldParameters = self.__Note.table.manifest.metainfo_rules.get_field_parameters(field)
		if not FieldParameters.values: return
		if value not in FieldParameters.values: raise Exceptions.Note.MetainfoBlocked()

	def __NormalizeString(self, value: str, separator: str | None = ";") -> str | tuple[str, ...]:
		"""
		Удаляет из строки повторяющиеся пробелы и разбивает её по вхождению символа `;`.

		:param value: Обрабатываемое значение.
		:type value: str
		:param separator: Разделитель подстрок, используемый для формирования из строки набора значений по вхождению символа.
		:type separator: str | None
		:return: Результат обработки.
		:rtype: str | tuple[str, ...]
		"""

		value = RemoveRecurringSubstrings(value, " ")
		value = value.strip()
		if separator and separator in value: value = tuple(Element.strip() for Element in value.split(separator))

		return value

	def __TryParseNumber(self, value: str) -> int | float | str:
		"""
		Пробует преобразовать строку в число.

		:param value: Обрабатываемое значение.
		:type value: str
		:return: Число или исходная строка.
		:rtype: int | float | str
		"""

		value = value.strip()
		if value.count("-") <= 1 and value.count(".") == 1 and value.replace(".", "").lstrip("-").isdigit(): return float(value)
		if value.count("-") <= 1 and value.lstrip("-").isdigit(): return int(value)

		return value

	def __ValidateData(self, data: dict[str, int | float | str | list[str] | None]) -> dict[str, int | float | str | tuple[str, ...] | None]:
		"""
		Производит валидацию метаданных, преобразуя списки в кортежи.

		:param data: Валидируемые данные.
		:type data: dict[str, int | float | str | list[str] | None]
		:return: Данные после валидации.
		:rtype: dict[str, int | float | str | tuple[str, ...] | None]
		"""

		for Field, Value in data.items():
			if type(data[Field]) == list: data[Field] = tuple(Value)

		return data

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, note: "BaseNote", data: dict):
		"""
		Оператор метаданных.

		:param note: Запись.
		:type note: BaseNote
		:param data: Словарь метаданных.
		:type data: dict
		"""

		self.__Note = note
		self.__Data: dict[str, int | float | str | tuple[str, ...] | None] = self.__ValidateData(data)

		self.__MetainfoRules = self.__Note.table.manifest.metainfo_rules

	def __getitem__(self, field: str) -> int | float | str | tuple[str, ...] | None:
		"""
		Возвращает значение поля метаданных.

		:param field: Имя поля.
		:type field: str
		:return: Значение поля метаданых.
		:rtype: int | float | str | tuple[str, ...] | None
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		"""

		return self.get_field_value(field, exception = False)

	def append_to_field(self, field: str, value: str | tuple[str, ...], separator: str | None = ";"):
		"""
		Добавляет строку или набор строк в поле, содержащее строку, набор строк или являющееся пустым.

		:param field: Имя поля.
		:type field: str
		:param value: Одна строка или набор.
		:type value: str | tuple[str, ...]
		:param separator: Разделитель подстрок, используемый для формирования из строки набора значений по вхождению символа.
		:type separator: str | None
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		:raises ValueError: Неверный тип значения.
		"""

		if type(value) == tuple: value = list(value)
		elif type(value) == str:
			value = self.__NormalizeString(value, separator)
			if type(value) == tuple: value = list(value)
			else: value = [value]
		else: raise ValueError("Value isn't str or tuple type.")

		FieldValue = self.get_field_value(field, exception = True)
		if FieldValue is None: FieldValue = list()
		elif type(FieldValue) == str: FieldValue = [FieldValue]
		elif type(FieldValue) == tuple: FieldValue = list(FieldValue)
		else: raise ValueError(f"Field \"{field}\" has non-string and non-sequence value.")

		self.set_field_value(field, tuple(FieldValue + value))

	def clear_field(self, field: str, exception: bool = True):
		"""
		Очищает поле метаданных и удаляет его ключ из записи.

		:param field: Имя поля.
		:type field: str
		:param exception: Указывает, выбрасывать ли исключения при отсутствии поля.
		:type exception: bool
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		"""

		if exception and field not in self.__MetainfoRules.fields_names: raise Exceptions.Note.MetainfoFieldNotDescribed(field)

		try:
			del self.__Data[field]
			self.__Note.save()

		except KeyError: pass

	def get_field_value(self, field: str, exception: bool = True) -> int | float | str | tuple[str, ...] | None:
		"""
		Возвращает значение поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param exception: Указывает, выбрасывать ли исключения при отсутствии поля.
		:type exception: bool
		:return: Значение поля метаданых.
		:rtype: int | float | str | tuple[str, ...] | None
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		"""
		
		if exception and field not in self.__MetainfoRules.fields_names: raise Exceptions.Note.MetainfoFieldNotDescribed(field)

		return self.__Data.get(field)

	def remove_from_field(self, field: str, value: str | tuple[str, ...], separator: str | None = ";"):
		"""
		Удаляет строку или набор строк из поля, содержащего строку или набор строк.

		:param field: Имя поля.
		:type field: str
		:param value: Одна строка или набор.
		:type value: str | tuple[str, ...]
		:param separator: Разделитель подстрок, используемый для формирования из строки набора значений по вхождению символа.
		:type separator: str | None
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		:raises ValueError: Неверный тип значения.
		"""

		if type(value) == str:
			value = self.__NormalizeString(value, separator)
			value = ToIterable(value)
		elif type(value) != tuple: raise ValueError("Value isn't str or tuple type.")

		FieldValue = self.get_field_value(field, exception = True)
		if type(FieldValue) == str: FieldValue = [FieldValue]
		elif type(FieldValue) == tuple: FieldValue = list(FieldValue)
		else: raise ValueError(f"Field \"{field}\" has non-string and non-sequence value.")

		for Element in set(value): FieldValue.remove(Element)
		self.set_field_value(field, tuple(FieldValue))

	def set_field_value(self, field: str, value: int | float | str | tuple[str, ...] | None, separator: str | None = ";"):
		"""
		Задаёт значение поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param value: Значение. При передаче `None` поле удаляется.
		:type value: int | float | str | tuple[str, ...] | None
		:param separator: Разделитель подстрок, используемый для формирования из строки набора значений по вхождению символа.
		:type separator: str | None
		:raises MetainfoBlocked: Прикрепление метаданных заброкировано фильтром манифеста.
		:raises ValueError: Кортежи могут содержать только строки.
		"""

		if not self.__MetainfoRules.is_free_allowed and field not in self.__MetainfoRules.fields_names: raise Exceptions.Note.MetainfoBlocked()
	
		if value == None:
			self.clear_field(field)
			return
		
		if type(value) == str: value = self.__TryParseNumber(value)
		if type(value) in (int, float):
			self.__CheckMetainfoValue(field, value)
			self.__Data[field] = value
			self.__Note.save()
			return
		
		if type(value) == str: value = self.__NormalizeString(value, separator)
		
		value = ToIterable(value)
		value = tuple(set(value))
		for Element in value:
			if type(Element) != str: raise ValueError("Tuples can contains only strings.")
			self.__CheckMetainfoValue(field, Element)

		if len(value) == 1: value = value[0]
		self.__Data[field] = value
		self.__Note.save()

	def to_dict(self, copy: bool = True) -> dict[str, int | float | str | tuple[str, ...] | None]:
		"""
		Возвращает словарное представление метаданных.

		:param copy: Указывает, нужно ли вернуть копию внутреннего словаря или оригинал.
		:type copy: bool
		:return: Словарное представление метаданных.
		:rtype: dict[str, int | float | str | tuple[str, ...] | None]
		"""

		return Copy(self.__Data) if copy else self.__Data