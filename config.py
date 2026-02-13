from datetime import timedelta


APP_VERSION: str = "0.0.1"
APP_NAME: str = "VolunteersBackend"

TOKEN_TYPE: str = "Bearer"
TOKEN_EXPIRE_DAYS: int = 5
TOKEN_EXPIRE: timedelta = timedelta(days=TOKEN_EXPIRE_DAYS)
TOKEN_SECRET_KEY: str = (
    "3018c04e83f4c0d7a4d6cf14c39327db3d0b86056a26ca122d5810a3490b05e7"
)
TOKEN_ALGORITHM: str = "HS256"

API_HOST: str = "0.0.0.0"
API_PORT: int = 8080
