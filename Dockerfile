FROM python:3.11.9-slim

WORKDIR /app

ENV POETRY_VERSION=1.7.1
RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

CMD ["poetry", "run", "python", "main.py"]