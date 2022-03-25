from typing import Optional

from fastapi import FastAPI

from app.routers import users

app = FastAPI()

app.include_router(users.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
