from dublib.CLI.StyledPrinter import StyledPrinter, Styles, TextStyler
from prettytable import PLAIN_COLUMNS, PrettyTable

#==========================================================================================#
# >>>>> ШАБЛОНЫ МЕТОДОВ ВВОДА-ВЫВОДА <<<<< #
#==========================================================================================#

def Columns(columns: dict[str, list], sort_by: str = "ID", reverse: bool = False):
	# Инициализация таблицы.
	TableObject = PrettyTable()
	TableObject.set_style(PLAIN_COLUMNS)

	# Для каждого столбца.
	for ColumnName in columns.keys():
		# Буфер стилизации названия колонки.
		Buffer = TextStyler(ColumnName, decorations = [Styles.Decorations.Bold])
		# Парсинг столбца.
		TableObject.add_column(Buffer, columns[ColumnName])

	# Установка стилей таблицы.
	TableObject.align = "l"
	TableObject.reversesort = reverse
	TableObject.sort_key = lambda x: 0 if x[0] == "" else x[0]
	TableObject.sortby = TextStyler(sort_by, decorations = [Styles.Decorations.Bold])
	# Вывод таблицы.
	print(TableObject)

def Error(error_type: str, description: str | None = None):
	"""
	Выводит в терминал сообщение об ошибке.
		error_type – тип ошибки;
		description – описание ошибки.
	"""
	
	# Генерация описания.
	description = f" - {description}" if type(description) == str else ""
	# Вывод в консоль: ошибка.
	StyledPrinter(f"ERROR: {error_type}{description}", text_color = Styles.Colors.Red)