# Отчёт о покрытии тестами

Дата проверки: 28 августа 2026 года.

Команда:

```bash
poetry run pytest
```

Результат:

```text
57 passed

Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
main.py                     5      1    80%   10
src/__init__.py             7      0   100%
src/aeroplane.py          124      3    98%   52, 55-56
src/api.py                 63      7    89%   52-53, 81-84, 87
src/base_api.py             8      0   100%
src/base_storage.py        10      0   100%
src/exceptions.py           5      0   100%
src/json_saver.py          79      4    95%   37-38, 100-101
src/services.py            36      0   100%
src/user_interface.py      46      1    98%   29
-----------------------------------------------------
TOTAL                     383     16    96%
```

Требуемое покрытие функционального кода — не менее 70%. Фактическое покрытие — **96%**.
