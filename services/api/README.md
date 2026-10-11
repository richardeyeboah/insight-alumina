# API scaffold
Only `/healthz` and generated FastAPI documentation exist. No database, authentication, webhook intake, booking storage, or AI is implemented. Do not deploy this service in phase 1.

Python 3.11+:
```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Run `pytest`, `ruff check .`, and `ruff format --check .` from this directory. Dependencies have compatibility ranges; produce a reviewed lockfile before phase 2 production deployment.
