FROM python:3.12.6

RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY requirements-dev.txt /app/
RUN pip install -r /app/requirements-dev.txt

COPY . /app/

WORKDIR /app

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]