from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from guard import SecurityMiddleware
from uvicorn import run

from config import (
    APP_VERSION,
    ApiSettings,
    StaticImagesSettings,
    get_api_settings,
    get_cors_origins,
    get_guard_setings,
    get_static_settings,
)
from core.api_v1.applicants import applicants_router
from core.api_v1.auth import auth_router
from core.api_v1.complaint import complaints_router
from core.api_v1.links import links_router
from core.api_v1.profile import profile_router
from core.api_v1.report import reports_router
from core.api_v1.shop import shop_router
from core.logger import setup_logger

api_settings: ApiSettings = get_api_settings()
setup_logger()

app: FastAPI = FastAPI(debug=api_settings.DEBUG, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityMiddleware, config=get_guard_setings())

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(links_router)
app.include_router(reports_router)
app.include_router(shop_router)
app.include_router(complaints_router)
app.include_router(applicants_router)

static_images_config: StaticImagesSettings = get_static_settings()
app.mount(
    path=static_images_config.API_URI,
    app=StaticFiles(directory=static_images_config.DIR_PATH),
    name="images",
)

if __name__ == "__main__":
    run(
        "main:app",
        host=api_settings.HOST,
        port=api_settings.PORT,
        reload=api_settings.RELOAD,
    )
