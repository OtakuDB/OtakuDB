from ._BaseSection import BaseSection

from Source.Core import Exceptions

from dublib.Methods.Data import ToSequence

from dataclasses import dataclass
from typing import Iterable

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class MetainfoFieldParameters:
	"""Параметры поля метаданных."""

	name: str
	types: tuple[type, ...] | None
	allow_list: bool
	values: tuple[int | float | str, ...] | None
	description: str | None

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		Values = self.values
		if Values != None and len(Values) == 1: Values = Values[0]

		return {
			"types": tuple(CurrentType.__name__ for CurrentType in self.types) if self.types else None,
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

		return self.__IsFreeAllowed
	
	@property
	def fields(self) -> tuple[MetainfoFieldParameters, ...]:
		"""Последовательность параметров полей метаданных."""

		return tuple(self.__Fields.values())

	@property
	def fields_names(self) -> tuple[str, ...]:
		"""Последовательность имён описанных полей метаданных."""

		return tuple(self.__Fields.keys())
	
	@property
	def rule(self) -> int:
		"""
		Правило использования метаданных.
		
		* 0 – запрещены все метаданные;
		* 1 – разрешены только определённые поля метаданных;
		* 2 – разрешены все метаданные.
		"""

		if not all((self.__IsFreeAllowed, self.__Fields)): return 0
		elif not self.__IsFreeAllowed: return 1
		else: return 2

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseFields(self, data: dict[str, dict]) -> dict[str, MetainfoFieldParameters]:
		"""
		Парсит словарь данных полей в объектные представления.

		:param data: Словарь данных.
		:type data: dict
		:return: Словарь параметров полей метаданных.
		:rtype: dict[str, MetainfoFieldParameters]
		"""
		
		FieldsData = dict()

		for Field, Parameters in data.items():
			Types = Parameters.get("types")
			if Types: Types = self.__ParseTypesString(Types)

			AllowList = bool(Parameters.get("allow_list"))

			Values = Parameters.get("values")
			if Values != None: Values = ToSequence(Values)

			Description = Parameters.get("description")
			
			FieldsData[Field] = MetainfoFieldParameters(Field, Types, AllowList, Values, Description)

		return FieldsData
	
	def __ParseTypesString(self, string: str) -> tuple[type, ...]:
		"""
		Парсит допустимые типы из строковых представлений.

		:param string: Обрабатываемая строка, в которой типы разделены символом `;`. Поддерживаются `float`, `int`, `str`.
		:type string: str
		:return: Последовательность поддерживаемых типов.
		:rtype: tuple[type, ...]
		:raises TypeError: Указан неподдерживаемый тип.
		"""

		Determinations = {Type.__name__: Type for Type in (float, int, str)}
		TypesStrings = tuple(String.strip() for String in string.split(";"))
		Result = list()

		for TypeString in TypesStrings:
			if TypeString not in Determinations: raise TypeError(f"Unsupported type \"{TypeString}\".")
			Result.append(Determinations[TypeString])

		return tuple(Result)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__IsFreeAllowed = False
		self.__Fields: dict[str, MetainfoFieldParameters] = dict()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def create_field_parameters(
			self,
			field: str,
			types: type | Iterable[type] | None = None,
			allow_list: bool = False,
			values: Iterable[int | float | str] | None = None,
			description: str | None = None,
			save: bool = True
		):
		"""
		Создаёт параметры поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param types: Допустимые в поле типы данных.
		:type types: type | Iterable[type] | None
		:param allow_list: Указывает, разрешено ли помещать в поле несколько значений.
		:type allow_list: bool
		:param values: Последовательность принимаемых значений или `None` для любого.
		:type values: Iterable[int | float | str] | None
		:param description: Описание поля.
		:type description: str | None
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		"""

		if types: types = ToSequence(types)
		self.__Fields[field] = MetainfoFieldParameters(field, types, allow_list, values, description)
		if save: self.save()

	def get_field_parameters(self, field: str) -> MetainfoFieldParameters:
		"""
		Возвращает параметры поля метаданных.

		:param field: Имя поля.
		:type field: str
		:return: Параметры поля.
		:rtype: MetainfoFieldParameters
		:raises MetainfoFieldNotDescribed: Данные поля не найдены.
		"""

		if field not in self.__Fields: raise Exceptions.Note.MetainfoFieldNotDescribed(field)

		return self.__Fields[field]

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__IsFreeAllowed = bool(data.get("allow_free"))
		self.__Fields: dict[str, MetainfoFieldParameters] = self.__ParseFields(data.get("fields") or dict())

	def remove_field_parameters(self, field: str, save: bool = True):
		"""
		Удаляет параметры поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		"""

		if field not in self.__Fields: raise Exceptions.Note.MetainfoFieldNotDescribed(field)
		del self.__Fields[field]
		if save: self.save()

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return {
			"allow_free": self.__IsFreeAllowed,
			"fields": {FieldData.name: FieldData.to_dict() for FieldData in self.__Fields.values()}
		}
