import uvicorn

from app.core.config import settings


def main() -> None:
    """Entrypoint of the application."""
    uvicorn.run(
        "app.main:app",
        workers=1,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        reload_dirs=["app"]
    )


if __name__ == "__main__":
    main()
