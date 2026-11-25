# Engineering Knowledge Assistant — Class 2 starter

This is the Class 2 snapshot of the same project introduced in Class 1. Its package layout follows the course
architecture: **API routes**, **business services**, and **SQL repositories** are separate, with unit and integration
tests in their own folders.

## Starter policy: no homework solutions

The Class 1 catalogue functions are carried forward to
`src/engineering_assistant/services/catalog.py`, but all four functions still raise `NotImplementedError`. The code has
been moved from the Class 1 package name into the `services/` layer shown in the Class 2 architecture. Its original
acceptance-test cases are retained in `tests/unit/test_catalog.py`; only the import path changes to match the new
package name and service layer.

All Class 2 business functions are also TODOs. The public starter does not contain Class 1 or Class 2 homework
implementations. If you completed Class 1, carry your own implementation forward from your personal repository.

## Project structure

```text
engineering-knowledge-assistant/
├── src/
│   └── engineering_assistant/
│       ├── api/                 # FastAPI routes and response schemas
│       ├── services/            # business rules and processing workflow
│       │   ├── catalog.py       # Class 1 TODOs
│       │   ├── extraction.py    # Class 2 TODO
│       │   ├── chunking.py      # Class 2 TODO
│       │   └── ingestion.py     # Class 2 TODO
│       ├── repositories/        # SQL access
│       │   └── documents.py     # SQLite TODOs
│       └── main.py              # FastAPI application entry point
├── tests/
│   ├── unit/
│   └── integration/
├── data/                       # local documents and DB; gitignored
├── pyproject.toml
├── uv.lock
├── Makefile
└── README.md
```

## Requirements and setup

- Python >= 3.12
- Git, GNU Make and [uv](https://docs.astral.sh/uv/)
- Linux, macOS or Windows with Ubuntu on WSL2
- PyCharm or another IDE configured to use `.venv`

From this directory:

```bash
make install-test
```

`uv sync` installs runtime and development dependencies from `pyproject.toml`
and `uv.lock`; the test group is installed by `make install-test`.

## Layer responsibilities

- `api/`: HTTP routes, request validation and response schemas. Route handlers should stay thin and translate HTTP
  concerns only.
- `services/`: application/business rules, including catalogue operations, extraction, chunking and ingestion
  orchestration.
- `repositories/`: SQLite connections, schema and parameterized SQL queries.
- `main.py`: creates and configures the FastAPI application.
- `tests/unit/`: test individual functions and repository behavior in isolation.
- `tests/integration/`: test API contracts and multi-layer workflows.
- `data/`: local corpus and SQLite database. Do not commit its contents.

## Class 2 implementation tasks

1. Complete the four Class 1 catalogue functions in `services/catalog.py`.
2. Implement PDF, TXT and Markdown extraction in `services/extraction.py`.
3. Implement deterministic overlapping text chunks in `services/chunking.py`.
4. Implement the SQLite schema and document/chunk queries in
   `repositories/documents.py`.
5. Compose those layers in `services/ingestion.py`.
6. Complete the routes in `api/routes.py` and use Pydantic response models from
   `api/schemas.py`.
7. Add unit and integration tests for edge cases.

The complete requirements and acceptance criteria are in
[`../homework.md`](../homework.md).

## Run, test and inspect the API

```bash
make lint
make test
uv run uvicorn engineering_assistant.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI and the generated OpenAPI documentation. The health route is available
at `GET /health`.

## Development workflow

```bash
git checkout -b feat/document-api
make lint
make test  # acceptance tests fail until the TODOs are implemented
make format
make lint
make test
uv run pre-commit install
uv run pre-commit run --all-files
```

Do not weaken or delete acceptance tests to obtain a green build. Keep
`.venv/`, secrets, IDE files, local documents and SQLite databases out of Git.
