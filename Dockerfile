ARG BASE_IMAGE=python:3.9-slim-buster
FROM $BASE_IMAGE

# system update & package install
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
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

# определение порта из контейнера наружу
EXPOSE 8000

# запуск контейнера
CMD ["python", "main.py"]
