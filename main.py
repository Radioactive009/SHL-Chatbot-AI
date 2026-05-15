from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="SHL Assessment Recommendation API"
)

app.include_router(router)