from typing import List, Literal
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
import databases 

"""
Разработать API для управления списком пользователей с использованием базы данных SQLite. 
Для этого создайте модель User со следующими полями:
- id: int (идентификатор пользователя, генерируется автоматически)
- username: str (имя пользователя)
- email: str (электронная почта пользователя)
- password: str (пароль пользователя)

API должно поддерживать следующие операции:
- Получение списка всех пользователей: GET /users/
- Получение информации о конкретном пользователе: GET /users/{user_id}/
- Создание нового пользователя: POST /users/
- Обновление информации о пользователе: PUT /users/{user_id}/
- Удаление пользователя: DELETE /users/{user_id}/

Для валидации данных используйте параметры Field модели User. 
Для работы с базой данных используйте SQLAlchemy и модуль databases.
"""
# from .lec import FastAPI, List, BaseModel, Field, databases, sqlalchemy 

app = FastAPI()
database_url = "sqlite:///my_database.db"
database = databases.Database(database_url)
metadata = sqlalchemy.MetaData()



class User(BaseModel):
    username: str = Field(max_lenght=32)
    email: str
    password: str 
    status: Literal["done", "not done"]

class User_id(User):
    id: int

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key = True),
    sqlalchemy.Column("username", sqlalchemy.String(30)),
    sqlalchemy.Column("email", sqlalchemy.String(50)),
    sqlalchemy.Column("password", sqlalchemy.String(25)),
    sqlalchemy.Column("Literal", sqlalchemy.String(25))
)

engine = sqlalchemy.create_engine(database_url, connect_args={'check_same_thread': False})
metadata.create_all(engine)
@app.on_event("startup")
async def start_up():
    await database.connect()

@app.on_event("shutdown")
async def shut_down():
    await database.disconnect()


@app.get("/users", response_model=List[User_id])
async def get_users():
    query = users.select()
    return await database.fetch_all(query)

@app.get("/users{user-id}", response_model=User_id)
async def get_user(user_id:int):
    query = users.select().where(users.c.id == user_id)
    return database.fetch_all(query)

@app.post("/users", response_model=User)
async def create_user(user: User):
    queary = users.insert().values(**user.dict())
    last_id = await database.execute(queary)
    return {**user.dict(), "id": last_id}

@app.put("/users/{user-id}")
async def update_user(user_id: int, new_user: User_id):
    queary = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(queary)
    return {**new_user.dict(), "id": user_id}

@app.delete("/users/{user-id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": "user deleted"}

# @app.delete("/users/{user_id}")
# async def delete_user(user_id: int):
#     query = users.delete().where(users.c.id == user_id)
#     await database.execute(query)
#     return {'message': 'User deleted'}