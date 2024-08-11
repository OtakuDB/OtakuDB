from dublib.CLI.StyledPrinter import Styles, TextStyler
from prettytable import PLAIN_COLUMNS, PrettyTable
from pick import pick

#==========================================================================================#
# >>>>> ШАБЛОНЫ МЕТОДОВ ВВОДА-ВЫВОДА <<<<< #
#==========================================================================================#

def Columns(columns: dict[str, list], sort_by: str = "ID", reverse: bool = False):
	TableObject = PrettyTable()
	TableObject.set_style(PLAIN_COLUMNS)

	for ColumnName in columns.keys():
		Buffer = TextStyler(ColumnName, decorations = [Styles.Decorations.Bold])
		TableObject.add_column(Buffer, columns[ColumnName])

	TableObject.align = "l"
	TableObject.reversesort = reverse
	TableObject.sort_key = lambda x: 0 if x[0] == "" else x[0]
	TableObject.sortby = TextStyler(sort_by, decorations = [Styles.Decorations.Bold])
	print(TableObject)

def Pick(title: str, variants: list[int, str], indicator: str = ">", default_index: int = 0):
	"""
	Предлагает пользователю выбрать один из предложенных вариантов.
		title – описание запроса;\n
		variants – список вариантов.
	"""

	Variant, Index = pick(variants, title, indicator = indicator, default_index = default_index)

	return variants[Index]