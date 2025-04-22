FROM python:3.12-alpine

WORKDIR /app

ENV POETRY_VERSION=1.7.1
ENV PATH="/root/.cargo/bin:${PATH}"

RUN apk --update add
RUN apk add --no-cache gcc python3-dev musl-dev

# Установка uv
RUN pip install uv

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN uv pip install --no-cache -r requirements.txt --system

COPY . .

CMD ["python", "main.py"]
