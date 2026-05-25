from .Options.Local import ColumnOptions

from dublib.CLI.TextStyler import FastStyler

from typing import Iterable

from prettytable import PLAIN_COLUMNS, PrettyTable

#==========================================================================================#
# >>>>> ШАБЛОНЫ МЕТОДОВ ВВОДА-ВЫВОДА <<<<< #
#==========================================================================================#

def PrintTable(columns: dict[str, list], options: Iterable[ColumnOptions] | None = None, sort_by: str | None = None, reverse: bool = False):
	"""
	Выводит таблицу.

	:param columns: Словарь, в которором ключи – названия колнок, а значения – списки значений.
	:type columns: dict[str, list]
	:param options: Набор параметров для колонок.
	:type options: Iterable[ColumnOptions] | None
	:param sort_by: Указывает название колонки, по которой идёт сортировка.
	:type sort_by: str | None
	:param reverse: Переключает реверсирование отображаемого контента.
	:type reverse: bool
	"""

	options = options or tuple()

	TableObject = PrettyTable()
	TableObject.set_style(PLAIN_COLUMNS)
	TableObject.left_padding_width = 0
	TableObject.right_padding_width = 3

	for ColumnName in columns.keys():
		Buffer = FastStyler(ColumnName).decorate.bold
		TableObject.add_column(Buffer, columns[ColumnName])

	TableObject.align = "l"
	TableObject.reversesort = reverse
	TableObject.sort_key = lambda x: 0 if x[0] == "" else x[0]
	if sort_by: TableObject.sortby = FastStyler(sort_by).decorate.bold
	print(TableObject)