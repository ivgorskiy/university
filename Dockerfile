# Набор инструкций для сборки образа.
# Каждая инструкция создаёт новый слой внутри образа.

# Определение переменных для инструкции FROM
ARG BASE_IMAGE=python:3.9-slim-buster

# Определение базового образа ОС
FROM $BASE_IMAGE

# Команды, выполняемые внутри образа
# && используются для объединения нескольких команд в одну строку. Команды
# при этом выполняются последовательно, с контролем успешного выполнения
# предыдущей (код возврата 0).
# libpq-dev и postgresql-client нужны для правильной работы с БД
# Загрузка последних версий пакетов
RUN apt-get -y update && \
    # Установка загруженных пакетов
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копирование из директории всего проекта в директорию всего образа
COPY . .

# Определение рабочей директории образа для последующих инструкций
# RUN, CMD, ENTRYPOINT, COPY и ADD
WORKDIR .

# Обновление pip и установка необходимых зависимостей проекта
RUN python3 -m pip install --user --upgrade pip && \
    python3 -m pip install -r requirements.txt

# Команда, выполняемая при запуске созданного контейнера
CMD ["python", "main.py"]
