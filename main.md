### Авторизация ###

Регистрация/логин → cookie access_token (JWT, 7 дней)

passlib (pbkdf2_sha256) для хэширования паролей

### Расчёт

POST /api/calc/run — считает по входным данным (без сохранения)

POST /api/calc/save — сохраняет расчёт и годовые строки в БД

GET /api/calc/list — список расчётов текущего пользователя

### Экспорт

GET /api/report/{id} — Word (.docx) (docxtpl + таблица)

GET /api/report/excel/{id} — Excel (.xlsx) (openpyxl/XlsxWriter)

GET /api/report/pdf/{id} — PDF (reportlab + встраивание шрифта для кириллицы)

для корректной кириллицы используется шрифт DejaVuSans (вшивается автоматически; при необходимости положите TTF в static/fonts и укажите путь в коде).

### Импорт

POST /api/import/word — .docx

Берётся первая таблица: колонки Год / Сумма / Взносы / Доходность

Заголовок «Отчёт по расчёту: …» — как имя расчёта (можно передать ?title=.../FormData title)

POST /api/import/excel — .xlsx

Заголовок в A1: «Отчёт по расчёту: …»

Заголовок таблицы на 7-й строке: Год / Сумма / Взносы / Доходность

Числа принимаются как в числовом формате Excel, так и строками (разделители, ₽, пробелы)

При импорте исходные параметры (initial_amount, monthly_contribution, annual_rate) восстановить нельзя — сохраняются 0. Итоги и помесячная таблица — полностью восстанавливаются.

### Частые проблемы и решения

* **uvicorn запускается не из вашего venv / “Fatal error in launcher”**
 Запускай так:

`python -m uvicorn main:app --reload`

или полным путём:

`.\.venv\Scripts\uvicorn.exe main:app --reload`


* **jose → SyntaxError (print без скобок)**

Удалить старый пакет и поставить правильный:

`pip uninstall jose -y
pip install "python-jose[cryptography]"`


* Проблема соединения с PostgreSQL / UnicodeDecodeError ... 0xC2
В DATABASE_URL затесался невидимый неразрывный пробел. Переопредели переменную вручную без пробелов (или задай заново в сессии PowerShell).

* Кириллица в PDF квадратиками
Убедись, что для reportlab берётся шрифт с кириллицей (например, DejaVuSans) и он встраивается. В нашем коде это учтено.

* Модалка логина всплывает на профиле
Мы подключаем partials/auth_modal.html только когда user отсутствует (см. base.html).