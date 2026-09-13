class BondAlreadyDescribedError(Exception):
	"""Исключение: связь уже описана."""

	def __init__(self, bond_name: str):
		"""
		Исключение: связь уже описана.

		:param bond_name: Имя связи.
		:type bond_name: str
		"""

		super().__init__(bond_name)

class MaxBindedNotesCountReachedError(Exception):
	"""Исключение: достигнуто максимальное количество прикрепляемых записей."""

	def __init__(self, bond_name: str, count: int):
		"""
		Исключение: достигнуто максимальное количество прикрепляемых записей.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param count: Максимальное количество записей.
		:type count: int
		"""

		super().__init__(f"For \"{bond_name}\" bond allowed only {count} notes.")

class BondNotDescribedError(Exception):
	"""Исключение: связь не описана."""

	def __init__(self, bond_name: str):
		"""
		Исключение: связь не описана.

		:param bond_name: Имя связи.
		:type bond_name: str
		"""

		super().__init__(bond_name)