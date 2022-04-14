from fastapi import FastAPI, Depends

from app.routers import users, auth, tasks
from app import oauth2, models

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
def read_root(current_user: 'models.User' = Depends(oauth2.get_current_user)):
    return {"Hello": "World"}
