def ValueToInt(value: str) -> int | str:
		"""
		Преобразует значение в целочисленное, если то не является спецсимволом.
			value – значение.
		"""

		# Преобразование значения.
		if value != "*": value = int(value)

		return value