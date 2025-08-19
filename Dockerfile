FROM python:3.8.18

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .

COPY alembic.ini .
COPY alembic/ ./alembic

COPY src/ ./src

RUN pip install -e .

CMD ["tail", "-f", "/dev/null"]