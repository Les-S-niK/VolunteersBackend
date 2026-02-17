
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from uvicorn import run

from config import settings


app: FastAPI = FastAPI(debug=True)

@app.get("/index/")
async def index_get() -> JSONResponse:
    return {"message": "Hello from Index!"}


if __name__ == "__main__":
    run("main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
