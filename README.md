# MyTwitter API Service

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)](https://fastapi.tiangolo.com/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)](https://www.postgresql.org/)

## Описание проекта

API-сервис, имитирующий функционал Twitter, разработан с использованием FastAPI и PostgreSQL. Поддерживает основные
возможности, такие как создание твитов, лайки, подписки, загрузка медиафайлов и управление профилем.

![Главная страница](/assets/Снимок%20экрана%202025-01-24%20в%2016.05.04.png)

## Основной функционал

1. **Создание твитов**
    - **URL**: `POST /api/tweets`
    - **Тело запроса**:
      ```json
      {
        "tweet_data": "string",
        "tweet_media_ids": [1, 2] // Опционально
      }
      ```
    - **Ответ**:
      ```json
      {
        "result": true,
        "tweet_id": 123
      }
      ```

2. **Удаление твита**
    - **URL**: `DELETE /api/tweets/<id>`
    - **Ответ**:
      ```json
      {
        "result": true
      }
      ```

3. **Лайки**
    - **Добавление лайка**:
        - **URL**: `POST /api/tweets/<id>/likes`
        - **Ответ**:
          ```json
          {
            "result": true
          }
          ```
    - **Удаление лайка**:
        - **URL**: `DELETE /api/tweets/<id>/likes`
        - **Ответ**:
          ```json
          {
            "result": true
          }
          ```

4. **Подписки**
    - **Подписаться на пользователя**:
        - **URL**: `POST /api/users/<id>/follow`
        - **Ответ**:
          ```json
          {
            "result": true
          }
          ```
    - **Отписаться от пользователя**:
        - **URL**: `DELETE /api/users/<id>/follow`
        - **Ответ**:
          ```json
          {
            "result": true
          }
          ```

5. **Загрузка медиафайлов**
    - **URL**: `POST /api/medias`
    - **Форма**:
      ```
      form: file="image.jpg"
      ```
    - **Ответ**:
      ```json
      {
        "result": true,
        "media_id": 456
      }
      ```

6. **Профиль пользователя**
    - **Получение информации о себе**:
        - **URL**: `GET /api/users/me`
        - **Ответ**:
          ```json
          {
            "result": true,
            "user": {
              "id": 11,
              "name": "Test User",
              "followers": [
                {"id": 6, "name": "Jeremy Smith"},
                {"id": 9, "name": "Lisa Wilcox"}
              ],
              "following": [
                {"id": 1, "name": "Kathleen Meyer"}
              ]
            }
          }
          ```
    - **Получение информации о другом пользователе**:
        - **URL**: `GET /api/users/<id>`
        - **Ответ**:
          ```json
          {
            "result": true,
            "user": {
              "id": 12,
              "name": "Other User",
              "followers": [...],
              "following": [...]
            }
          }
          ```

7. **Лента твитов**
    - **URL**: `GET /api/tweets`
    - **Ответ**:
      ```json
      {
        "result": true,
        "tweets": [
          {
            "id": 101,
            "content": "Hello World!",
            "attachments": ["/media/1", "/media/2"],
            "author": {
              "id": 11,
              "name": "Test User"
            },
            "likes": [
              {"user_id": 6, "name": "Jeremy Smith"},
              {"user_id": 9, "name": "Lisa Wilcox"}
            ]
          }
        ]
      }
      ```

## Технические особенности

- **Язык**: Python 3.12.6
- **Фреймворк**: FastAPI
- **База данных**: PostgreSQL
- **Контейнеризация**: Docker и docker-compose
- **Тестирование**: pytest
- **Линтинг**: mypy, black, isort

## Установка и запуск

### Локальный запуск

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настройте переменные окружения, используя файл `.env.template`:
   ```bash
   cp .env.template .env
   ```
   Заполните необходимые значения в файле `.env`. Обратите внимание на переменную `MODE=TEST`. Это значение используется
   для запуска тестов. Вы можете заменить его на любое значение, соответствующее режиму работы вашего приложения (например,
   `MODE=development` или `MODE=production`), в зависимости от ваших потребностей.


4. Выполните миграции базы данных:
   ```bash
   alembic upgrade head
   ```

5. Запустите сервер разработки:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Документация будет доступна по адресу: `http://127.0.0.1:8000/docs`

### Запуск с использованием Docker

1. Настройте переменные окружения, используя файл `.env.template`:
   ```bash
   cp .env.template .env
   ```
   Заполните необходимые значения в файле `.env`. Обратите внимание на переменную `MODE=TEST`. Это значение используется
   для запуска тестов. Вы можете заменить его на любое значение, соответствующее режиму работы вашего приложения (например,
   `MODE=development` или `MODE=production`), в зависимости от ваших потребностей.


2. Убедитесь, что значения из файла .env соответствуют параметрам в docker-compose.yml. Замените переменные окружения
   для PostgreSQL:
   environment:
   ```dockerfile
     - POSTGRES_USER=<ваше_значение>
     - POSTGRES_PASSWORD=<ваше_значение>
     - POSTGRES_DB=<ваше_значение>
   healthcheck:
     test: [ "CMD-SHELL", "pg_isready -U <ваше_значение> -d <ваше_значение>" ]
   ```

3. Соберите и запустите контейнеры:
   ```bash
   docker-compose up -d
   ```

4. Убедитесь, что приложение работает: `http://127.0.0.1:80`

## Тестирование

Для запуска тестов выполните:

   ```bash
   pytest tests
   ```

## Используемые технологии

- **FastAPI**: Для создания веб-API.
- **PostgreSQL**: Для хранения данных.
- **Docker**: Для контейнеризации приложения.
