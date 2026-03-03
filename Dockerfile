FROM python:3.12-slim AS builder

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install  --no-cache-dir poetry==1.8.3

WORKDIR /app

# Add Poetry to the PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* ./

# Install dependencies in a virtual environment
ENV POETRY_VIRTUALENVS_CREATE=false
RUN poetry install --only main --no-root

# Copy the application code
COPY app ./app

# Expose the port the app runs on
EXPOSE 8000

CMD ["python", "-m", "app.server"]
