# base python img
FROM python:3.11-slim AS build

# install poetry and update pip
RUN pip install -U pip setuptools poetry --no-cache-dir
# disable venv creation in container
RUN poetry config virtualenvs.create false

WORKDIR /app

# separate step for caching
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

COPY . .

ENV ENVIRONMENT=dev
ENV LOG_LEVEL=INFO

# run tests
RUN pytest

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
