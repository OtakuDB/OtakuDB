from typing import TYPE_CHECKING, Sequence

from dublib.functions.data import deep_copy, to_sequence
from dublib.functions.data.dictionary import deep_merge
from dublib.functions.data.string import remove_recurring_substrings
from dublib.validators import types

from otakudb.core import exceptions

if TYPE_CHECKING:
	from ..manifest.sections.metainfo_rules import MetainfoRules
	from . import BaseNote

type SupportedTypes = float | int | str

class Metainfo[N: "BaseNote" = "BaseNote"]:
	"""Metainfo operator."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def fields(self) -> tuple[str, ...]:
		"""Последовательность имён доступных полей метаданных."""

		return tuple(self.__data.keys())
	
	@property
	def has_values(self) -> bool:
		"""Condition: is at least one field filled."""

		values = self.__data.values()

		return any(values) if values else False

	#==========================================================================================#
	# >>>>> PRIVATE METHODS <<<<< #
	#==========================================================================================#

	def __parse_value(self, value: Sequence | SupportedTypes, separator: str | None = ";") -> tuple[SupportedTypes, ...]:
		"""
		Parse field value.

		:param value: Field value.
		:type value: Sequence | SupportedTypes
		:param separator: By this separator strings will be splitted.
		:type separator: str | None
		:return: Parsed field values.
		:rtype: tuple[SupportedTypes, ...]
		"""

		if isinstance(value, float | int):
			return (value,)

		value_sequence: list = []

		if isinstance(value, str):
			value = remove_recurring_substrings(value, " ")
			value = value.strip()

			if separator:
				value_sequence = [part.strip() for part in value.split(separator)]

			else:
				if types.Number.validate(value):
					value = types.Number.convert(value)

				return (value,)

		if not value_sequence:
			value_sequence = list(value)

		parsed_value_sequence: tuple[float | int | str, ...] = ()
		
		for index in range(len(value_sequence)):
			parsed_value_sequence += self.__parse_value(value_sequence[index], separator = None)
		
		return parsed_value_sequence
		
	def __validate_value(self, field_name: str, value: tuple[SupportedTypes, ...]):
		"""
		Validate value with field parameters. If field is free checking will be skipped.

		:param field_name: Field name.
		:type field_name: str
		:param value: Field value.
		:type value: tuple[SupportedTypes, ...]
		:raises MetainfoEnlistingDeniedError: Enlisting denied for matainfo field.
		:raises MetainfoTypingError: Metainfo field typing error.
		"""

		if self.is_free_field(field_name):
			return

		parameters = self.__rules.get_field_parameters(field_name)

		if not parameters.allow_list and len(value) > 1:
			raise exceptions.note.metainfo.MetainfoEnlistingDeniedError(field_name)

		if parameters.types:
			for element in value:
				element_type: type[SupportedTypes] = type(element)

				if element_type not in parameters.types:
					raise exceptions.note.metainfo.MetainfoTypingError(field_name, element_type, parameters.types)

	def __set_value(self, field_name: str, parsed_value: tuple[SupportedTypes, ...]):
		"""
		Set value into internal dictionary.

		:param field_name: Field name.
		:type field_name: str
		:param parsed_value: Field parsed value.
		:type parsed_value: tuple[SupportedTypes, ...]
		"""

		if len(parsed_value) == 1:
			self.__data[field_name] = parsed_value[0]
		else:
			self.__data[field_name] = parsed_value

		self.__note.save()

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, note: N, data: dict[str, SupportedTypes | list[SupportedTypes] | None]):
		"""
		Оператор метаданных.

		:param note: Запись.
		:type note: BaseNote
		:param data: Словарь метаданных.
		:type data: dict[str, float | int | list | str | None]
		"""

		self.__rules: "MetainfoRules" = note.table.manifest.metainfo_rules

		self.__note: N = note
		self.__data: dict[str, SupportedTypes | tuple[SupportedTypes, ...] | None] = deep_merge(
			base = dict.fromkeys(self.__rules.fields_names, None),
			content = data,
			sequences_type = tuple
		)

	def is_free_field(self, field_name: str) -> bool:
		"""
		Check if field is free.

		:param field_name: Field name.
		:type field_name: str
		:return: Return `True` if field name not found in described by manifest fields.
		:rtype: bool
		"""

		return field_name not in self.__rules.fields_names

	def clear_field(self, field_name: str):
		"""
		Clear metainfo field value. If field is free also remove field key.

		:param field_name: Field name.
		:type field_name: str
		"""

		if field_name in self.__data:
			
			if self.is_free_field(field_name):
				del self.__data[field_name]
			else:
				self.__data[field_name] = None

		self.__note.save()

	def get_field_value(self, field_name: str) -> SupportedTypes | tuple[SupportedTypes, ...] | None:
		"""
		Get metainfo field value.

		:param field_name: Field name.
		:type field_name: str
		:return: Field value.
		:rtype: SupportedTypes | tuple[SupportedTypes, ...] | None
		:raises FreeMetainfoFieldsDeniedError: Free metainfo fields denied.
		:raises MetainfoFieldNotFoundError: Metainfo field not found.
		"""

		if self.is_free_field(field_name):

			if not self.__rules.is_free_allowed:
				raise exceptions.note.metainfo.FreeMetainfoFieldsDeniedError()

			if field_name not in self.__data:
				raise exceptions.note.metainfo.MetainfoFieldNotFoundError(field_name)

		return self.__data[field_name]

	def set_field_value(self, field_name: str, value: Sequence[SupportedTypes] | SupportedTypes | None):
		"""
		Set field value.

		:param field_name: Field name.
		:type field_name: str
		:param value: Field value. If value is `None` field will be cleared.
		:type value: Sequence[SupportedTypes] | SupportedTypes | None
		:raises MetainfoBlockedError: Поле метаданных не описано и свободный режим отключён.
		:raises ValueError: Кортежи могут содержать только строки.
		"""

		is_free_metainfo: bool = field_name not in self.__rules.fields_names

		if not self.__rules.is_free_allowed and is_free_metainfo:
			raise exceptions.note.metainfo.FreeMetainfoFieldsDeniedError()

		if value is None:
			self.clear_field(field_name)
			return
		
		parsed_value: tuple[float | int | str, ...] = self.__parse_value(value)
		self.__validate_value(field_name, parsed_value)
		self.__set_value(field_name, parsed_value)

	def to_dict(self, copy: bool = True) -> dict:
		"""
		Returns a dictionary representation of object.

		:param copy: Make deep copy of internal data dictionary.
		:type copy: bool
		:return: Dictionary representation of object.
		:rtype: dict
		"""

		return deep_copy(self.__data) if copy else self.__data

	#==========================================================================================#
	# >>>>> PUBLIC FIELDS SEQUENCES MANIPULATION METHODS <<<<< #
	#==========================================================================================#

	def append_to_field(self, field_name: str, value: SupportedTypes | Sequence[SupportedTypes], separator: str | None = ";"):
		"""
		Append value(s) to field.

		:param field_name: Field name.
		:type field_name: str
		:param value: Value.
		:type value: SupportedTypes | Sequence[SupportedTypes]
		:param separator: By this separator strings will be splitted.
		:type separator: str | None
		"""

		current_value: SupportedTypes | tuple[SupportedTypes, ...] | None = self.get_field_value(field_name)
		current_value_tuple: tuple[SupportedTypes, ...] = to_sequence(current_value) if current_value else ()
		parsed_value: tuple[SupportedTypes, ...] = self.__parse_value(value, separator)
		result_value: tuple[SupportedTypes, ...] = current_value_tuple + parsed_value
		self.__validate_value(field_name, result_value)
		self.__set_value(field_name, parsed_value)

	def remove_from_field(self, field_name: str, value: SupportedTypes | Sequence[SupportedTypes], separator: str | None = ";"):
		"""
		Remove value(s) from field.

		:param field_name: Field name.
		:type field_name: str
		:param value: Value.
		:type value: SupportedTypes | Sequence[SupportedTypes]
		:param separator: By this separator strings will be splitted.
		:type separator: str | None
		"""

		current_value: SupportedTypes | tuple[SupportedTypes, ...] | None = self.get_field_value(field_name)
		current_value_list: list[SupportedTypes] = to_sequence(current_value, target_type = list) if current_value else []
		parsed_value: tuple[SupportedTypes, ...] = self.__parse_value(value, separator)

		for element in parsed_value:
			if element in current_value_list:
				index: int = current_value_list.index(element)
				current_value_list.pop(index)

		self.__set_value(field_name, tuple(current_value_list))
