# Habit Log API

REST API для трекера привычек на FastAPI + PostgreSQL. Позволяет логировать выполнение привычек по дням (название привычки, дата, выполнена/нет, заметка).

## Что внутри

- Python 3
- FastAPI
- SQLAlchemy 2
- PostgreSQL
- Uvicorn

## Структура проекта
```text
habit-log-api/
├── app/
│   └── main.py
├── .env.example
├── requirements.txt
```

## API методы

### Проверка состояния
```bash
curl http://127.0.0.1:8010/health
```

### Создать запись
```bash
curl -X POST http://127.0.0.1:8010/logs \
  -H 'Content-Type: application/json' \
  -d '{"habit_name":"Чтение","log_date":"2026-10-01","completed":true,"notes":"30 минут"}'
```

### Получить список записей (с фильтром по привычке)
```bash
curl http://127.0.0.1:8010/logs
curl "http://127.0.0.1:8010/logs?habit_name=Чтение"
```

### Получить запись по ID
```bash
curl http://127.0.0.1:8010/logs/1
```

### Обновить запись
```bash
curl -X PUT http://127.0.0.1:8010/logs/1 \
  -H 'Content-Type: application/json' \
  -d '{"completed":true}'
```

### Удалить запись
```bash
curl -X DELETE http://127.0.0.1:8010/logs/1
```

---

## Задача: запустить через Docker Compose

Приложения в репозитории ещё нет ни `Dockerfile`, ни `docker-compose.yml` — это и есть задача, написать их самостоятельно.

1. **Dockerfile** для `app/` — базовый образ Python, установка зависимостей из `requirements.txt`, запуск через `uvicorn app.main:app --host 0.0.0.0 --port <порт>`.
2. **docker-compose.yml** с двумя сервисами:
   - `db` — официальный образ `postgres` (задать `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` через переменные окружения);
   - `app` — собирается из твоего `Dockerfile`, пробрасывает порт наружу.
3. Добавить **volume** для `db`, чтобы данные не терялись при пересоздании контейнера.
4. Настроить **`depends_on`**, чтобы `app` поднимался после `db` (учти: это не гарантирует, что PostgreSQL уже готов принимать соединения к моменту старта приложения — подумай, что с этим можно сделать).
5. Важный момент про `DATABASE_URL`: в `.env.example` сейчас указан `localhost` — внутри Docker-сети это работать не будет. На что его нужно поменять, когда оба контейнера общаются через одну и ту же docker-compose сеть?
6. Поднять всё одной командой (`docker compose up -d --build`), проверить `docker compose ps`.
7. Проверить все пять эндпоинтов через `curl` (см. примеры выше, порт уже наружу проброшен).
8. Убедиться, что данные переживают перезапуск: `docker compose down`, затем `docker compose up -d` — данные в `/logs` должны остаться (volume сработал).
