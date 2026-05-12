from Source.Core.Base.Table import BaseTable

class Table(BaseTable):
	"""Таблица просмотров аниме."""

	@property
	def max_estimation(self) -> int:
		"""Максимальная допустимая оценка."""

		return self._Descriptor.manifest.custom["max_estimation"]