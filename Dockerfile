FROM python:3.9.4

EXPOSE 5000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

ARG ENVIRONMENT=prod

RUN apt-get update \
    # нужно для запуска тестов с использованием pytest-redis \
    && if [ "$ENVIRONMENT" != "prod" ]; then apt-get install -y redis; fi;

COPY ./requirements ./requirements
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install -r requirements/$ENVIRONMENT.txt \
    && rm -rf /root/.cache/pip

COPY ./address_book ./address_book
