ARG BASE_IMAGE=python:3.9-slim-buster
FROM $BASE_IMAGE

# system update & package install
RUN apt-get -y update && \
    apt-get install -y --noinstall-recommends \
    build-essential \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .
WORKDIR .

# pip & poetry
RUN python3 -m pip install --user --upgrade pip && \
    python3 -m pip install -r requirements.txt

# configuration
EXPOSE 8000

# execute
CMD ["python", "main.py"]
