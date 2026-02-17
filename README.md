## Run APP

``` shell
poetry run uvicorn app.main:app --reload
poetry run python -m app.server
```

## Run Migration (alembic)
``` shell
poetry run alembic revision --autogenerate -m "Initial migration"   # Create migrations
poetry run alembic upgrade head    # Apply migrations
```

## Features

 - SQL ORM
 - Migration (alembic)
 - Mail send
 - File upload
 - Cache server (redis)
