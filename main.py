from fastapi import FastAPI
from fastapi.responses import JSONResponse
from uvicorn import run

from config import API_HOST, API_PORT
from core.api_v1.auth import auth_router

app: FastAPI = FastAPI(debug=True)
app.include_router(auth_router)


@app.get("/index/")
def index_get() -> JSONResponse:
    return JSONResponse(content={"message": "hello"})


if __name__ == "__main__":
    run("main:app", host=API_HOST, port=API_PORT, reload=True)
