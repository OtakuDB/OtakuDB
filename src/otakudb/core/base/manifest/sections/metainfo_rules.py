from dataclasses import dataclass
from typing import Sequence

from dublib.functions.data import to_sequence

from .... import exceptions
from ._base import BaseSection

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class MetainfoFieldParameters:
	"""Параметры поля метаданных."""

	name: str
	types: tuple[type[float | int | str], ...] | None
	allow_list: bool
	values: tuple[float | int | str, ...] | None
	description: str | None

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		Values = self.values
		if Values is not None and len(Values) == 1: Values = Values[0]

		return {
			"types": ";".join(CurrentType.__name__ for CurrentType in self.types) if self.types else None,
			"allow_list": self.allow_list,
			"values": Values,
			"description": self.description
		}

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class MetainfoRules(BaseSection):
	"""Правила метаданных."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_free_allowed(self) -> bool:
		"""Состояние: разрешены ли неопределённые в правилах поля метаданных."""

		return self.__is_free_allowed
	
	@property
	def fields_parameters(self) -> tuple[MetainfoFieldParameters, ...]:
		"""Последовательность параметров полей метаданных."""

		return tuple(self.__fields.values())

	@property
	def fields_names(self) -> tuple[str, ...]:
		"""Последовательность имён описанных полей метаданных."""

		return tuple(self.__fields.keys())
	
	@property
	def rule(self) -> int:
		"""
		Правило использования метаданных.
		
		* 0 – запрещены все метаданные;
		* 1 – разрешены только определённые поля метаданных;
		* 2 – разрешены все метаданные.
		"""

		if not all((self.__is_free_allowed, self.__fields)): return 0
		elif not self.__is_free_allowed: return 1
		
		return 2

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __parse_fields_parameters(self, data: dict[str, dict]) -> dict[str, MetainfoFieldParameters]:
		"""
		Парсит словарь данных полей в объектные представления.

		:param data: Словарь данных.
		:type data: dict
		:return: Словарь параметров полей метаданных.
		:rtype: dict[str, MetainfoFieldParameters]
		"""
		
		fields_parameters: dict = {}

		for name, parameters in data.items():
			types: str | None = parameters.get("types")
			is_allow_list: bool = bool(parameters.get("allow_list"))
			values: list | None = parameters.get("values")
			description: str | None = parameters.get("description")

			fields_parameters[name] = MetainfoFieldParameters(
				name = name,
				types = self.__parse_field_types(types) if types else None,
				allow_list = is_allow_list,
				values = to_sequence(values) if values else (),
				description = description
			)

		return fields_parameters
	
	def __parse_field_types(self, string: str) -> tuple[type[float | int | str], ...]:
		"""
		Парсит допустимые типы из строковых представлений.

		:param string: Обрабатываемая строка, в которой типы разделены символом `;`. Поддерживаются `float`, `int`, `str`.
		:type string: str
		:return: Последовательность поддерживаемых типов.
		:rtype: tuple[type[float | int | str], ...]
		:raises TypeError: Указан неподдерживаемый тип.
		"""

		determinations: dict[str, type[float | int | str]] = {value_type.__name__: value_type for value_type in (float, int, str)}
		types_strings: tuple[str, ...] = tuple(part.strip() for part in string.split(";"))
		result: list[type[float | int | str]] = []

		for part in types_strings:

			if part not in determinations:
				raise TypeError(f"Unsupported type \"{part}\".")

			result.append(determinations[part])

		return tuple(result)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__is_free_allowed = bool(data.get("allow_free"))
		self.__fields = self.__parse_fields_parameters(data.get("fields", {}))

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__is_free_allowed: bool = False
		self.__fields: dict[str, MetainfoFieldParameters] = {}

	def _to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return {
			"allow_free": self.__is_free_allowed,
			"fields": {field.name: field.to_dict() for field in self.__fields.values()}
		}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def create_field_parameters(
			self,
			field: str,
			types: type[float | int | str] | Sequence[type[float | int | str]] | None = None,
			allow_list: bool = False,
			values: Sequence[int | float | str] | None = None,
			description: str | None = None
		):
		"""
		Создаёт параметры поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param types: Допустимые в поле типы данных.
		:type types: type[float | int | str] | Sequence[type[float | int | str]] | None
		:param allow_list: Указывает, разрешено ли помещать в поле несколько значений.
		:type allow_list: bool
		:param values: Последовательность принимаемых значений или `None` для любого.
		:type values: Sequence[int | float | str] | None
		:param description: Описание поля.
		:type description: str | None
		"""

		self.__fields[field] = MetainfoFieldParameters(
			name = field,
			types = to_sequence(types) if types else None,
			allow_list = allow_list,
			values = tuple(values) if values else None,
			description = description
		)

	def get_field_parameters(self, field: str) -> MetainfoFieldParameters:
		"""
		Возвращает параметры поля метаданных.

		:param field: Имя поля.
		:type field: str
		:return: Параметры поля.
		:rtype: MetainfoFieldParameters
		:raises MetainfoFieldNotFoundError: Данные поля не найдены.
		"""

		if field not in self.__fields:
			raise exceptions.note.metainfo.MetainfoFieldNotFoundError(field)

		return self.__fields[field]

	def remove_field_parameters(self, field: str):
		"""
		Удаляет параметры поля метаданных.

		:param field: Имя поля.
		:type field: str
		:raises MetainfoFieldNotFoundError: Поле метаданных не описано.
		"""

		if field not in self.__fields:
			raise exceptions.note.metainfo.MetainfoFieldNotFoundError(field)

		del self.__fields[field]
