# Aircraft Tracker

Консольный трекер самолётов для курсовой работы SkyPro «Проект 2. Трекер самолётов». Программа получает границы
выбранной страны через Nominatim, запрашивает находящиеся в этом прямоугольнике воздушные суда у OpenSky,
преобразует ответ в проверенные объекты и сохраняет их в JSON.

## Возможности

- поиск географических границ страны через API Nominatim;
- получение актуальных векторов состояния воздушных судов через API OpenSky;
- валидация позывного, страны регистрации, ICAO24, скорости, высоты, координат и статуса самолёта;
- сравнение самолётов отдельно по скорости и по высоте;
- приватное хранение состояния объекта `Aeroplane` и доступ через свойства;
- добавление, обновление, поиск и удаление записей в UTF-8 JSON-файле;
- фильтрация самолётов по одной или нескольким странам регистрации без учёта регистра;
- фильтрация по диапазону высот;
- сортировка по высоте по убыванию и получение топа N;
- человекочитаемый консольный вывод;
- обработка сетевых ошибок, некорректных ответов API, повреждённого JSON и неверного пользовательского ввода.

## Архитектура

`BaseAPI` и `BaseStorage` — абстрактные интерфейсы, все их операции отмечены `@abstractmethod`.
`AeroplanesAPI` и `JSONSaver` реализуют эти интерфейсы. Консольный сценарий зависит от абстракций и принимает
реализации через параметры, поэтому API-клиент или хранилище можно заменить без изменения пользовательского слоя.

Такое разделение обеспечивает:

- **SRP** — модель, сетевые запросы, хранение, обработка данных и ввод-вывод имеют отдельные зоны ответственности;
- **OCP** — новый API-провайдер или формат хранения добавляется реализацией существующего интерфейса;
- инкапсуляцию данных модели и наследование реализаций от абстрактных классов.

## Структура проекта

```text
aircraft_tracker/
├── data/
│   └── aeroplanes.json
├── src/
│   ├── __init__.py
│   ├── aeroplane.py
│   ├── api.py
│   ├── base_api.py
│   ├── base_storage.py
│   ├── exceptions.py
│   ├── json_saver.py
│   ├── services.py
│   └── user_interface.py
├── tests/
│   ├── conftest.py
│   ├── test_aeroplane.py
│   ├── test_api.py
│   ├── test_base_classes.py
│   ├── test_json_saver.py
│   ├── test_main.py
│   ├── test_services.py
│   └── test_user_interface.py
├── .flake8
├── coverage_report.md
├── main.py
├── poetry.lock
└── pyproject.toml
```

## Установка

Требуются Python 3.12 или новее и Poetry 2.x.

```bash
git clone https://github.com/gefrix/aircraft-tracker.git
cd aircraft-tracker
poetry install
```

Регистрация или API-ключи для базового анонимного запроса не требуются. Nominatim требует идентифицирующий
`User-Agent`; приложение передаёт его автоматически. Внешние сервисы могут ограничивать частоту запросов, поэтому
программа выполняет только по одному запросу к каждому API на один пользовательский поиск.

Документация используемых API:

- [Nominatim Search API](https://nominatim.org/release-docs/develop/api/Search/)
- [OpenSky REST API](https://openskynetwork.github.io/opensky-api/rest.html)

## Запуск

```bash
poetry run python main.py
```

Программа последовательно запросит:

1. страну, в воздушном пространстве которой нужно найти самолёты;
2. размер топа N;
3. страны регистрации через запятую — поле можно оставить пустым;
4. диапазон высот вида `1000 - 15000` — поле также можно оставить пустым.

Пример строки результата:

```text
1. UAL1621 — United States; высота: 10203 м; скорость: 268.8 м/с; в полете
```

Полученные самолёты сохраняются в [`data/aeroplanes.json`](data/aeroplanes.json). Повторная запись самолёта с тем
же ICAO24 обновляет существующую запись и не создаёт дубликат.

## Программное использование

```python
from src.aeroplane import Aeroplane
from src.api import AeroplanesAPI
from src.json_saver import JSONSaver
from src.services import get_top_aeroplanes, sort_aeroplanes

api = AeroplanesAPI()
raw_states = api.get_aeroplanes("Spain")
aeroplanes = Aeroplane.cast_to_object_list(raw_states)

saver = JSONSaver()
for aeroplane in aeroplanes:
    saver.add_aeroplane(aeroplane)

top_five = get_top_aeroplanes(sort_aeroplanes(aeroplanes), 5)
```

## Проверка качества

```bash
poetry run pytest
poetry run black --check src tests main.py
poetry run isort --check-only src tests main.py
poetry run flake8 src tests main.py
poetry run mypy src main.py
poetry check
```

В проекте проходят **57 тестов**, покрытие функционального кода составляет **96%** при требовании не менее 70%.
Полный результат сохранён в [`coverage_report.md`](coverage_report.md).

## Соответствие критериям

| Критерий | Реализация |
|---|---|
| Абстрактный API-класс | `BaseAPI(ABC)`, два осмысленных абстрактных метода |
| Работа с API и исключениями | `AeroplanesAPI`, тайм-ауты, `raise_for_status()`, проверка структуры JSON, собственные исключения |
| Не менее четырёх атрибутов | В `Aeroplane` восемь типизированных и валидируемых атрибутов |
| Сравнение по скорости и высоте | `compare_speed()`, `compare_altitude()`, `is_faster_than()`, `is_higher_than()` |
| Абстрактное хранилище | `BaseStorage(ABC)`, все операции отмечены `@abstractmethod` |
| Корректный JSON | `JSONSaver` добавляет/обновляет, фильтрует и удаляет записи |
| Пользовательский ввод | Проверка страны, положительного N и формата диапазона высот |
| Топ N | Сортировка `DESC` по высоте и скорости, затем безопасный срез |
| Фильтрация | Без учёта регистра по странам регистрации и включительно по высоте |
| Единая программа | Все классы объединены в `user_interaction()` и запускаются из `main.py` |
| Тестирование | 57 тестов, покрытие 96% |

## GitFlow

- `main` — стабильная версия;
- `develop` — интеграционная ветка;
- `feature/coursework-aircraft-tracker` — ветка реализации курсовой работы.
