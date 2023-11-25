FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN apk update &&\
    apk add bash &&\
    pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./entrypoint-fastapi.sh && \
    chmod +x ./wait-for-it.sh

ENTRYPOINT ["./wait-for-it.sh", "database:5432", "--strict", "--timeout=3000", "--", "./entrypoint-fastapi.sh"]
