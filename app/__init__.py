from fastapi import FastAPI
from app.views import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Test Apifox API",
        description="用于测试 Apifox 同步的示例服务",
        version="1.2.0",
    )
    app.include_router(router)
    return app
