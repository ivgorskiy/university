ARG BASE_IMAGE=python:3.9-slim-buster
FROM $BASE_IMAGE

# system update & package install
# libpq-dev и postgresql-client нужны для правильной работы с БД
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# копирование из директории всего проекта в директорию всего образа
COPY . .

# определение рабочей директории образа
WORKDIR .

# обновление pip и установка необходимых зависимостей проекта
RUN python3 -m pip install --user --upgrade pip && \
    python3 -m pip install -r requirements.txt

# запуск контейнера
CMD ["python", "main.py"]
