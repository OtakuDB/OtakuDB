from dublib.StyledPrinter import StyledPrinter, Styles, TextStyler
from prettytable import PLAIN_COLUMNS, PrettyTable

#==========================================================================================#
# >>>>> ШАБЛОНЫ МЕТОДОВ ВВОДА-ВЫВОДА <<<<< #
#==========================================================================================#

def Columns(columns: dict[str, list], sort_by: str = "ID"):
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
	TableObject.sortby = TextStyler(sort_by, decorations = [Styles.Decorations.Bold])
	# Вывод таблицы.
	print(TableObject)

def Confirmation(text: str) -> bool:
	"""
	Запрашивает подтверждение.
		text – описание запроса.
	"""

	# Ответ.
	Response = None

	# Постоянно.
	while True:
		# Запрос подтверждения.
		InputLine = input(f"{text}\nConfirm? [Y/N]: ").strip().lower()
		# Проверка ответов.
		if InputLine == "y": Response = True
		if InputLine == "n": Response = False
		# Если ответ дан, остановить цикл.
		if Response != None: break

	return Response

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

def Warning(warning_type: str, description: str | None = None):
	"""
	Выводит в терминал предупреждение.
		warning_type – тип предупреждения;
		description – описание ошибки.
	"""
	
	# Генерация описания.
	description = f" - {description}" if type(description) == str else ""
	# Вывод в консоль: ошибка.
	StyledPrinter(f"WARNING: {warning_type}{description}", text_color = Styles.Colors.Yellow)

#==========================================================================================#
# >>>>> ШАБЛОНЫ ДАННЫХ <<<<< #
#==========================================================================================#

class ExecutionStatus:
	"""Отчёт о выполнении метода."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def code(self) -> int:
		"""Код выполнения."""

		return self.__Code

	@property
	def data(self) -> dict | None:
		"""Дополнительные данные."""

		return self.__Data

	@property
	def message(self) -> str | None:
		"""Сообщение."""

		return self.__Message

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, code: int, message: str | None = None, data: dict | None = None):
		"""
		Отчёт о выполнении метода.
			code – числовой код;
			message – сообщение;
			data – словарь дополнительных данных.
		"""

		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# Код выполнения.
		self.__Code = code
		# Сообщение.
		self.__Message = message
		# Дополнительные данные.
		self.__Data = data