"""FastAPI application factory and Uvicorn entry point."""

from pathlib import Path

from fastapi import FastAPI

from engineering_assistant.api.routes import router


def create_app(
    database_path: Path | None = None,
    documents_root: Path | None = None,
) -> FastAPI:
    """Create the API app with configurable local paths for tests and runtime."""
    app = FastAPI(
        title="Engineering Knowledge Assistant",
        version="0.2.0",
        description="Class 2 document catalogue and keyword-search API",
    )
    app.state.database_path = database_path or Path("data/catalogue.sqlite3")
    app.state.documents_root = documents_root or Path("data/documents")
    app.include_router(router)
    return app


app = create_app()
