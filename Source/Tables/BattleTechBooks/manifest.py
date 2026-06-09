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
		
		manifest.common.switch_binds(True)
		manifest.attachments.add_slot("ebook", "The e-book file.")
		manifest.metainfo_rules.set_field("author", None, "One or more authors.")
		manifest.metainfo_rules.set_field("publisher", None, "Publisher of paper book.")
		manifest.metainfo_rules.set_field(
			"series",
			("The Proliferation Cycle", "Blitzkrieg", "MechWarrior"),
			"Series to which the book belongs."
		)
		manifest.metainfo_rules.set_field("publication_date", None, "Date of book publication in original.")
		manifest.metainfo_rules.set_field("story_source", None, "Source of story.")

		ColumnsNames = ("ID", "Status", "Name", "Author", "Publication", "Type", "Series", "Era", "Estimation")
		OptionsCLI = {
			"columns": dict().fromkeys(ColumnsNames, {"enabled": True, "max_width": None})
		}
		manifest.interfaces_options.set_options(Interfaces.CLI, OptionsCLI)

		return manifest