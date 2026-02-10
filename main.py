
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from uvicorn import run

from config import API_HOST, API_PORT


app: FastAPI = FastAPI(debug=True)

@app.get("/index/")
def index_get() -> JSONResponse:
    return {"message": "Hello from Index!"}


if __name__ == "__main__":
    run("main:app", host=API_HOST, port=API_PORT, reload=True)
