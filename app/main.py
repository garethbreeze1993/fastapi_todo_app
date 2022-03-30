from typing import Optional

from fastapi import FastAPI

from app.routers import users, auth

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
