from Source.CLI.Templates import ExecutionStatus
from dublib.Methods import ReadJSON, WriteJSON

import os

class MediaViewsNote:
	"""Запись просмотра медиаконтента."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	# Пустая структура записи.
	BASE_NOTE = {
		"name": None,
		"another-names": [],
		"estimation": None,
		"status": None,
		"group": None,
		"tags": [],
		"metainfo": {},
		"parts": []
	}

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self.__Data["another-names"]

	@property
	def emoji_status(self) -> str:
		"""Статус просмотра в видзе эмодзи."""

		# Определения статусов.
		Statuses = {
			"announced": "ℹ️",
			"watching": "▶️",
			"complete": "✅",
			"dropped": "⛔",
			None: ""
		}

		return Statuses[self.__Data["status"]]

	@property
	def estimation(self) -> int | None:
		"""Оценка."""

		return self.__Data["estimation"]

	@property
	def group_id(self) -> int | None:
		"""Идентификатор группы."""

		return self.__Data["group"]

	@property
	def id(self) -> int:
		"""Идентификатор."""

		return self.__ID

	@property
	def metainfo(self) -> dict:
		"""Метаданные."""

		return self.__Data["metainfo"]

	@property
	def name(self) -> str | None:
		"""Название."""

		return self.__Data["name"]

	@property
	def parts(self) -> list[dict]:
		"""Список частей."""

		return list(self.__Data["parts"])

	@property
	def progress(self) -> float:
		"""Прогресс просмотра."""

		# Прогресс.
		Progress = 0
		# Максимальное значение прогресса.
		MaxProgress = 0
		# Текущий прогресс.
		CurrentProgress = 0
		# Список частей.
		Parts = self.parts

		# Если есть части.
		if Parts:

			# Для каждой части.
			for Part in self.parts:

				# Если есть серии.
				if "series" in Part.keys() and Part["series"] != None:
					# Подсчёт серий.
					MaxProgress += Part["series"]

				else:
					# Инкремент.
					MaxProgress += 1

			# Для каждой части.
			for Part in self.parts:

				# Если часть просмотрена и есть серии.
				if Part["watched"] and "series" in Part.keys() and Part["series"] != None:
					# Подсчёт серий.
					CurrentProgress += Part["series"] if "mark" not in Part.keys() else Part["mark"]

				elif Part["watched"]:
					# Инкремент.
					CurrentProgress += 1

			# Подсчёт прогресса.
			Progress = int(CurrentProgress / MaxProgress * 100)

		return Progress

	@property
	def status(self) -> str | None:
		"""Статус просмотра."""

		return self.__Data["status"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return list(self.__Data["tags"])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetBasePart(self, part_type: str) -> dict:
		"""
		Возвращает стандартную словарную структуру части.
			part_type – тип части.
		"""

		# Типы: сезон.
		if part_type in ["season"]: return {
			"type": part_type,
			"number": None,
			"series": None,
			"watched": False
		}

		# Типы: фильм.
		if part_type in ["film"]: return {
			"type": part_type,
			"name": None,
			"watched": False
		}

		# Типы: ONA, OVA, специальные выпуски.
		if part_type in ["ONA", "OVA", "specials"]: return {
			"type": part_type,
			"series": None,
			"watched": False
		}

	def __ModifyPart(self, part: dict, data: dict) -> dict:
		"""
		Подставляет типовые значения в часть.
			part – словарное представление части;
			data – словарь данных для подстановки в часть.
		"""
		
		# Для каждого значения из переданных данных.
		for Key in data.keys():

			# Если ключ в списке опциональных.
			if Key in ["announce", "comment", "link", "name", "number"]:

				# Если значение не удаляется.
				if data[Key] != "*":
					# Добавление нового значения.
					part[Key] = data[Key]

				# Если опциональное значение определено.
				elif Key in part.keys():
					# Удаление опционального значения.
					del part[Key]

			# Если ключ удаляет закладку.
			elif Key == "watched":
				# Если просмотрено, удалить закладку.
				if data["watched"] and "mark" in data.keys(): del part["mark"]
				# Обновление статуса просмотра.
				part[Key] = data[Key]

			else:
				# Если ключ определён в части, перезаписать данные.
				if Key in part.keys(): part[Key] = data[Key]

		return part

	def __UpdateStatus(self):
		"""Обновляет статус просмотра."""

		# Если не заброшено.
		if self.__Data["status"] != "dropped":
			# Получение прогресса.
			Progress = self.progress
			# Обработка статусов.
			if Progress == None: self.__Data["status"] = None
			elif Progress == 100: self.__Data["status"] = "complete"
			else: self.__Data["status"] = "watching"

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "MediaViewsTable", note_id: int):
		"""
		Запись просмотра медиаконтента.
			table – объектное представление таблицы;
			note_id – идентификатор записи.
		"""
		
		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# ID записи.
		self.__ID = note_id
		# Объектное представление таблицы.
		self.__Table = table
		# Данные записи.
		self.__Data = ReadJSON(f"{table.directory}/{table.name}/{self.__ID}.json")
	
	def add_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Добавляет альтернативное название.
			another_name – альтернативное название.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если такое альтренативное название ещё не задано.
			if another_name not in self.__Data["another-names"]:
				# Добавление алтернативного названия.
				self.__Data["another-names"].append(another_name)
				# Сохранение изменений.
				self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def add_part(self, part_type: str, data: dict) -> ExecutionStatus:
		"""
		Добавляет новую часть.
			part_type – тип части;
			data – данные для заполнения свойств части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Буфер части.
			Buffer = self.__GetBasePart(part_type)
			# Подстановка данных.
			Buffer = self.__ModifyPart(Buffer, data)
			# Добавление новой части.
			self.__Data["parts"].append(Buffer)
			# Обновление статуса просмотра.
			self.__UpdateStatus()
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def add_tag(self, tag: str) -> ExecutionStatus:
		"""
		Добавляет тег.
			tag – название тега.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если тег ещё не задан.
			if tag not in self.__Data["tags"]:
				# Добавление нового тега.
				self.__Data["tags"].append(tag)
				# Сохранение изменений.
				self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def delete_another_name(self, another_name: int | str) -> ExecutionStatus:
		"""
		Удаляет альтернативное название.
			another_name – альтернативное название или его индекс.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если передан индекс.
			if another_name.isdigit():
				# Удаление альтернативного названия по индексу.
				self.__Data["another-names"].pop(int(another_name))

			else:
				# Удаление альтернативного названия по значению.
				self.__Data["another-names"].remove(another_name)

			# Сохранение изменений.
			self.save()

		except IndexError:
			# Изменение статуса.
			Status = ExecutionStatus(1, "incorrect_another_name_index")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def delete_metainfo(self, key: str) -> ExecutionStatus:
		"""
		Удаляет метаданные.
			key – ключ метаданных.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Удаление метаданных.
			del self.__Data["metainfo"][key]
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def delete_part(self, part_index: int) -> ExecutionStatus:
		"""
		Удаляет часть.
			index – индекс части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Удаление части.
			del self.__Data["parts"][part_index]
			# Обновление статуса просмотра.
			self.__UpdateStatus()
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def delete_tag(self, tag: int | str) -> ExecutionStatus:
		"""
		Удаляет тег.
			tag – тег или его индекс.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если передан индекс.
			if tag.isdigit():
				# Удаление тега по индексу.
				self.__Data["tags"].pop(int(tag))

			else:
				# Удаление тега по значению.
				self.__Data["tags"].remove(tag)

			# Сохранение изменений.
			self.save()

		except IndexError:
			# Изменение статуса.
			Status = ExecutionStatus(1, "incorrect_tag_index")

		except IndexError:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def down_part(self, part_index: int) -> ExecutionStatus:
		"""
		Опускает часть на одну позицию вниз.
			part_index – индекс части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если не последняя часть.
			if part_index != len(self.__Data["parts"]) - 1:
				# Перемещение части вверх.
				self.__Data["parts"].insert(part_index + 1, self.__Data["parts"].pop(part_index))
				# Сохранение изменений.
				self.save()

			# Если последняя часть.
			elif part_index == len(self.__Data["parts"]) - 1:
				# Изменение статуса.
				Status = ExecutionStatus(1, "unable_down_last_part")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def edit_part(self, part_index: int, data: dict) -> ExecutionStatus:
		"""
		Редактирует свойства части.
			part_index – индекс части;
			data – данные для обновления свойств части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Подстановка данных.
			self.__Data["parts"][part_index] = self.__ModifyPart(self.__Data["parts"][part_index], data)
			# Обновление статуса просмотра.
			self.__UpdateStatus()
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def estimate(self, estimation: int) -> ExecutionStatus:
		"""
		Выставляет оценку.
			estimation – оценка.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если оценка в допустимом диапазоне.
			if estimation <= self.__Table.options["max-estimation"]:
				# Выставление оценки.
				self.__Data["estimation"] = estimation
				# Сохранение изменений.
				self.save()

			else:
				# Изменение статуса.
				Status = ExecutionStatus(1, "max_estimation_exceeded")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает запись.
			name – название записи.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Изменение имени.
			self.__Data["name"] = name
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def reset(self, key: str) -> ExecutionStatus:
		"""
		Сбрасывает поле к стандартному значению.
			key – ключ поля.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Сброс значения.
			self.__Data[key] = type(self.BASE_NOTE[key])()
			# Обновление статуса просмотра.
			self.__UpdateStatus()
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def save(self):
		"""Сохраняет запись в локальный файл."""

		# Сохранение записи.
		WriteJSON(f"{self.__Table.directory}/{self.__Table.name}/{self.__ID}.json", self.__Data)

	def set_group(self, group_id: int) -> ExecutionStatus:
		"""
		Устанавливает принадлежность к группе.
			group_id – идентификатор группы.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Сброс значения.
			self.__Data["group"] = group_id
			# Добавление элемента в группу.
			self.__Table.add_group_element(group_id, self.__ID)
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def set_mark(self, part_index: int, mark: int) -> ExecutionStatus:
		"""
		Добавляет закладку на серию.
			part_index – индекс части;
			mark – номер серии для постановки закладки (0 для удаления закладки, номер последней серии для пометки всей части как просмотренной).
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если часть многосерийная.
			if "series" in self.__Data["parts"][part_index].keys():

				# Если закладка установлена на просмотренную часть.
				if self.__Data["parts"][part_index]["watched"]:
					# Снятие статуса полностью просмотренного и установка закладки.
					self.__Data["parts"][part_index]["watched"] = False
					self.__Data["parts"][part_index]["mark"] = mark
					# Обновление статуса просмотра.
					self.__UpdateStatus()
					# Сохранение изменений.
					self.save()
					# Изменение статуса.
					Status = ExecutionStatus(2, "Part marked as unseen.")

				else:

					# Если закладка лежит в диапазоне серий.
					if mark < self.__Data["parts"][part_index]["series"] and mark != 0:
						# Обновление закладки.
						self.__Data["parts"][part_index]["mark"] = mark

					# Если закладка на последней серии.
					elif mark == self.__Data["parts"][part_index]["series"]:
						# Добавление статуса полностью просмотренного и удаление закладки.
						self.__Data["parts"][part_index]["watched"] = True
						if "mark" in self.__Data["parts"][part_index].keys(): del self.__Data["parts"][part_index]["mark"]
						# Изменение статуса.
						Status = ExecutionStatus(1, "Part marked as fully viewed.")

					# Если закладка на нулевой серии.
					elif mark == 0:
						# Удаление закладки.
						del self.__Data["parts"][part_index]["mark"]
						# Изменение статуса.
						Status = ExecutionStatus(3, "Mark removed.")

					# Сохранение изменений.
					self.save()
					# Обновление статуса просмотра.
					self.__UpdateStatus()

			else:
				# Изменение статуса.
				Status = ExecutionStatus(-2, "only_series_supports_marks")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def set_metainfo(self, key: str, metainfo: str) -> ExecutionStatus:
		"""
		Задаёт метаданные.
			key – ключ метаданных;
			metainfo – значение метаданных.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Установка метаданных.
			self.__Data["metainfo"][key] = metainfo
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def set_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус.
			status – статус просмотра.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)
		# Определения статусов.
		Statuses = {
			"w": "watching",
			"c": "complete",
			"d": "dropped",
			"*": None
		}

		try:
			# Установка статуса.
			self.__Data["status"] = Statuses[status]
			# Сохранение изменений.
			self.save()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def up_part(self, part_index: int) -> ExecutionStatus:
		"""
		Поднимает часть на одну позицию вверх.
			part_index – индекс части.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:

			# Если не первая часть.
			if part_index != 0:
				# Перемещение части вверх.
				self.__Data["parts"].insert(part_index - 1, self.__Data["parts"].pop(part_index))
				# Сохранение изменений.
				self.save()

			# Если первая часть.
			elif part_index == 0:
				# Изменение статуса.
				Status = ExecutionStatus(1, "unable_up_first_part")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

class MediaViewsTable:
	"""Таблица просмотров медиакнотента."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def directory(self) -> str:
		"""Путь к каталогу таблицы."""

		return self.__StorageDirectory

	@property
	def id(self) -> list[MediaViewsNote]:
		"""Идентификатор таблицы."""

		return self.__Notes.values()

	@property
	def max_estimation(self) -> int:
		"""Максимальная допустимая оценка."""

		return self.__Options["max-estimation"]

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self.__Name

	@property
	def notes(self) -> list[MediaViewsNote]:
		"""Список записей."""

		return self.__Notes.values()

	@property
	def options(self) -> dict:
		"""Словарь опций таблицы."""

		return self.__Options.copy()	

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Create(self):
		"""Создаёт каталог и файл описания таблицы."""

		# Если каталог не существует, создать его.
		if not os.path.exists(f"{self.__StorageDirectory}/{self.__Name}"): os.makedirs(f"{self.__StorageDirectory}/{self.__Name}")
		# Сохранение описания.
		WriteJSON(f"{self.__StorageDirectory}/{self.__Name}/main.json", self.__Options)

	def __GetNewID(self, container: dict) -> int:
		"""
		Генерирует ID для новой записи или группы.
			container – контейнер записи или группы.
		"""

		# Новый ID.
		NewID = None

		# Если включено использование освободившихся ID.
		if self.__Options["recycle-id"]:
			# Список ID.
			ListID = container.keys()

			# Для каждого значения ID до максимального.
			for ID in range(1, len(ListID) + 1):

				# Если ID свободен.
				if ID not in ListID:
					# Выбор ID.
					NewID = ID
					# Остановка цикла.
					break

		# Если ID не назначен.
		if not NewID:
			# Назначение нового ID методом инкремента максимального.
			NewID = int(max(container.keys())) + 1 if len(container.keys()) > 0 else 1

		return NewID

	def __GetNotesListID(self) -> list[int]:
		"""Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON."""

		# Список ID.
		ListID = list()
		# Получение списка файлов в таблице.
		Files = os.listdir(f"{self.__StorageDirectory}/{self.__Name}")
		# Фильтрация только файлов формата JSON.
		Files = list(filter(lambda File: File.endswith(".json"), Files))

		# Для каждого файла.
		for File in Files: 
			# Если название файла не является числом, удалить его.
			if not File.replace(".json", "").isdigit(): Files.remove(File)

		# Для каждого файла получить и записать ID.
		for File in Files: ListID.append(int(File.replace(".json", "")))
		
		return ListID

	def __ReadNote(self, note_id: int):
		"""
		Считывает содержимое записи.
			note_id – идентификатор записи.
		"""

		# Чтение записи.
		self.__Notes[note_id] = MediaViewsNote(self, note_id)

	def __ReadNotes(self):
		"""Считывает содержимое всех записей."""

		# Получение списка ID записей.
		ListID = self.__GetNotesListID()

		# Для каждого ID записи.
		for ID in ListID:
			# Чтение записи.
			self.__ReadNote(ID)

	def __SaveGroups(self):
		"""Сохраняет описание группы в локальный файл."""

		# Если определения групп остались.
		if len(self.__Groups.keys()) > 0:
			# Сохранение локального файла JSON.
			WriteJSON(f"{self.__StorageDirectory}/{self.__Name}/groups.json", self.__Groups)

		else:
			# Удаление локального файла.
			os.remove(f"{self.__StorageDirectory}/{self.__Name}/groups.json")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, storage_dir: str, name: str, autocreation: bool = True):
		"""
		Таблица просмотров медиакнотента.
			storage_dir – директория хранения таблиц;
			name – название таблицы;
			autocreation – указывает, нужно ли создавать таблицу при отсутствии таковой. 
		"""
		
		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# Директория хранения таблиц.
		self.__StorageDirectory = storage_dir.rstrip("/\\")
		# Имя таблицы.
		self.__Name = name
		# Словарь записей.
		self.__Notes = dict()
		# Словарь групп.
		self.__Groups = dict()
		# Опции таблицы.
		self.__Options = {
			"version": 1,
			"type": "media-views",
			"recycle-id": False,
			"max-estimation": 10,
			"viewer": {
				"links": True,
				"comments": True
			}
		}

		# Если найден файл описания таблицы.
		if os.path.exists(f"{self.__StorageDirectory}/{self.__Name}/main.json"):
			# Чтение файла.
			self.__Options = ReadJSON(f"{self.__StorageDirectory}/{self.__Name}/main.json")
			# Если тип таблицы не соответствует, выбросить исключение.
			if self.__Options["type"] != "media-views": raise TypeError("Only \"media-views\" type tables supported.")
			# Чтение записей.
			self.__ReadNotes()

		# Если включено автосоздание таблицы.
		elif autocreation:
			# Создание таблицы.
			self.__Create()

		# Выброс исключения
		else: raise FileExistsError("main.json")

		# Если найден файл описания групп.
		if os.path.exists(f"{self.__StorageDirectory}/{self.__Name}/groups.json"):
			# Чтение групп.
			self.__Groups = ReadJSON(f"{self.__StorageDirectory}/{self.__Name}/groups.json")

	def add_group_element(self, group_id: int, note_id: int):
		"""
		Добавляет идентификатор записи в элементы группы.
			group_id – идентификатор группы;
			note_id – идентификатор записи.
		"""

		# Данные группы.
		Group = self.get_group(group_id)
		# Если элемент ещё не в группе, добавить его.
		if note_id not in Group["elements"]: Group["elements"].append(note_id)
		# Сохранение групп в локальный файл.
		self.__SaveGroups()

	def create_group(self, name: str) -> ExecutionStatus:
		"""
		Создаёт группу для объединения записей.
			name – название группы.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# ID новой группы.
			ID = self.__GetNewID(self.__Groups)
			# Заполнение структуры группы.
			self.__Groups[str(ID)] = {
				"name": name,
				"elements": []
			}
			# Сохранение групп в локальный файл.
			self.__SaveGroups()
			# Изменение статуса.
			Status = ExecutionStatus(0, data = {"id": ID})

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def create_note(self) -> ExecutionStatus:
		"""Создаёт запись."""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# ID новой записи.
			ID = self.__GetNewID(self.__Notes)
			# Сохранение локального файла JSON.
			WriteJSON(f"{self.__StorageDirectory}/{self.__Name}/{ID}.json", MediaViewsNote.BASE_NOTE)
			# Чтение и объектная интерпретация записи.
			self.__ReadNote(ID)
			# Изменение статуса.
			Status = ExecutionStatus(0, data = {"id": ID})

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Переименование каталога.
			os.rename(f"{self.__StorageDirectory}/{self.__Name}", f"{self.__StorageDirectory}/{name}")
			# Перезапись имени.
			self.__Name = name

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status
		
	def remove_group(self, group_id: int) -> ExecutionStatus:
		"""
		Удаляет группу. 
			group_id – идентификатор группы.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Приведение ID к строковому типу.
			group_id = str(group_id)
			# Удаление группы из словаря.
			del self.__Groups[group_id]
			# Сохранение групп в локальный файл.
			self.__SaveGroups()

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def remove_note(self, note_id: int) -> ExecutionStatus:
		"""
		Удаляет запись из таблицы. 
			note_id – идентификатор записи.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		try:
			# Приведение ID к целочисленному типу.
			note_id = int(note_id)
			# Удаление записи из словаря.
			del self.__Notes[note_id]
			# Удаление локального файла.
			os.remove(f"{self.__StorageDirectory}/{self.__Name}/{note_id}.json")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def get_group(self, group_id: int) -> dict | None:
		"""
		Возвращает словарное представление группы.
			group_id – идентификатор группы.
		"""

		# Группа.
		Group = None
		# Приведение ID к строковому типу.
		group_id = str(group_id)
		# Если группа существует, записать её определение.
		if group_id in self.__Groups.keys(): Group = self.__Groups[group_id]

		return Group

	def get_group_notes(self, group_id: int) -> list[MediaViewsNote]:
		"""
		Возвращает словарное представление группы.
			group_id – идентификатор группы.
		"""

		# Список записей.
		NotesList = list()
		
		# Для каждой записи.
		for Note in self.notes:
			# Если запись включена в указанную группу, добавить её в список.
			if note.group == group_id: NotesList.append(Note)

		return NotesList

	def get_note(self, note_id: int) -> MediaViewsNote | None:
		"""
		Возвращает объектное представление записи.
			note_id – идентификатор записи.
		"""

		# Запись.
		Note = None

		try:
			# Приведение ID к целочисленному типу.
			note_id = int(note_id)
			# Осуществление доступа к записи.
			Note = self.__Notes[note_id]

		except: pass

		return Note