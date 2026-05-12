from Source.Core.Base.Manifest.Generator import Manifest, ManifestGenerator

class Generator(ManifestGenerator):
	"""Генератор манифеста."""

	def _EditManifest(self, manifest: Manifest) -> Manifest:
		"""
		Переопределите данный метод для редактирования стандартного манифеста.

		:param manifest: Редактируемый манифест.
		:type manifest: Manifest
		:return: Отредактированный манифест.
		:rtype: Manifest
		"""

		manifest.metainfo_rules.set_rule("base", ("game", "manga", "novel", "original", "ranobe"))
		manifest.custom["max_estimation"] = 10

		return manifest