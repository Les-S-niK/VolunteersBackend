from fastapi import FastAPI
from uvicorn import run

from config import APP_VERSION, ApiSettings, get_api_settings
from core.api_v1.auth import auth_router
from core.api_v1.links import links_router
from core.api_v1.profile import profile_router
from core.logger.logger import setup_logger

api_settings: ApiSettings = get_api_settings()
setup_logger()

app: FastAPI = FastAPI(debug=api_settings.DEBUG, version=APP_VERSION)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(links_router)


if __name__ == "__main__":
    run(
        "main:app",
        host=api_settings.HOST,
        port=api_settings.PORT,
        reload=api_settings.RELOAD,
    )
