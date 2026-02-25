from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from uvicorn import run

from config import ApiSettings, get_api_settings
from core.api_v1.auth import auth_router, get_current_user
from core.api_v1.events import events_router
from core.api_v1.profile import profile_router
from core.database.sqlalchemy.models import User

api_settings: ApiSettings = get_api_settings()

app: FastAPI = FastAPI(debug=api_settings.DEBUG)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(events_router)


@app.get("/index/")
async def index_get(user: Annotated[User, Depends(get_current_user)]) -> JSONResponse:
    return JSONResponse(content={"message": "hello", "user_id": user.id})


if __name__ == "__main__":
    run(
        "main:app",
        host=api_settings.HOST,
        port=api_settings.PORT,
        reload=api_settings.RELOAD,
    )
