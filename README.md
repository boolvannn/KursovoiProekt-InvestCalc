# Инвестиционный калькулятор (FastAPI)

Веб-приложение на FastAPI: считает сложный процент с ежемесячными взносами, рисует графики, сохраняет расчёты в PostgreSQL и умеет экспорт/импорт:
- **Word (.docx)** — шаблонные отчёты с таблицей и графиком
- **Excel (.xlsx)** — отчёт в виде таблицы
- **PDF** — отчёт с вшитым шрифтом (кириллица)
- **Импорт** из Word/Excel обратно в базу

## Стек
- Back: FastAPI, SQLAlchemy 2.x, python-jose, passlib  
- DB: PostgreSQL (psycopg2)  
- Templates: Jinja2  
- Office: python-docx, docxtpl, docxcompose, openpyxl, XlsxWriter  
- PDF/Chart: reportlab, matplotlib  
- Front: HTML/CSS + Chart.js (CDN)

## Быстрый старт

###  Установка

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

(Таблицы создаются автоматически при старте (через Base.metadata.create_all).)
 
###-Запуск-###

python -m uvicorn main:app --reload

# Открыть http://127.0.0.1:8000

git add .
git commit -m ""
git rebase --abort
git push -u origin master --force