from fastapi import APIRouter

service_router = login_router = APIRouter()


# Проверка работы приложения
@service_router.get("/ping")
async def ping():
    return {"Success": True}


# Проверка работы Sentry
@service_router.get("/sentry-debug")
async def trigger_error():
    return 1 / 0
