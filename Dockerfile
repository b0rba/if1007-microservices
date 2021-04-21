FROM python:3.8.5-slim-buster AS build

WORKDIR /app

RUN apt update && apt install curl -y
# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

ADD poetry.lock pyproject.toml ./
RUN poetry export --without-hashes -f requirements.txt -o requirements.txt

FROM python:3.8.5-slim-buster

WORKDIR /app

ENV PYTHONPATH $PWD
ENV PYTHONUNBUFFERED 1

COPY --from=build /app/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
