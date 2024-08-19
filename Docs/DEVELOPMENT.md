## Требования к классам таблиц
Для совместимости с драйвером и унификации все классы таблиц должны содержать следующие обязательные компоненты.

### Статические атрибуты
* `TYPE: str` – название типа таблицы;
* `MANIFEST: dict` – базовый манифест таблицы.

### Свойства
* `cli: any` – класс-обработчик CLI таблицы;
* `manifest: dict` – манифест таблицы;
* `modules: list[str]` – список названий модулей таблицы;
* `name: str` – название таблицы;
* `notes: list[any]` – cписок записей;
* `notes_id: list[int]` – список ID записей;
* `storage: str` – путь к хранилищу таблиц.

### Методы
* `def __init__(self, storage: str, path: str, name: str, autocreation: bool = False)`
* `def create_note(self) -> ExecutionStatus`
* `def delete_note(self, note_id: int) -> ExecutionStatus`
* `def get_note(self, note_id: int) -> ExecutionStatus`
* `def rename(self, name: str) -> ExecutionStatus`

## Требования к классам записей
Для совместимости с драйвером и унификации все классы записей должны содержать следующие обязательные компоненты.

### Статические атрибуты
* `BASE_NOTE: dict` – базовая структура записи.

### Свойства
* `cli: any` – класс-обработчик CLI записи;
* `id: int` – ID записи;
* `name: str` – название записи.

### Методы
* `def __init__(self, table: any, note_id: int):`
* `def rename(self, name: str) -> ExecutionStatus`
* `def save(self) -> ExecutionStatus`

