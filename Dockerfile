# Использовать официальный образ Python как базовый
FROM python:3.11

# Установить Poetry
RUN pip install poetry

# Установить рабочую директорию в контейнере
WORKDIR /code

# Копировать файл зависимостей Poetry в контейнер
COPY pyproject.toml poetry.lock ./

# Установить зависимости проекта с помощью Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Копировать остальные файлы проекта в контейнер
COPY . .