[ТЗ = Автоматический_учет_выданных_ветеринарных_препаратов_1.docx](https://github.com/user-attachments/files/23161081/_._._._._._1.docx)

Бекенд для проекта по учету ветеринарных препаратов в рамках обучающего проекта.


## Quick start (Docker)
```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
# Открыть: http://localhost:8000/admin 
```


## Локальный запуск (без Docker)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# в зависимости от OS выполнить одно из:
# linux: export DJANGO_SETTINGS_MODULE=config.settings.local
# win: $env:DJANGO_SETTINGS_MODULE = "config.settings.local"
python manage.py migrate
python manage.py runserver
```


## Структура проекта
1) apps/\<domain> — доменные приложения (модели, API, тесты)
2) apps/\<domain>/services.py — бизнес-логика (Use Cases: приёмка, выдача и т.д.)
3) apps/<domain>/repository.py — взаимодействие с БД
4) common/ — общие утилиты
5) config/settings/ — настройки base.py, local.py, prod.py
6) tests живут рядом с кодом: apps/\<domain>/tests/