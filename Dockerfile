# base python img
FROM python:3.11

# install poetry and update pip
RUN pip install -U pip setuptools poetry --no-cache-dir
# disable venv creation in container
RUN poetry config virtualenvs.create false

# ..pretty self explanatory.. :)
WORKDIR /app

# separate step for caching
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY . .

ENV ENVIRONMENT=dev

# run tests
RUN python -m unittest discover -s app/__tests__ -p "*_test.py" -v

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
