class MetainfoBlocked(Exception):
	"""Исключение: невозможно задать метаданные."""

	def __init__(self):
		"""Исключение: невозможно задать метаданные."""
		
		self.__Message = "Check matainfo rules."
		super().__init__(self.__Message)
			
	def __str__(self):
		return self.__Message
	
class AttachmentsDenied(Exception):
	"""Исключение: вложения определённого типа запрещены."""

	def __init__(self, slot: bool):
		"""
		Исключение: вложения определённого типа запрещены.
			slot – запрещены ли вложения в слоты.
		"""
		
		if slot: self.__Message = "Attachments to slots denied."
		else: self.__Message = "Attachments without slots denied."
		super().__init__(self.__Message)
			
	def __str__(self):
		return self.__Message