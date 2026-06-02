from Source.Core.Base.Manifest.Generator import Manifest, ManifestGenerator
from Source.Core.Enums import Interfaces

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

		manifest.attachments.add_slot("ebook", "The e-book file.")
		manifest.metainfo_rules.set_rule("product_code", None)

		ColumnsNames = ("ID", "Status", "Code", "Name", "Ebook", "Type")
		OptionsCLI = {
			"columns": dict().fromkeys(ColumnsNames, {"enabled": True, "max_width": None})
		}
		manifest.interfaces_options.set_options(Interfaces.CLI, OptionsCLI)

		return manifest