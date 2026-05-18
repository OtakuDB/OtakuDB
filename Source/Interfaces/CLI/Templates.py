from prettytable import PLAIN_COLUMNS, PrettyTable
from dublib.CLI.TextStyler import FastStyler

#==========================================================================================#
# >>>>> ШАБЛОНЫ МЕТОДОВ ВВОДА-ВЫВОДА <<<<< #
#==========================================================================================#

def PrintTable(columns: dict[str, list], sort_by: str = "ID", reverse: bool = False):
	"""
	Выводит таблицу.

	:param columns: Словарь, в которором ключи – названия колнок, а значения – списки значений.
	:type columns: dict[str, list]
	:param sort_by: Указывает название колонки, по которой идёт сортировка.
	:type sort_by: str
	:param reverse: Переключает реверсирование отображаемого контента.
	:type reverse: bool
	"""

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
	TableObject.sortby = FastStyler(sort_by).decorate.bold
	print(TableObject)