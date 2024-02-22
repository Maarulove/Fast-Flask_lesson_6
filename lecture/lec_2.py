from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field

import databases
import sqlalchemy

"""
>>> pip install sqlalchemy
>>> pip install databases[aiosqlite]
>>> uvicorn lec_2:app --reload
"""


app = FastAPI(__name__)


database_url = "sqlite:///my_database.db"
database = databases.Database(database_url)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key = True)
    sqlalchemy.Column("name", sqlalchemy.String(32))
    sqlalchemy.Column("email", sqlalchemy.String(50))
)

engine = sqlalchemy.create_engine(database_url, connect_args = {"check_same_thread": False})
metadata.create_all(engine)


class User_in(BaseModel):
    name: str = Field(max_length=32)
    email: str = Field(max_length=50)

class User(BaseModel):
    id: int
    name: str = Field(max_length=32)
    email: str = Field(max_length=50)

@app.on_event("start-up")
async def start_up():
    await database.connect()

@app.on_event("shut-down")
async def dhut_down():
    await database.disconnect()



@app.post("/create-user", response_model=User)
async def create_user(user: User_in):
    query = users.insert().values(name=user.name, email = user.email)
    query = users.insert().values(**user.dict())
    last_id= await database.execute(query)
    return {**user.dict(), "id": last_id}


@app.get("/users", response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)

@app.get("users{user-id}", response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return database.fetch_all(query)

@app.put("/users{user-id}")
async def update_users(user_id:int, new_user: User_in):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}

@app.delete("users{user-id}")
async def delete_user(user_id:int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": "user deleted"}
