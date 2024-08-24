class MetainfoBlocked(Exception):
	"""Исключение: невозможно задать метаданные."""

	def __init__(self):
		"""Исключение: невозможно задать метаданные."""
		
		self.__Message = "Check matainfo rules."
		super().__init__(self.__Message)
			
	def __str__(self):
		return self.__Message