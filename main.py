from fastapi import FastAPI
from fastapi.responses import JSONResponse
from uvicorn import run

from config import ApiSettings, get_api_settings
from core.api_v1.auth import auth_router
from core.database.sqlalchemy.models import User

api_settings: ApiSettings = get_api_settings()
app: FastAPI = FastAPI(debug=api_settings.DEBUG)
app.include_router(auth_router)


@app.get("/index/")
async def index_get() -> JSONResponse:
    a = await User.get_all()
    print(len(a))

    return JSONResponse(content={"message": "hello"})


if __name__ == "__main__":
    run(
        "main:app",
        host=api_settings.HOST,
        port=api_settings.PORT,
        reload=api_settings.RELOAD,
    )
