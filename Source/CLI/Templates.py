from prettytable import PLAIN_COLUMNS, PrettyTable
from dublib.CLI.TextStyler import TextStyler
from pick import pick

#==========================================================================================#
# >>>>> ШАБЛОНЫ МЕТОДОВ ВВОДА-ВЫВОДА <<<<< #
#==========================================================================================#

def Columns(columns: dict[str, list], sort_by: str = "ID", reverse: bool = False):
	TableObject = PrettyTable()
	TableObject.set_style(PLAIN_COLUMNS)
	TableObject.left_padding_width = 0
	TableObject.right_padding_width = 3

	for ColumnName in columns.keys():
		Buffer = TextStyler(ColumnName).decorate.bold
		TableObject.add_column(Buffer, columns[ColumnName])

	TableObject.align = "l"
	TableObject.reversesort = reverse
	TableObject.sort_key = lambda x: 0 if x[0] == "" else x[0]
	TableObject.sortby = TextStyler(sort_by).decorate.bold
	print(TableObject)

def Pick(title: str, variants: list[int, str], indicator: str = ">", default_index: int = 0):
	"""
	Предлагает пользователю выбрать один из предложенных вариантов.
		title – описание запроса;\n
		variants – список вариантов.
	"""

	Variant, Index = pick(variants, title, indicator = indicator, default_index = default_index)

	return variants[Index]