from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Insight Alumina API", version="0.1.0")


class Health(BaseModel):
    status: str
    service: str


@app.get("/healthz", response_model=Health, tags=["operations"])
def health() -> Health:
    return Health(status="ok", service="api")
