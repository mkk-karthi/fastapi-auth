poetry run uvicorn app.main:app --reload
python app/server.py

alembic revision --autogenerate -m "Example model" // Create migrations
alembic upgrade head    // Apply migrations