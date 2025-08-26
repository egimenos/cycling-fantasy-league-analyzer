FROM python:3.8.18

WORKDIR /app

# Install only base/runtime deps in the image
COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir -r requirements/base.txt

COPY pyproject.toml .
COPY alembic.ini .
COPY alembic/ ./alembic
COPY src/ ./src

RUN pip install --no-cache-dir -e .

# Default command for production containers (honors PORT env; default 8000)
CMD ["sh", "-c", "uvicorn procycling_scraper.analysis.infrastructure.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]