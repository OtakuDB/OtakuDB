from typing import Any

def Unstar(value: Any) -> Any:
	"""
	Преобразует значение `*` в `None`.

	:param value: Обрабатываемое значение.
	:type value: Any
	:return: Обработанное значение.
	:rtype: Any
	"""

	return None if value == "*" else value